from datetime import datetime
import uuid
import boto3
import os
from esmerald import UploadFile
from ulid import ULID
from nprOlusolaBe.configs import settings
from typing import Optional, Tuple
from botocore.exceptions import ClientError


class S3Handler:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.aws_endpoint_url,
            aws_access_key_id=settings.aws_access_key,
            aws_secret_access_key=settings.aws_secret_key,
            region_name=settings.aws_region_name,
        )
        self.bucket_name = settings.aws_bucket_name

    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename using UUID and timestamp"""
        ext = os.path.splitext(original_filename)[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = ULID().hex
        return f"{timestamp}_{unique_id}{ext}"

    def get_file_url(self, file_name: str) -> str:
        """Generate the public URL for the uploaded file"""
        return f"{settings.aws_endpoint_url}/{self.bucket_name}/{file_name}"

    async def upload_file(self, file: UploadFile) -> Tuple[bool, str, str]:
        """
        Upload file to Contabo Object Storage
        Returns: (success, message/url, filename)
        """
        try:
            # Generate unique filename
            unique_filename = self.generate_unique_filename(file.filename)

            # Read file content
            file_content = await file.read()

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_content,
                ContentType=file.content_type,
            )

            # Generate public URL
            file_url = self.get_file_url(unique_filename)
            return True, file_url, unique_filename

        except Exception as e:
            return False, str(e), ""
        finally:
            # Reset file pointer for potential reuse
            await file.seek(0)

    async def update_file(
        self, file: UploadFile, old_filename: str
    ) -> Tuple[bool, str, str]:
        """
        Update existing file in storage
        Returns: (success, message/url, filename)
        """
        try:
            # Check if old file exists
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=old_filename)
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    return False, "Original file not found", ""

            # Read new file content
            file_content = await file.read()

            # Upload new content with same filename
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=old_filename,
                Body=file_content,
                ContentType=file.content_type,
            )

            # Generate URL
            file_url = self.get_file_url(old_filename)
            return True, file_url, old_filename

        except Exception as e:
            return False, str(e), ""
        finally:
            await file.seek(0)

    async def delete_file(self, filename: str) -> Tuple[bool, str]:
        """
        Delete file from storage
        Returns: (success, message)
        """
        try:
            # Check if file exists
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=filename)
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    return False, "File not found"

            # Delete the file
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=filename)
            return True, "File deleted successfully"

        except Exception as e:
            return False, str(e)

    async def check_file_exists(self, filename: str) -> bool:
        """Check if a file exists in the bucket"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=filename)
            return True
        except ClientError:
            return False

    def get_file_metadata(self, filename: str) -> Optional[dict]:
        """Get metadata for a file"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=filename)
            return {
                "content_type": response.get("ContentType"),
                "content_length": response.get("ContentLength"),
                "last_modified": response.get("LastModified"),
                "metadata": response.get("Metadata", {}),
            }
        except ClientError:
            return None
