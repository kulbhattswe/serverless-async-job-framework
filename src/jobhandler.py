import json
import boto3
import uuid
import os
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key
import logging
import traceback

#logging.basicConfig(level=logging.INFO)  

logger = logging.getLogger()
logger.setLevel(logging.INFO)
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST'
        },
        'body': json.dumps(body)
    }
def generate_presigned_url(key):
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': os.environ['S3_BUCKET_NAME'], 'Key': key},
        ExpiresIn=3600  # 1 hour
    )
def lambda_handler(event, context):
    try:
        logger.info(f"Incoming event: {json.dumps(event)}")
        
        # API Gateway v2.0 uses different event structure
        http_method = event['requestContext']['http']['method']
        route_key = event['routeKey']
        
        if route_key == 'POST /job':
            return handle_post(event, context)
        elif route_key == 'GET /job':
            return handle_get(event, context)
        elif route_key == 'GET /jobs':
            return handle_get_all_jobs(event, context)
        elif route_key == 'GET /ping':
            return handle_ping(event, context)
        else:
            return response(405, {'error': 'Method not allowed'})
                                      
    except Exception as e:
        logger.error(f"Error: {str(e)}",  exc_info=True)
        return response(500, {'error': 'Internal server error'})
                    
def handle_post(event, context):
    try:
        # Validate request body 
        # Extract user_id from JWT claims (v2.0 format)
        jwt_claims = event['requestContext']['authorizer']['jwt']['claims']
        user_id = jwt_claims['sub']
        
        # Parse request body
        body = json.loads(event['body'])
        name = body.get('name')
        action = body.get('action')
        context1 = body.get('context1')
        context2 = body.get('context2')
        
        # Generate job_id
        job_id = str(uuid.uuid4())
        
        # Create job item for SQS
        job_item = {
            'job_id': job_id,
            'name': name,
            'action': action,
            'context1': context1,
            'context2': context2,
            'user_id': user_id
        }
        
        logger.info(f"Sending to queue job_item={job_item}")
            
        # Send to SQS
        sqs.send_message(
            QueueUrl=os.environ['JOBS_QUEUE_URL'],
            MessageBody=json.dumps(job_item)
        )
        
        # Create DynamoDB entry
        table = dynamodb.Table(os.environ['JOBS_TABLE_NAME'])
        table.put_item(
            Item={
                'job_id': job_id,
                'user_id': user_id,
                'status': 'PENDING',
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'action': action,
                'name': name
            }
        )
        
        return response(201, {'job_id': job_id, 'status': 'PENDING'})
    except Exception as e:
        logger.error(f"Error processing job: {str(e)}", exc_info=True)
        return response(500, {'error': 'Failed to submit job'}) 
            
def handle_get(event, context):
    try:
        # Get job_id from query parameters
        job_id = event['queryStringParameters'].get('job_id') if event.get('queryStringParameters') else None
        
        if not job_id:
            return response(400, {'error': 'job_id parameter is required'})
                          
        # Get job from DynamoDB
        table = dynamodb.Table(os.environ['JOBS_TABLE_NAME'])
        db_response = table.get_item(Key={'job_id': job_id})
        
        if 'Item' not in db_response:
            return response(404, {'error': 'Job not found'})
            
        item = db_response['Item']
        result = {
            'job_id': item['job_id'],
            'status': item['status'],
            'createdAt': item['createdAt'],
            'action': item['action']
        }
        logger.info(f"Retrieved item: {item}")
        if 'name' in item:
            result['name'] = item['name']
        
        if 'S3FileKey' in item and item['S3FileKey']:
            # Generate presigned URL for S3 file if it exists 
            presigned_url = generate_presigned_url(item['S3FileKey'])
            if presigned_url:
                result['presigned_url'] = presigned_url
                result['S3FileKey'] = item['S3FileKey']
            elif item['status'] != 'PENDING':
                logger.warning(f"No S3FileKey found for job_id: {job_id}")
        
        return response(200, result)
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        logger.error(f"Error retrieving job: {str(e)}")
        raise e
        
def handle_get_all_jobs(event, context):
    # Extract user_id from JWT claims (v2.0 format)
    jwt_claims = event['requestContext']['authorizer']['jwt']['claims']
    user_id = jwt_claims['sub']
    
    # Get today's date range
    today = datetime.now(timezone.utc).date()
    start_of_day = datetime.combine(today, datetime.min.time(), timezone.utc).isoformat()
    end_of_day = datetime.combine(today, datetime.max.time(), timezone.utc).isoformat()
    
    # Query DynamoDB using GSI
    table = dynamodb.Table(os.environ['JOBS_TABLE_NAME'])
    
    try:
        db_response = table.query(
            IndexName='user-date-index',
            KeyConditionExpression=Key('user_id').eq(user_id) & Key('createdAt').between(start_of_day, end_of_day),
            ScanIndexForward=False  # Sort by createdAt descending (newest first)
        )
        
        jobs = []
        for item in db_response['Items']:
            job_data = {
                'job_id': item['job_id'],
                'status': item['status'],
                'createdAt': item['createdAt'],
                'action': item['action']
            }
            
            if 'name' in item:
                job_data['name'] = item['name']
            
            if 'S3FileKey' in item:
                job_data['S3FileKey'] = item['S3FileKey']
            
            jobs.append(job_data)
        
        return response(200, {
                'jobs': jobs,
                'count': len(jobs),
                'date': today.isoformat()
        })                                    
        
    except Exception as e:
        logger.error(f"Error querying jobs: {str(e)}", exc_info=True)
        return response(500, {'error': 'Failed to retrieve jobs'})

def handle_ping(event, context):
    return response(200, {'message': 'ping ok'})