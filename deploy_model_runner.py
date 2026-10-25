import boto3
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Upload model_runner.py to S3
s3 = boto3.client('s3', region_name='us-east-1')
bucket = 'roadsense-hazards-464817648755-us-east-1'
s3.upload_file('lib/backend/utils/model_runner.py', bucket, 'backend-build/model_runner.py')
print('Uploaded updated model_runner.py to S3!')

# 2. Command EC2 via SSM to download and restart service
ssm = boto3.client('ssm', region_name='us-east-1')
deploy_script = """
/var/www/roadsense/lib/backend/venv/bin/python3 -c "import boto3; s3 = boto3.client('s3', region_name='us-east-1'); s3.download_file('roadsense-hazards-464817648755-us-east-1', 'backend-build/model_runner.py', '/var/www/roadsense/lib/backend/utils/model_runner.py')"
chown -R ubuntu:ubuntu /var/www/roadsense
chmod 644 /var/www/roadsense/lib/backend/utils/model_runner.py
systemctl restart roadsense.service
sleep 2
systemctl status roadsense.service --no-pager
grep -n "timeout=25" /var/www/roadsense/lib/backend/utils/model_runner.py
"""

res = ssm.send_command(
    InstanceIds=['i-086b755fd5a8050e9'],
    DocumentName='AWS-RunShellScript',
    Parameters={'commands': [deploy_script]}
)

cmd_id = res['Command']['CommandId']
print('Sent deployment command to EC2. Waiting...')
time.sleep(5)
inv = ssm.get_command_invocation(CommandId=cmd_id, InstanceId='i-086b755fd5a8050e9')
print('Status:', inv['Status'])
print('Output:\n', inv.get('StandardOutputContent', ''))
print('Error:\n', inv.get('StandardErrorContent', ''))
