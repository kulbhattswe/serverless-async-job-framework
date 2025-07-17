#!/bin/bash

# AWS Serverless Job Processing Stack Deployment Script

set -e
source .env

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME=${STACK_NAME}
TEMPLATE_FILE=${TEMPLATE_FILE:-"template.yaml"}
PARAMETERS_FILE=${PARAMETERS_FILE:-"updated-parameters.json"}

REGION=${REGION:-"us-east-1"}
echo "Using PARAMETERS_FILE  name: $PARAMETERS_FILE"
# Functions
print_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  deploy    Deploy the CloudFormation stack"
    echo "  update    Update existing stack"
    echo "  delete    Delete the stack"
    echo "  status    Show stack status"
    echo "  events    Show recent stack events"
    echo "  outputs   Show stack outputs"
    echo "  logs      Show recent Lambda logs"
    echo ""
    echo "Options:"
    echo "  -s, --stack-name NAME    Stack name (default: $STACK_NAME)"
    echo "  -r, --region REGION      AWS region (default: $REGION)"
    echo "  -p, --parameters FILE    Parameters file (default: $PARAMETERS_FILE)"
    echo "  -h, --help              Show this help message"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed or not in PATH"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured or invalid"
        exit 1
    fi
    
    # Check template file
    if [ ! -f "$TEMPLATE_FILE" ]; then
        print_error "Template file $TEMPLATE_FILE not found"
        exit 1
    fi
    
    # Check parameters file
    if [ ! -f "$PARAMETERS_FILE" ]; then
        print_error "Parameters file $PARAMETERS_FILE not found"
        print_info "Please create $PARAMETERS_FILE based on parameters.json.template"
        exit 1
    fi
    
    print_info "Prerequisites check passed"
}

deploy_stack() {
    print_info "Deploying CloudFormation stack: $STACK_NAME"
    print_info "Stack creation initiated. with template=${TEMPLATE_FILE}"
    print_info " parameters=${PARAMETERS_FILE}.   Waiting for completion..."
    
    aws cloudformation deploy \
        --stack-name "$STACK_NAME" \
        --template-file "$TEMPLATE_FILE" \
        --parameter-overrides "file://$PARAMETERS_FILE" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION" 
    
     if [ $? -eq 0 ]; then
        print_info "Stack deployed successfully!"
        show_outputs
    else
        print_error "Stack deployment failed"
        exit 1
    fi
}

update_stack() {
    print_info "Updating CloudFormation stack: $STACK_NAME"
    
    aws cloudformation update-stack \
        --stack-name "$STACK_NAME" \
        --template-body "file://$TEMPLATE_FILE" \
        --parameters "file://$PARAMETERS_FILE" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION" #\
        #2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_info "Stack update initiated. Waiting for completion..."
        
        aws cloudformation wait stack-update-complete \
            --stack-name "$STACK_NAME" \
            --region "$REGION"
        
        if [ $? -eq 0 ]; then
            print_info "Stack updated successfully!"
            show_outputs
        else
            print_error "Stack update failed"
            exit 1
        fi
    else
        print_warning "No updates to perform or stack update failed"
    fi
}

delete_stack() {
    print_warning "This will delete the entire stack and all its resources!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Deleting CloudFormation stack: $STACK_NAME"
        
        # First, empty the S3 bucket if it exists
        BUCKET_NAME=$(aws cloudformation describe-stacks \
            --stack-name "$STACK_NAME" \
            --region "$REGION" \
            --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
            --output text 2>/dev/null)
        
        if [ "$BUCKET_NAME" != "None" ] && [ -n "$BUCKET_NAME" ]; then
            print_info "Emptying S3 bucket: $BUCKET_NAME"
            aws s3 rm "s3://$BUCKET_NAME" --recursive --region "$REGION" 2>/dev/null || true
        fi
        
        aws cloudformation delete-stack \
            --stack-name "$STACK_NAME" \
            --region "$REGION"
        
        print_info "Stack deletion initiated. Waiting for completion..."
        
        aws cloudformation wait stack-delete-complete \
            --stack-name "$STACK_NAME" \
            --region "$REGION"
        
        print_info "Stack deleted successfully!"
    else
        print_info "Stack deletion cancelled"
    fi
}

show_status() {
    print_info "Stack Status:"
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].{Status:StackStatus,Created:CreationTime,Updated:LastUpdatedTime}' \
        --output table
}

show_outputs() {
    print_info "Stack Outputs:"
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs' \
        --output table
}

show_events() {
    print_info "Stack Events:"
    aws cloudformation describe-stack-events \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --max-items 20
}

show_logs() {
    print_info "Recent Lambda logs (last 5 minutes):"
    
    # Get function names from stack outputs
    JOBHANDLER_FUNCTION=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`JobHandlerFunctionName`].OutputValue' \
        --output text 2>/dev/null)
    
    if [ "$JOBHANDLER_FUNCTION" != "None" ] && [ -n "$JOBHANDLER_FUNCTION" ]; then
        print_info "JobHandler Lambda logs:"
        aws logs tail "/aws/lambda/$JOBHANDLER_FUNCTION" \
            --since 5m \
            --region "$REGION" \
            --format short
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--stack-name)
            STACK_NAME="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -p|--parameters)
            PARAMETERS_FILE="$2"
            shift 2
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        deploy)
            COMMAND="deploy"
            shift
            ;;
        update)
            COMMAND="update"
            shift
            ;;
        delete)
            COMMAND="delete"
            shift
            ;;
        status)
            COMMAND="status"
            shift
            ;;
        events)
            COMMAND="events"
            shift
            ;;
        outputs)
            COMMAND="outputs"
            shift
            ;;
        logs)
            COMMAND="logs"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Execute command
case $COMMAND in
    deploy)
        check_prerequisites
        deploy_stack
        ;;
    update)
        check_prerequisites
        update_stack
        ;;
    delete)
        delete_stack
        ;;
    status)
        show_status
        ;;
    events)
        show_events
        ;;
    outputs)
        show_outputs
        ;;
    logs)
        show_logs
        ;;
    *)
        print_error "No command specified"
        print_usage
        exit 1
        ;;
esac