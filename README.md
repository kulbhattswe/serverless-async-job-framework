# AWS Serverless Job Processing Stack

A complete serverless job processing system built with AWS CloudFormation, featuring API Gateway, Lambda functions, SQS, DynamoDB, and S3.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway   │────│  JWT Authorizer  │────│  JobHandler λ   │
│   (REST API)    │    │   (Cognito)      │    │   (POST/GET)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   S3 Bucket     │────│ JobWorker λ      │────│   SQS Queue     │
│  (Job Files)    │    │  (Processing)    │    │  (Job Items)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                                │                         │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   DynamoDB      │    │  Dead Letter    │
                       │  (Job Status)   │    │     Queue       │
                       └─────────────────┘    └─────────────────┘
```

## Features

- **Serverless Architecture**: No servers to manage, pay only for usage
- **JWT Authentication**: Secure API access using existing Cognito User Pool
- **Asynchronous Processing**: Jobs processed via SQS for scalability
- **Job Status Tracking**: Real-time job status in DynamoDB
- **File Storage**: Processed results stored in S3 with lifecycle management
- **Error Handling**: Dead letter queue for failed job processing
- **CORS Support**: Ready for web frontend integration
- **Monitoring**: CloudWatch logs for all components

## API Endpoints

### POST /job
Create a new job for processing.

**Request Body:**
```json
{
  "name": "job-name",
  "action": "process-data",
  "context1": "first part of data",
  "context2": "second part of data"
}
```

**Response:**
```json
{
  "job_id": "uuid-generated-id",
  "status": "PENDING"
}
```

### GET /job?job_id={id}
Check the status of a job.

**Response:**
```json
{
  "job_id": "uuid-generated-id",
  "status": "COMPLETE",
  "createdAt": "2025-07-14T12:00:00Z",
  "action": "process-data",
  "S3FileKey": "user-id/2025-07-14/job-id.txt"
}
```
### GET /jobs
Get the status of all jobs.

**Response:**
```json
[
    {
    "job_id": "uuid-generated-id",
    "status": "COMPLETE",
    "createdAt": "2025-07-14T12:00:00Z",
    "action": "process-data",
    "S3FileKey": "user-id/2025-07-14/job-id.txt"
    }
 ]
```
## Prerequisites

- AWS CLI configured with appropriate permissions
- Existing Cognito User Pool with:
  - User Pool ARN
  - Issuer URL
  - App Client ID

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/aws-serverless-job-processing.git
   cd aws-serverless-job-processing
   ```
  Create a .env file
  ```code
# Load environment variables
Project=async-job-processing-framework
COGNITO_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxxx
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxx
USER_POOL_ARN=arn:aws:cognito-idp:us-east-1:xxxxxxxxxxxx:userpool/us-east-1_xxxxxxxxx
ISSUER_URL=https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxxxxxxx
API_ENV=dev
STACK_NAME=job-processing-stack
TEMPLATE_FILE=template.yaml
PARAMETERS_FILE=updated-parameters.json
REGION=${COGNITO_REGION}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
CODE_BUCKET_NAME=$(echo jobsdemocodebucket-${ACCOUNT_ID}-${REGION})
```

2. **Deploy the stack:**
   ```bash
   make deploy
   ```

3. **Monitor deployment:**
   ```bash
   make status
   ```
4. **Update the stack:**
   ```bash
   make update
   ```
5. **Delete Stack:**
   ```bash
   make delete
   ```
6. **View Logs:**
   ```bash
   make logs
   ```  
7. **View Outputs:**
   ```bash
   make outputs
   ```  
8. **Validate Stack**
   
   _Run the tests in UnitTest_
     
9. **View  Events**
   ```bash
   make events
   ``` 
## Parameters

Create a `parameters.json` file:

```json
[
  {
    "ParameterKey": "Project",
    "ParameterValue": "MyJobProcessing"
  },
  {
    "ParameterKey": "UserPoolArn",
    "ParameterValue": "arn:aws:cognito-idp:region:account:userpool/pool-id"
  },
  {
    "ParameterKey": "IssuerUrl",
    "ParameterValue": "https://cognito-idp.region.amazonaws.com/pool-id"
  },
  {
    "ParameterKey": "CognitoClientId",
    "ParameterValue": "your-client-id"
  },
  {
    "ParameterKey": "ApiEnv",
    "ParameterValue": "dev"
  }
]
```

## Cost Estimation

This stack is designed to be cost-effective, especially for demo/development usage:

**Free Tier Eligible:**
- **Lambda**: 1M requests/month + 400K GB-seconds
- **API Gateway**: 1M requests/month (first 12 months)
- **DynamoDB**: 25GB storage + 25 RCU/WCU
- **S3**: 5GB storage + 20K GET + 2K PUT requests (first 12 months)
- **SQS**: 1M requests/month
- **CloudWatch**: 5GB logs

**Estimated Monthly Cost** (after free tier): $1-10 for light usage

## Security

- JWT authentication via Cognito
- IAM roles with least-privilege access
- S3 bucket with blocked public access
- CloudWatch logging for audit trails

## Development

### Local Testing

The Lambda functions can be tested locally using:
- AWS SAM CLI
- LocalStack
- Lambda test events in AWS Console

### Monitoring

Access logs and metrics via:
- CloudWatch Logs: `/aws/lambda/project-name-*`
- CloudWatch Metrics: Lambda, API Gateway, DynamoDB dashboards
- X-Ray tracing (can be enabled)

## Troubleshooting

### Common Issues

1. **JWT Authorization Failures**
   - Verify Cognito User Pool configuration
   - Check JWT token format and expiration
   - Ensure correct audience and issuer URLs

2. **Lambda Timeouts**
   - Check CloudWatch logs for error details
   - Verify SQS message format
   - Ensure proper IAM permissions

3. **S3 Access Errors**
   - Verify bucket permissions
   - Check Lambda execution role
   - Confirm bucket naming conventions

### Debugging Commands

```bash
# View stack events
make events

# View stack status
make status

# Check Lambda logs
aws logs tail /aws/lambda/project-name-jobhandler --follow

# Test API endpoint
curl -X POST https://api-id.execute-api.region.amazonaws.com/dev/job \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"test","action":"demo","context1":"hello","context2":"world"}'
```

## Cleanup

To remove all resources:

```bash
make delete
```

**Note**: S3 bucket must be empty before deletion. If deployment fails, you may need to empty the bucket manually.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Create an issue in this repository
- Check AWS CloudFormation documentation
- Review AWS service limits and quotas

## Roadmap

- [ ] Add CloudWatch alarms for monitoring
- [ ] Implement job priority queues
- [ ] Add batch job processing
- [ ] Support for multiple file formats
- [ ] Add API rate limiting
- [ ] Implement job scheduling
- [ ] Add notification system (SNS)
- [ ] Performance optimization guides
