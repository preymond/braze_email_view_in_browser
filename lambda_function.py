import boto3
import gzip
import json
import os
import io
import traceback
from urllib.parse import unquote_plus

s3_client = boto3.client('s3')

# Configuration
destination_bucket = os.environ.get('DESTINATION_BUCKET', 'default-bucket-name')  # Fallback value

def lambda_handler(event, context):
    print("Lambda function started")
    print(f"Event received: {json.dumps(event)}")
    print(f"Destination bucket set to: {destination_bucket}")

    try:
        # Check if event has expected structure
        if 'Records' not in event or len(event['Records']) == 0:
            print("Error: No records found in event")
            return {
                'statusCode': 400,
                'body': 'No records found in event'
            }

        # Get the S3 bucket and key from the event
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        key = unquote_plus(event['Records'][0]['s3']['object']['key'])

        print(f"Processing file {key} from bucket {source_bucket}")

        try:
            # Download the .gz file
            print(f"Attempting to download file from {source_bucket}/{key}")
            response = s3_client.get_object(Bucket=source_bucket, Key=key)
            compressed_content = response['Body'].read()
            print(f"Downloaded file, size: {len(compressed_content)} bytes")

            # Decompress the .gz file
            print("Decompressing file")
            with gzip.GzipFile(fileobj=io.BytesIO(compressed_content), mode='rb') as gzipped_file:
                file_content = gzipped_file.read().decode('utf-8')
            print(f"Decompressed file, content length: {len(file_content)}")

            # Parse the file content as JSON
            print("Parsing file content as JSON")
            message_data = json.loads(file_content)
            print("Successfully parsed file as JSON")

            # Extract relevant fields based on the actual structure
            print("Extracting fields from the parsed data")

            # Extract the IDs we need from the message data
            dispatch_id = message_data.get('dispatch_id', 'unknown')
            campaign_id = message_data.get('campaign_id')
            canvas_id = message_data.get('canvas_id')
            step_id = message_data.get('canvas_step_id')

            print(f"Extracted IDs - Dispatch: {dispatch_id}, Campaign: {campaign_id}, Canvas: {canvas_id}, Step: {step_id}")

            # Extract HTML content from html_body field
            html_content = message_data.get('html_body')

            if not html_content:
                print("HTML content not found in html_body field")
                return {
                    'statusCode': 200,
                    'body': json.dumps('No HTML content found in the message')
                }

            print(f"HTML content found, length: {len(html_content)}")

            # Create the destination path based on campaign or canvas
            if campaign_id:
                destination_path = f"campaigns/{campaign_id}/{dispatch_id}/index.html"
            elif canvas_id and step_id:
                destination_path = f"canvases/{canvas_id}/steps/{step_id}/{dispatch_id}/index.html"
            else:
                destination_path = f"messages/{dispatch_id}/index.html"

            print(f"Destination path: {destination_path}")

            # Upload the HTML content to the destination bucket
            print(f"Uploading HTML to {destination_bucket}/{destination_path}")
            s3_client.put_object(
                Bucket=destination_bucket,
                Key=destination_path,
                Body=html_content,
                ContentType='text/html',
                CacheControl='max-age=86400',  # Cache for 1 day
                ACL='public-read'  # Make it publicly accessible
            )

            # Generate the public URL
            public_url = f"https://{destination_bucket}.s3.amazonaws.com/{destination_path}"
            print(f"HTML content extracted and uploaded to: {public_url}")

            return {
                'statusCode': 200,
                'body': json.dumps('HTML extraction and upload successful'),
                'url': public_url
            }

        except json.JSONDecodeError as json_err:
            print(f"Failed to parse file as JSON: {str(json_err)}")
            return {
                'statusCode': 400,
                'body': f'Invalid JSON format: {str(json_err)}'
            }

        except s3_client.exceptions.NoSuchKey:
            print(f"Error: File {key} does not exist in bucket {source_bucket}")
            return {
                'statusCode': 404,
                'body': f'File not found: {key}'
            }

        except Exception as inner_e:
            print(f"Error processing file {key}: {str(inner_e)}")
            print(f"Inner traceback: {traceback.format_exc()}")
            raise inner_e

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'body': f'Error processing request: {str(e)}'
        }
