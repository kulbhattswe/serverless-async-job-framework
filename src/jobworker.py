import json
import boto3
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    try:
        logger.info(f"Incoming event: {json.dumps(event)}")
        for record in event['Records']:
            # Parse SQS message
            job_item = json.loads(record['body'])
            
            logger.info(f"Processing job item: {job_item}")
            job_id = job_item['job_id']
            user_id = job_item['user_id']
            context1 = job_item['context1']
            context2 = job_item['context2']
            
            now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
            now_str = now_utc.strftime("%Y-%m-%d %H:%M:%S %Z%z")
            # Concatenate context1 and context2
            content = (
                        f"async job framework processed job {job_id}\n"
                        f"Job processed at {now_str}\n"
                        f"{context1}\n"
                        f"{context2}\n"
            )
            
            # Create S3 key
            current_date = datetime.utcnow().strftime('%Y-%m-%d')
            s3_key = f"{user_id}/{current_date}/{job_id}.txt"
            
            # Save to S3
            s3.put_object(
                Bucket=os.environ['S3_BUCKET_NAME'],
                Key=s3_key,
                Body=content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            # Update DynamoDB entry
            table = dynamodb.Table(os.environ['JOBS_TABLE_NAME'])
            table.update_item(
                Key={'job_id': job_id},
                UpdateExpression='SET #status = :status, S3FileKey = :s3key',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'COMPLETE',
                    ':s3key': s3_key
                }
            )
            
            print(f"Successfully processed job {job_id}")
            
    except Exception as e:
        print(f"Error processing job: {str(e)}")
        raise e