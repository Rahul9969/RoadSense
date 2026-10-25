import json
import logging
import os
import urllib.parse
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Regional AWS config
REGION = os.environ.get("AWS_REGION", "us-east-1")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:464817648755:roadsense-prod-critical-alerts")

def calculate_triage_score(hazard_type, severity):
    """
    Municipal dispatch priority algorithm (0 - 100):
    Potholes and Waterlogging in critical traffic zones receive highest dispatch priority.
    """
    base_scores = {
        "critical": 90,
        "high": 75,
        "medium": 50,
        "low": 25
    }
    type_weight = {
        "Potholes": 10,
        "Waterlogging": 10,
        "Damaged Road": 5,
        "Broken Streetlight": 0,
        "Garbage": -5
    }
    score = base_scores.get(severity.lower(), 50) + type_weight.get(hazard_type, 0)
    return min(100, max(10, score))


def lambda_handler(event, context):
    """
    RoadSense Serverless Hazard Event Worker.
    Triggered by Amazon SQS hazard queue (roadsense-prod-hazard-queue).
    Processes municipal hazard telemetry, evaluates SLA compliance, and publishes SNS notifications.
    """
    logger.info(f"RoadSenseHazardWorker received {len(event.get('Records', []))} event record(s).")
    processed_count = 0

    for record in event.get("Records", []):
        try:
            # 1. Parse SQS Message Body
            body_str = record.get("body", "{}")
            message = json.loads(body_str) if isinstance(body_str, str) else body_str
            
            report_id = message.get("report_id", "N/A")
            label = message.get("label", "Road Hazard")
            severity = message.get("severity", "medium").lower()
            location = message.get("location", {})
            lat = location.get("lat", 27.6194)
            lng = location.get("lng", 85.5388)
            image_url = message.get("image_url", "")
            reporter = message.get("username", "citizen")
            timestamp = message.get("timestamp", datetime.utcnow().isoformat())

            # 2. Municipal Triage Score Calculation
            triage_score = calculate_triage_score(label, severity)
            sla_hours = 24 if severity in ["critical", "high"] else 48

            logger.info(
                f"[TRIAGE] Report #{report_id} | Type: {label} | Severity: {severity.upper()} | "
                f"Score: {triage_score}/100 | SLA Target: {sla_hours}h | Coordinates: ({lat}, {lng})"
            )

            # 3. Critical Hazard Auto-Escalation via Amazon SNS
            if severity in ["critical", "high"]:
                import boto3
                sns = boto3.client("sns", region_name=REGION)
                alert_subject = f"[URGENT ROAD HAZARD] Critical {label} Detected - ID #{report_id}"
                alert_body = (
                    f"ROADSENSE MUNICIPAL RAPID RESPONSE ALERT\n"
                    f"=========================================\n"
                    f"Report ID: {report_id}\n"
                    f"Hazard Type: {label}\n"
                    f"Severity: {severity.upper()}\n"
                    f"Priority Score: {triage_score}/100\n"
                    f"GPS Location: https://maps.google.com/?q={lat},{lng}\n"
                    f"Reported By: {reporter}\n"
                    f"Timestamp: {timestamp}\n"
                    f"Evidence Photo: {image_url}\n"
                    f"Required Action: Municipal crew dispatch within {sla_hours} hours.\n"
                )
                try:
                    sns.publish(
                        TopicArn=SNS_TOPIC_ARN,
                        Subject=alert_subject[:100],
                        Message=alert_body
                    )
                    logger.info(f"[SNS PUBLISHED] Alert dispatched to {SNS_TOPIC_ARN}")
                except Exception as sns_err:
                    logger.warning(f"SNS publish failed (non-blocking): {sns_err}")

            processed_count += 1

        except Exception as e:
            logger.error(f"Error processing SQS record {record.get('messageId')}: {e}", exc_info=True)
            # Re-raise to trigger SQS retry / dead-letter queue if critical
            raise e

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Hazard batch processed successfully",
            "processed_records": processed_count,
            "engine": "RoadSense Serverless Worker v2.0"
        })
    }
