from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, HttpResponseError
import os
from dotenv import load_dotenv

def init_storage_account():
    # Load environment variables
    load_dotenv()
    
    # Get connection string from environment variable
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING not found in environment variables. Please check your .env file.")
    
    try:
        # Create the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Test the connection
        blob_service_client.get_service_properties()
        print("Successfully connected to Azure Storage Account!")
        
        # Define container names
        containers = [
            'media-assets',      # For original uploaded media
            'generated-videos',  # For AI-generated videos
            'thumbnails',        # For video preview images
            'temp'              # For temporary processing files
        ]
        
        # Create containers if they don't exist
        for container_name in containers:
            try:
                container_client = blob_service_client.get_container_client(container_name)
                if not container_client.exists():
                    container_client.create_container()
                    print(f"Created container: {container_name}")
                else:
                    print(f"Container already exists: {container_name}")
            except ResourceExistsError:
                print(f"Container already exists: {container_name}")
            except HttpResponseError as e:
                print(f"Error creating container {container_name}: {str(e)}")
                if "AuthenticationFailed" in str(e):
                    print("\nAuthentication Error! Please check your connection string in .env file.")
                    print("Make sure you've copied the entire connection string from Azure Portal.")
                    print("You can find it in: Storage Account -> Access Keys -> Connection String")
                    return
        
        print("\nStorage account initialization completed successfully!")
        
    except HttpResponseError as e:
        print(f"Error connecting to Azure Storage: {str(e)}")
        if "AuthenticationFailed" in str(e):
            print("\nAuthentication Error! Please check your connection string in .env file.")
            print("Make sure you've copied the entire connection string from Azure Portal.")
            print("You can find it in: Storage Account -> Access Keys -> Connection String")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    init_storage_account() 