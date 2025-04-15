import gzip
import json

# Create sample content
test_data = {
    "dispatch_id": "test123",
    "campaign_id": "campaign456",
    "html_body": "<html><body><h1>Test Email</h1><p>This is a test email content.</p></body></html>"
}

# Write to a gzip file
with gzip.open('test_archive.gz', 'wb') as f:
    f.write(json.dumps(test_data).encode('utf-8'))

print("Test file created: test_archive.gz")
