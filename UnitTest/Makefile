.PHONY: job_submit job_status

# Replace this with a real job ID or pass it as a variable like JOB_ID=abc123
JOB_ID=your-job-id

job_submit:
	@echo "Submitting job..."
	python job_tester.py job_submit

job_status:
	@echo "Checking job status for JOB_ID=$(JOB_ID)..."
	python job_tester.py job_status $(JOB_ID)

get_all_jobs:
	@echo "Getting all jobs..."
	python job_tester.py get_all_jobs