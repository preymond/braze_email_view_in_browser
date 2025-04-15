# Braze Message Viewer

Lambda function that extracts HTML from Braze message archives stored in S3 and makes them available for browser viewing.

## Overview

This solution enables "View in Browser" functionality for Braze emails by:
1. Detecting when Braze uploads a message archive to S3
2. Extracting the HTML content
3. Storing it in a public S3 bucket with a folder structure that makes it easy to link to from emails

## Setup Instructions

1. Create two S3 buckets:
   - Source bucket: Where Braze archives messages
   - Destination bucket: Public bucket to host HTML files for browser viewing

2. Create an IAM role with these permissions:
   - Read from source bucket
   - Write to destination bucket
   - Basic Lambda execution permissions

3. Create the Lambda function:
   - Use the provided Python code
   - Set up an S3 trigger for object creation in the source bucket
   - Add the environment variable `DESTINATION_BUCKET` with your public bucket name

4. Update your Braze email templates to include "View in Browser" links:
   - For campaign emails: `https://your-bucket.s3.amazonaws.com/campaigns/{{campaign.${api_id}}}/{{campaign.${dispatch_id}}}/index.html`
   - For canvas emails: `https://your-bucket.s3.amazonaws.com/canvases/{{canvas.${id}}}/steps/{{campaign.${api_id}}}/{{campaign.${dispatch_id}}}/index.html`

## Deployment

To deploy this Lambda function using the AWS CLI:

```bash
aws lambda create-function \
  --function-name braze-message-extractor \
  --runtime python3.9 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::your-account-id:role/BrazeMessageExtractorRole \
  --zip-file fileb://deployment-package.zip
