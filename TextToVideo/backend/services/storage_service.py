from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import mimetypes

class StorageService:
    def __init__(self, connection_string: str):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.containers = {
            'media': 'media-assets',
            'videos': 'generated-videos',
            'thumbnails': 'thumbnails',
            'temp': 'temp'
        }
        
    def _get_container_client(self, container_type: str):
        """Get container client for the specified container type."""
        container_name = self.containers.get(container_type)
        if not container_name:
            raise ValueError(f"Invalid container type: {container_type}")
        return self.blob_service_client.get_container_client(container_name)
    
    def _get_content_settings(self, filename: str) -> ContentSettings:
        """Get content settings based on file type."""
        content_type, _ = mimetypes.guess_type(filename)
        return ContentSettings(content_type=content_type or 'application/octet-stream')
    
    async def upload_file(self, 
                         file_data: bytes, 
                         filename: str, 
                         container_type: str = 'media',
                         metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Upload a file to Azure Blob Storage.
        
        Args:
            file_data: The file data in bytes
            filename: The name of the file
            container_type: Type of container to upload to ('media', 'videos', 'thumbnails', 'temp')
            metadata: Optional metadata to attach to the blob
            
        Returns:
            Dict containing the blob URL and metadata
        """
        try:
            container_client = self._get_container_client(container_type)
            blob_client = container_client.get_blob_client(filename)
            
            # Set content settings based on file type
            content_settings = self._get_content_settings(filename)
            
            # Upload the file
            blob_client.upload_blob(
                file_data,
                overwrite=True,
                content_settings=content_settings,
                metadata=metadata
            )
            
            # Generate a SAS token for temporary access (if needed)
            sas_token = self._generate_sas_token(container_type, filename)
            
            return {
                'url': blob_client.url,
                'sas_url': f"{blob_client.url}?{sas_token}" if sas_token else None,
                'filename': filename,
                'container': container_type,
                'content_type': content_settings.content_type,
                'metadata': metadata
            }
            
        except Exception as e:
            raise Exception(f"Error uploading file: {str(e)}")
    
    def _generate_sas_token(self, container_type: str, filename: str, 
                          expiry_hours: int = 24) -> Optional[str]:
        """Generate a SAS token for temporary access to the blob."""
        try:
            container_client = self._get_container_client(container_type)
            blob_client = container_client.get_blob_client(filename)
            
            # Generate SAS token
            sas_token = blob_client.generate_shared_access_signature(
                permission="r",  # Read permission
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
            )
            return sas_token
        except Exception:
            return None
    
    async def delete_file(self, filename: str, container_type: str = 'media') -> bool:
        """Delete a file from Azure Blob Storage."""
        try:
            container_client = self._get_container_client(container_type)
            blob_client = container_client.get_blob_client(filename)
            blob_client.delete_blob()
            return True
        except ResourceNotFoundError:
            return False
        except Exception as e:
            raise Exception(f"Error deleting file: {str(e)}")
    
    async def get_file_url(self, filename: str, container_type: str = 'media', 
                          generate_sas: bool = True) -> Optional[str]:
        """Get the URL for a file, optionally with a SAS token."""
        try:
            container_client = self._get_container_client(container_type)
            blob_client = container_client.get_blob_client(filename)
            
            if generate_sas:
                sas_token = self._generate_sas_token(container_type, filename)
                return f"{blob_client.url}?{sas_token}" if sas_token else blob_client.url
            return blob_client.url
        except ResourceNotFoundError:
            return None
        except Exception as e:
            raise Exception(f"Error getting file URL: {str(e)}")
    
    async def list_files(self, container_type: str = 'media', 
                        prefix: Optional[str] = None) -> list:
        """List files in a container, optionally filtered by prefix."""
        try:
            container_client = self._get_container_client(container_type)
            blobs = container_client.list_blobs(name_starts_with=prefix)
            
            return [{
                'name': blob.name,
                'url': self._generate_sas_token(container_type, blob.name),
                'size': blob.size,
                'last_modified': blob.last_modified,
                'content_type': blob.content_settings.content_type
            } for blob in blobs]
        except Exception as e:
            raise Exception(f"Error listing files: {str(e)}") 