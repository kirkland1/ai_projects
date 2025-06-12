from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import HttpResponseError
import os
from dotenv import load_dotenv

def setup_cors_rules():
    # Load environment variables
    load_dotenv()
    
    # Get connection string from environment variable
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING not found in environment variables. Please check your .env file.")
    
    try:
        # Create the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Define CORS rules
        cors_rules = {
            'cors_rules': [
                {
                    'allowed_origins': [
                        'http://localhost:3000',  # Flutter web development server
                        'http://localhost:8000',  # FastAPI development server
                        'https://your-production-domain.com'  # Add your production domain
                    ],
                    'allowed_methods': [
                        'GET',    # For downloading files
                        'POST',   # For uploading files
                        'PUT',    # For updating files
                        'DELETE', # For deleting files
                        'HEAD',   # For checking file existence
                        'OPTIONS' # For CORS preflight requests
                    ],
                    'allowed_headers': [
                        '*',  # Allow all headers
                    ],
                    'exposed_headers': [
                        'Content-Length',
                        'Content-Type',
                        'ETag',
                        'Last-Modified',
                        'x-ms-request-id',
                        'x-ms-version',
                        'x-ms-blob-content-type',
                        'x-ms-blob-content-disposition',
                        'x-ms-blob-content-encoding',
                        'x-ms-blob-content-language',
                        'x-ms-blob-content-md5',
                        'x-ms-blob-cache-control',
                        'x-ms-blob-sequence-number',
                        'x-ms-blob-type',
                        'x-ms-blob-committed-block-count',
                        'x-ms-blob-server-encrypted',
                        'x-ms-blob-copy-status',
                        'x-ms-blob-copy-source',
                        'x-ms-blob-copy-progress',
                        'x-ms-blob-copy-completion-time',
                        'x-ms-blob-copy-status-description',
                        'x-ms-blob-copy-id',
                        'x-ms-blob-copy-destination-snapshot',
                        'x-ms-lease-status',
                        'x-ms-lease-state',
                        'x-ms-lease-duration',
                        'x-ms-lease-id',
                        'x-ms-lease-time',
                        'x-ms-lease-break-time',
                        'x-ms-lease-end-time',
                        'x-ms-lease-start-time',
                        'x-ms-lease-status',
                        'x-ms-lease-state',
                        'x-ms-lease-duration',
                        'x-ms-lease-id',
                        'x-ms-lease-time',
                        'x-ms-lease-break-time',
                        'x-ms-lease-end-time',
                        'x-ms-lease-start-time'
                    ],
                    'max_age_in_seconds': 3600  # Cache preflight requests for 1 hour
                }
            ]
        }
        
        # Set the CORS rules
        blob_service_client.set_service_properties(cors=cors_rules)
        print("Successfully configured CORS rules for Azure Storage Account!")
        print("\nAllowed origins:")
        for origin in cors_rules['cors_rules'][0]['allowed_origins']:
            print(f"- {origin}")
        print("\nAllowed methods:", ', '.join(cors_rules['cors_rules'][0]['allowed_methods']))
        
    except HttpResponseError as e:
        print(f"Error configuring CORS rules: {str(e)}")
        if "AuthenticationFailed" in str(e):
            print("\nAuthentication Error! Please check your connection string in .env file.")
            print("Make sure you've copied the entire connection string from Azure Portal.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    setup_cors_rules() 