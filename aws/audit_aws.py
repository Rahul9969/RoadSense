import boto3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

region = 'us-east-1'
account_id = '464817648755'

print("=============================================")
print("   ROADSENSE AWS LIVE CLOUD AUDIT & VERIFY   ")
print("=============================================")

# 1. S3
s3 = boto3.client('s3', region_name=region)
bucket_name = f'roadsense-hazards-{account_id}-{region}'
try:
    s3.head_bucket(Bucket=bucket_name)
    print(f"✅ [S3] Bucket exists & reachable: {bucket_name}")
except Exception as e:
    print(f"❌ [S3] Bucket error: {e}")

# 2. SQS
sqs = boto3.client('sqs', region_name=region)
for q_name in ['roadsense-prod-hazard-queue', 'roadsense-prod-hazard-dlq']:
    try:
        url = sqs.get_queue_url(QueueName=q_name)['QueueUrl']
        attrs = sqs.get_queue_attributes(QueueUrl=url, AttributeNames=['All'])['Attributes']
        has_policy = bool(attrs.get('Policy'))
        has_redrive = bool(attrs.get('RedrivePolicy'))
        print(f"✅ [SQS] Queue: {q_name} | Policy: {has_policy} | RedrivePolicy: {has_redrive}")
        if has_redrive:
            print(f"   RedriveConfig: {attrs.get('RedrivePolicy')}")
    except Exception as e:
        print(f"❌ [SQS] Error on {q_name}: {e}")

# 3. SNS
sns = boto3.client('sns', region_name=region)
topic_arn = f"arn:aws:sns:{region}:{account_id}:roadsense-prod-critical-alerts"
try:
    t_attrs = sns.get_topic_attributes(TopicArn=topic_arn)
    subs = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
    sub_count = len(subs.get('Subscriptions', []))
    print(f"✅ [SNS] Topic exists: {topic_arn} (Subscriptions: {sub_count})")
    for s in subs.get('Subscriptions', []):
        print(f"   - Protocol: {s['Protocol']} | Endpoint: {s['Endpoint']}")
except Exception as e:
    print(f"❌ [SNS] Topic error: {e}")

# 4. Lambda
lam = boto3.client('lambda', region_name=region)
for fn in ['RoadSenseHazardWorker', 'roadsense-prod-hazard-worker']:
    try:
        f_info = lam.get_function(FunctionName=fn)
        role = f_info['Configuration']['Role']
        state = f_info['Configuration'].get('State', 'Active')
        print(f"✅ [LAMBDA] {fn} | State: {state} | Role: {role.split('/')[-1]}")
        mappings = lam.list_event_source_mappings(FunctionName=fn)
        for m in mappings.get('EventSourceMappings', []):
            print(f"   -> SQS EventSource: {m['EventSourceArn'].split(':')[-1]} | State: {m['State']} | UUID: {m['UUID']}")
    except Exception as e:
        print(f"❌ [LAMBDA] Error on {fn}: {e}")

# 5. SSM Parameter Store
ssm = boto3.client('ssm', region_name=region)
try:
    params = ssm.describe_parameters(ParameterFilters=[{'Key': 'Name', 'Option': 'BeginsWith', 'Values': ['/roadsense']}])
    p_list = params.get('Parameters', [])
    print(f"✅ [SSM] Managed Parameters: {len(p_list)} registered")
    for p in p_list:
        print(f"   - {p['Name']} ({p['Type']})")
except Exception as e:
    print(f"❌ [SSM] Error: {e}")

# 6. CloudWatch Alarms & Dashboards
cw = boto3.client('cloudwatch', region_name=region)
try:
    alarms = cw.describe_alarms(AlarmNames=['roadsense-prod-high-cpu-alarm'])
    alarm_list = alarms.get('MetricAlarms', [])
    print(f"✅ [CloudWatch Alarm] roadsense-prod-high-cpu-alarm: {len(alarm_list)} found")
    for a in alarm_list:
        print(f"   - State: {a['StateValue']} | Threshold: {a['MetricName']} >= {a['Threshold']}%")
except Exception as e:
    print(f"❌ [CloudWatch Alarm] Error: {e}")

try:
    dash = cw.get_dashboard(DashboardName='RoadSense-Production-Dashboard')
    print("✅ [CloudWatch Dashboard] RoadSense-Production-Dashboard: Active & Configured")
except Exception as e:
    print(f"⚠️ [CloudWatch Dashboard] {e}")
