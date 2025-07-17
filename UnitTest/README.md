# 🧪 Job API Unit Tester

This repository provides a Python-based unit testing tool (`job_tester.py`) for an authenticated REST API that supports job submission and job status retrieval. It is primarily intended for testing API endpoints secured via AWS Cognito.

---

## ✅ What This Tool Tests

1. **Authentication via Cognito**
   - Validates that the user login and token retrieval works correctly using the `USER_PASSWORD_AUTH` flow.

2. **Job Submission**
   - Sends a POST request to submit a new job.
   - Confirms successful creation with status code `201`.
   - Validates presence of `job_id` and `status` in the response.

3. **Job Status Check**
   - Sends a GET request using a known `job_id`.
   - Confirms status retrieval succeeds.
   - Verifies response includes expected status field.

4. **Get All Jobs**
   - Sends a GET request to get all jobs endpoint
   - Prints each retrieved job
---

## 🧪 How to Run Unit Tests

This repo uses a `Makefile` to simplify running individual test cases.

### Submit a Job

```bash
make job_submit
```
### What it does?
* Calls the job_submit function inside job_tester.py
* Submits a test job to the API
* Prints the job_id and initial status

### Check Job Status

```bash
make job_status JOB_ID=your-job-id
```
### What it does?
* Calls the job_status function inside job_tester.py
* Retrieves the status of a job using the given ID
* Prints the job_id and its current status

### Gets All Jobs

```bash
make get_all_jobs
```
### What it does?
* Calls the get_all_jobs function inside job_tester.py
* Retrieves the status of all jobs
* For each retrived job prints the job_id and its current status

## 🔧 Configuration and Environment

### 🛠️ Prerequisites

- **Python 3.8+**
- `pip` installed
- **AWS CLI v2** installed and configured

### 🌐 AWS CLI Configuration

Ensure you have valid AWS credentials locally:

```bash
aws configure
```

##  🧪 Cognito Test User & API Configuration
```bash
export client_id=xxxxxxxxxxxxxxxxxxxxxx
export username="xxxxxxx"
export password="xxxxxxxxxxxxxxxxxxxx"
export job_api_url="https://xxxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/job"
```

###
* client_id – ID of your Cognito App Client
* username and password – credentials for a confirmed test user in your Cognito User Pool
* job_api_url - The API URL of generated API

## ✅ Final Checklist
Before running any test commands, ensure:
### 
1. Python 3.8+ is installed
2. AWS CLI v2 is installed and aws configure is successful
3. Environment variables for Cognito are set
4. (Optional) AWS_PROFILE is set if using named profiles

