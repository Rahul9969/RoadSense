import os
import json
import logging
import uuid
from datetime import datetime
from io import BytesIO

# Configure logger
logger = logging.getLogger("roadsense.aws")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Lazy-loaded AWS clients
_s3_client = None
_sns_client = None
_sqs_client = None
_ssm_client = None

def get_aws_region():
    """Retrieve AWS region from environment or default to us-east-1."""
    return os.getenv("AWS_REGION", "us-east-1")

def get_s3_client():
    global _s3_client
    if _s3_client is None:
        try:
            import boto3
            _s3_client = boto3.client("s3", region_name=get_aws_region())
        except Exception as e:
            logger.warning(f"Could not initialize boto3 S3 client: {e}")
    return _s3_client

def get_sns_client():
    global _sns_client
    if _sns_client is None:
        try:
            import boto3
            _sns_client = boto3.client("sns", region_name=get_aws_region())
        except Exception as e:
            logger.warning(f"Could not initialize boto3 SNS client: {e}")
    return _sns_client

def get_sqs_client():
    global _sqs_client
    if _sqs_client is None:
        try:
            import boto3
            _sqs_client = boto3.client("sqs", region_name=get_aws_region())
        except Exception as e:
            logger.warning(f"Could not initialize boto3 SQS client: {e}")
    return _sqs_client

def get_ssm_client():
    global _ssm_client
    if _ssm_client is None:
        try:
            import boto3
            _ssm_client = boto3.client("ssm", region_name=get_aws_region())
        except Exception as e:
            logger.warning(f"Could not initialize boto3 SSM client: {e}")
    return _ssm_client


def load_config_from_ssm(app):
    """
    Load database and security configuration from AWS SSM Parameter Store.
    Only executes if RUNNING_IN_AWS or FLASK_ENV=production is set.
    Credentials and secrets are NEVER hardcoded in source code!
    """
    env = os.getenv("FLASK_ENV", "development").lower()
    in_aws = os.getenv("RUNNING_IN_AWS", "false").lower() == "true" or env == "production"

    if not in_aws:
        logger.info("Running locally: skipping AWS SSM Parameter Store retrieval.")
        return

    ssm = get_ssm_client()
    if not ssm:
        logger.warning("SSM client unavailable; using local environment variables.")
        return

    param_names = [
        "/roadsense/db_host",
        "/roadsense/db_name",
        "/roadsense/db_user",
        "/roadsense/db_password",
        "/roadsense/secret_key",
        "/roadsense/s3_bucket",
        "/roadsense/sns_topic_arn",
        "/roadsense/sqs_queue_url"
    ]

    try:
        logger.info("Fetching configuration from AWS SSM Parameter Store...")
        response = ssm.get_parameters(Names=param_names, WithDecryption=True)
        params = {}
        for p in response.get("Parameters", []):
            key = p["Name"].split("/")[-1]
            params[key] = p["Value"]

        if "db_host" in params and "db_user" in params and "db_password" in params:
            db_name = params.get("db_name", "roadsensedb")
            db_uri = f"postgresql://{params['db_user']}:{params['db_password']}@{params['db_host']}:5432/{db_name}"
            app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
            logger.info(f"Loaded RDS Database URI for host: {params['db_host']}")

        if "secret_key" in params:
            app.config["SECRET_KEY"] = params["secret_key"]

        if "s3_bucket" in params:
            os.environ["S3_BUCKET"] = params["s3_bucket"]

        if "sns_topic_arn" in params:
            os.environ["SNS_TOPIC_ARN"] = params["sns_topic_arn"]

        if "sqs_queue_url" in params:
            os.environ["SQS_QUEUE_URL"] = params["sqs_queue_url"]

        logger.info("Successfully loaded AWS configuration parameters.")
    except Exception as e:
        logger.error(f"Error loading parameters from AWS SSM: {e}")


def upload_image_to_s3(image_bytes, filename_prefix="hazards", content_type="image/jpeg"):
    """
    Upload image bytes to Amazon S3 bucket.
    Returns the public S3 URL.
    Falls back to saving locally in uploaded_images/ if S3 is not configured or fails.
    """
    bucket_name = os.getenv("S3_BUCKET")
    region = get_aws_region()
    unique_filename = f"{filename_prefix}/{uuid.uuid4().hex}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"

    s3 = get_s3_client()
    if s3 and bucket_name:
        try:
            s3.put_object(
                Bucket=bucket_name,
                Key=unique_filename,
                Body=image_bytes,
                ContentType=content_type
            )
            s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{unique_filename}"
            logger.info(f"Uploaded hazard image to S3: {s3_url}")
            return s3_url
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}. Falling back to local disk storage.")

    # Local fallback
    upload_dir = os.path.join(os.path.dirname(__file__), "uploaded_images")
    os.makedirs(upload_dir, exist_ok=True)
    local_path = os.path.join(upload_dir, os.path.basename(unique_filename))
    with open(local_path, "wb") as f:
        f.write(image_bytes)
    logger.info(f"Saved hazard image locally to: {local_path}")
    return f"/uploaded_images/{os.path.basename(unique_filename)}"


def publish_critical_alert(report_id, label, severity, location, reporter, image_url=None):
    """
    Publishes an alert to the Amazon SNS topic for high or critical road hazards.
    """
    topic_arn = os.getenv("SNS_TOPIC_ARN")
    if not topic_arn:
        logger.info(f"[SNS Simulation] No SNS_TOPIC_ARN configured. Critical alert logged for report #{report_id} ({label})")
        return False

    sns = get_sns_client()
    if not sns:
        return False

    try:
        lat = location.get("lat", 0.0)
        lng = location.get("lng", 0.0)
        message = (
            f"⚠️ ROADSENSE CRITICAL ROAD HAZARD ALERT ⚠️\n"
            f"-----------------------------------------\n"
            f"Report ID: #{report_id}\n"
            f"Category:  {label}\n"
            f"Severity:  {severity.upper()}\n"
            f"Reporter:  {reporter}\n"
            f"Location:  Lat {lat}, Lng {lng}\n"
            f"Photo:     {image_url or 'N/A'}\n"
            f"Time:      {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"-----------------------------------------\n"
            f"Municipal highway crew has been notified for immediate inspection."
        )

        response = sns.publish(
            TopicArn=topic_arn,
            Subject=f"[RoadSense Alert] {severity.upper()} {label} Reported",
            Message=message
        )
        logger.info(f"Published SNS alert for report #{report_id}. MessageId: {response.get('MessageId')}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish SNS alert: {e}")
        return False


def enqueue_hazard_event(event_payload):
    """
    Enqueues hazard report into Amazon SQS for asynchronous background processing & deduplication.
    """
    queue_url = os.getenv("SQS_QUEUE_URL")
    if not queue_url:
        logger.info(f"[SQS Simulation] No SQS_QUEUE_URL configured. Hazard event enqueued in memory.")
        return False

    sqs = get_sqs_client()
    if not sqs:
        return False

    try:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(event_payload),
            MessageAttributes={
                "EventType": {
                    "DataType": "String",
                    "StringValue": "RoadHazardCreated"
                }
            }
        )
        logger.info(f"Enqueued hazard event to SQS. MessageId: {response.get('MessageId')}")
        return True
    except Exception as e:
        logger.error(f"Failed to enqueue to SQS: {e}")
        return False
