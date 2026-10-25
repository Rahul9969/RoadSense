"""
RoadSense AWS Lambda & SQS Trigger Automator
Deploys and wires the SQS event source mapping to the Lambda function.
"""

import boto3
import json
import os
import zipfile
import io
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("roadsense.setup_lambda")

REGION = os.getenv("AWS_REGION", "us-east-1")
QUEUE_NAME = "roadsense-prod-hazard-queue"
LAMBDA_FUNCTION_NAME = "RoadSenseHazardWorker"
ACCOUNT_ID = "464817648755"
ROLE_ARN = f"arn:aws:iam::{ACCOUNT_ID}:role/roadsense-prod-ec2-role"


def create_lambda_deployment_package():
    """Builds an in-memory zip archive containing the Lambda worker script."""
    worker_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "aws_lambda_worker.py")
    if not os.path.exists(worker_path):
        raise FileNotFoundError(f"Worker code not found at {worker_path}")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(worker_path, arcname="lambda_function.py")
    zip_buffer.seek(0)
    return zip_buffer.read()


def setup_queue_and_lambda():
    sqs = boto3.client("sqs", region_name=REGION)
    lambda_client = boto3.client("lambda", region_name=REGION)

    logger.info("1. Resolving SQS Queue URL & ARN...")
    try:
        queue_url_response = sqs.get_queue_url(QueueName=QUEUE_NAME)
        queue_url = queue_url_response["QueueUrl"]
        attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["All"])["Attributes"]
        queue_arn = attrs["QueueArn"]
        logger.info(f"   Queue URL: {queue_url}")
        logger.info(f"   Queue ARN: {queue_arn}")
        logger.info(f"   Approximate Messages in Queue: {attrs.get('ApproximateNumberOfMessages', '0')}")
    except Exception as e:
        logger.error(f"Error fetching queue details: {e}")
        return

    logger.info("2. Preparing AWS Lambda deployment zip package...")
    zip_bytes = create_lambda_deployment_package()
    logger.info(f"   Package size: {len(zip_bytes)} bytes")

    logger.info(f"3. Deploying or updating Lambda function '{LAMBDA_FUNCTION_NAME}'...")
    function_arn = None
    try:
        response = lambda_client.create_function(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Runtime="python3.11",
            Role=ROLE_ARN,
            Handler="lambda_function.lambda_handler",
            Code={"ZipFile": zip_bytes},
            Description="Processes civic road hazard reports asynchronously from Amazon SQS with departmental routing and SLA targets.",
            Timeout=30,
            MemorySize=128,
            Publish=True
        )
        function_arn = response["FunctionArn"]
        logger.info(f"   Successfully created Lambda function: {function_arn}")
    except lambda_client.exceptions.ResourceConflictException:
        logger.info("   Function already exists; updating function code...")
        response = lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            ZipFile=zip_bytes,
            Publish=True
        )
        function_arn = response["FunctionArn"]
        logger.info(f"   Successfully updated Lambda code for: {function_arn}")
    except Exception as e:
        logger.warning(f"   Could not create/update Lambda via API (check IAM permissions): {e}")

    if function_arn:
        logger.info("4. Setting up Event Source Mapping (SQS -> Lambda Trigger)...")
        try:
            mappings = lambda_client.list_event_source_mappings(
                EventSourceArn=queue_arn,
                FunctionName=LAMBDA_FUNCTION_NAME
            )
            if mappings.get("EventSourceMappings"):
                logger.info("   Event source mapping is already configured and ACTIVE.")
            else:
                mapping = lambda_client.create_event_source_mapping(
                    EventSourceArn=queue_arn,
                    FunctionName=LAMBDA_FUNCTION_NAME,
                    Enabled=True,
                    BatchSize=10,
                    FunctionResponseTypes=["ReportBatchItemFailures"]
                )
                logger.info(f"   Created SQS event source mapping UUID: {mapping.get('UUID')}")
        except Exception as e:
            logger.warning(f"   Could not configure event source mapping: {e}")

    logger.info("AWS Lambda & SQS verification complete.")


if __name__ == "__main__":
    setup_queue_and_lambda()
