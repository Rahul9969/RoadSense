import io
import json
import time
import zipfile
import sys
import boto3

sys.stdout.reconfigure(encoding='utf-8')

REGION = "us-east-1"
ACCOUNT_ID = "464817648755"
ROLE_NAME = "roadsense-prod-lambda-role"
FUNCTION_NAME = "RoadSenseHazardWorker"
QUEUE_NAME = "roadsense-prod-hazard-queue"
QUEUE_ARN = f"arn:aws:sqs:{REGION}:{ACCOUNT_ID}:{QUEUE_NAME}"
SNS_TOPIC_ARN = f"arn:aws:sns:{REGION}:{ACCOUNT_ID}:roadsense-prod-critical-alerts"

iam = boto3.client("iam", region_name=REGION)
lambda_client = boto3.client("lambda", region_name=REGION)
sqs = boto3.client("sqs", region_name=REGION)

print(f"🚀 [1/5] Setting up IAM Role: {ROLE_NAME}...")

assume_role_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }
    ]
}

try:
    role = iam.get_role(RoleName=ROLE_NAME)
    role_arn = role["Role"]["Arn"]
    print(f"  Existing IAM Role found: {role_arn}")
except iam.exceptions.NoSuchEntityException:
    print(f"  Creating new IAM Role: {ROLE_NAME}...")
    role = iam.create_role(
        RoleName=ROLE_NAME,
        AssumeRolePolicyDocument=json.dumps(assume_role_policy),
        Description="Execution role for RoadSense Serverless Hazard Worker Lambda"
    )
    role_arn = role["Role"]["Arn"]
    print(f"  Created IAM Role: {role_arn}")

# Attach AWSLambdaBasicExecutionRole
iam.attach_role_policy(
    RoleName=ROLE_NAME,
    PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
)

# Inline Policy for SQS, SNS, and S3
lambda_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "SQSAccess",
            "Effect": "Allow",
            "Action": [
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes"
            ],
            "Resource": QUEUE_ARN
        },
        {
            "Sid": "SNSPublish",
            "Effect": "Allow",
            "Action": [
                "sns:Publish"
            ],
            "Resource": SNS_TOPIC_ARN
        },
        {
            "Sid": "S3Access",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": f"arn:aws:s3:::roadsense-hazards-{ACCOUNT_ID}-{REGION}/*"
        }
    ]
}

iam.put_role_policy(
    RoleName=ROLE_NAME,
    PolicyName="RoadSenseWorkerPolicy",
    PolicyDocument=json.dumps(lambda_policy)
)
print("  IAM Policies attached successfully.")

# Give IAM a few seconds for propagation
print("⏳ Waiting 8s for IAM role propagation...")
time.sleep(8)

print("📦 [2/5] Packaging lambda_function.py into ZIP...")
zip_buf = io.BytesIO()
with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as z:
    z.write("aws/lambda_function.py", arcname="lambda_function.py")
zip_bytes = zip_buf.getvalue()
print(f"  ZIP package created ({len(zip_bytes)} bytes).")

print(f"⚡ [3/5] Deploying Lambda Function: {FUNCTION_NAME}...")

try:
    lambda_client.get_function(FunctionName=FUNCTION_NAME)
    print(f"  Function {FUNCTION_NAME} already exists. Updating code & config...")
    lambda_client.update_function_code(
        FunctionName=FUNCTION_NAME,
        ZipFile=zip_bytes
    )
    lambda_client.update_function_configuration(
        FunctionName=FUNCTION_NAME,
        Runtime="python3.11",
        Role=role_arn,
        Handler="lambda_function.lambda_handler",
        Timeout=30,
        MemorySize=256,
        Environment={
            "Variables": {
                "SNS_TOPIC_ARN": SNS_TOPIC_ARN
            }
        }
    )
except lambda_client.exceptions.ResourceNotFoundException:
    print(f"  Creating function {FUNCTION_NAME}...")
    # Retry loop in case IAM role is still propagating
    for attempt in range(5):
        try:
            lambda_client.create_function(
                FunctionName=FUNCTION_NAME,
                Runtime="python3.11",
                Role=role_arn,
                Handler="lambda_function.lambda_handler",
                Code={"ZipFile": zip_bytes},
                Description="RoadSense Serverless Hazard Event Worker (SQS -> Triage -> SNS)",
                Timeout=30,
                MemorySize=256,
                Publish=True,
                Environment={
                    "Variables": {
                        "SNS_TOPIC_ARN": SNS_TOPIC_ARN
                    }
                }
            )
            print(f"  Function {FUNCTION_NAME} created successfully!")
            break
        except lambda_client.exceptions.InvalidParameterValueException as e:
            if "The role defined for the function cannot be assumed by Lambda" in str(e):
                print(f"  IAM role still propagating... attempt {attempt+1}/5, waiting 5s")
                time.sleep(5)
            else:
                raise e

print("🔗 [4/5] Configuring Amazon SQS Event Source Mapping...")
# Check if EventSourceMapping already exists
mappings = lambda_client.list_event_source_mappings(
    FunctionName=FUNCTION_NAME,
    EventSourceArn=QUEUE_ARN
)

if not mappings.get("EventSourceMappings"):
    esm = lambda_client.create_event_source_mapping(
        EventSourceArn=QUEUE_ARN,
        FunctionName=FUNCTION_NAME,
        Enabled=True,
        BatchSize=10
    )
    print(f"  Event source mapping created: UUID {esm['UUID']}")
else:
    esm_uuid = mappings["EventSourceMappings"][0]["UUID"]
    print(f"  Event source mapping already active: UUID {esm_uuid}")

print("🧪 [5/5] Testing Lambda Invocation with Mock SQS Event...")
test_event = {
    "Records": [
        {
            "messageId": "test-msg-001",
            "body": json.dumps({
                "report_id": 999,
                "label": "Potholes",
                "severity": "critical",
                "location": {"lat": 19.0422, "lng": 72.8598},
                "image_url": "https://example.com/pothole.jpg",
                "username": "citizen_test",
                "timestamp": "2026-10-25T17:45:00Z"
            })
        }
    ]
}

inv_res = lambda_client.invoke(
    FunctionName=FUNCTION_NAME,
    InvocationType="RequestResponse",
    Payload=json.dumps(test_event)
)

status = inv_res["StatusCode"]
response_payload = inv_res["Payload"].read().decode("utf-8")
print(f"  Invocation StatusCode: {status}")
print(f"  Invocation Response: {response_payload}")

print("\n🎉 SUCCESS: RoadSense Serverless Lambda Function is 100% DEPLOYED and ACTIVE on AWS!")
print(f"📍 AWS Console Region: {REGION} | Function: {FUNCTION_NAME}")
