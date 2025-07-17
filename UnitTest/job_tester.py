import boto3
import botocore.exceptions
import os
import sys
import requests
import json
import argparse

def getUserTokens():
    # Replace these values with your actual values
    client_id = os.getenv("client_id")
    username = os.getenv("username")
    password = os.getenv("password")
    job_api_url = os.getenv("job_api_url")
    jobs_api_url = os.getenv("jobs_api_url")

    if not all([client_id, username, password, job_api_url, jobs_api_url]):
        print("Missing required environment variables.")
        sys.exit(1)

    client = boto3.client("cognito-idp")

    try:
        response = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password
            },
            ClientId=client_id
        )

        auth_result = response['AuthenticationResult']
        return auth_result

    except botocore.exceptions.ClientError as e:
        print("Boto3 ClientError:", e.response['Error']['Message'])
    except Exception as e:
        print("Unexpected error:", str(e))


def get_job_status(job_id, access_token=None):
    try:
        job_api_url = os.getenv("job_api_url") + f"?job_id={job_id}"
        
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        response = requests.get(job_api_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get job status: {response.status_code} - {response.text}")
    except Exception as e:
        print("Unexpected error:", str(e))
    return None

def get_all_jobs(access_token=None):
    try:
        jobs_api_url = os.getenv("jobs_api_url")
        
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        response = requests.get(jobs_api_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get jobs: {response.status_code} - {response.text}")
    except Exception as e:
        print("Unexpected error:", str(e))
    return None

def submit_job(access_token=None):
    try:
        job_api_url = os.getenv("job_api_url") # The payload you want to submit
        payload = {
            "name": "Test Job",
            "action": "submit a job",
            "context1": "This is context 1",
            "context2": "This is context 2"
        }

        # Set the Authorization header with the token
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        # Make the POST request
        response = requests.post(job_api_url, json=payload, headers=headers)

        return response
    except Exception as e:
        print("Unexpected error:", str(e))
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Submit a job or get job status.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # job_status command
    status_parser = subparsers.add_parser("job_status", help="Check status of a job")
    status_parser.add_argument("job_id", help="The ID of the job to check")

    # job_submit command
    subparsers.add_parser("job_submit", help="Submit a new job")

    # get all jobs command
    subparsers.add_parser("get_all_jobs", help="Get all jobs")

    args = parser.parse_args()

    tokens = getUserTokens()

    if args.command == "job_status":
        response = get_job_status(args.job_id, tokens['AccessToken'])
        print("Response object:", response)
        sys.exit(0)
    elif args.command == "get_all_jobs":
        response = get_all_jobs(tokens['AccessToken'])
        #print("Response object:", response)
        print(json.dumps(response, indent=2))
        sys.exit(0)
    elif args.command == "job_submit":
        response = submit_job(tokens['AccessToken'])
        data = response.json()

        if 'job_id' in data:
            print(f"Job successfully submitted! Job ID: {data['job_id']}, its status: {data['status']}")
            print("Job submission failed!")
            print("Status Code:", getattr(response, 'status_code', 'None'))
            print("Text:", repr(getattr(response, 'text', 'None')))
            print("Headers:", getattr(response, 'headers', 'None'))


