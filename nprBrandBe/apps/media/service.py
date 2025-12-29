import uuid
from edgy import or_
import magic
from typing import List, Optional
from esmerald import UploadFile, status
from nprOlusolaBe.apps.media.models import Media
from nprOlusolaBe.core.schema import QueryTypeWithoutLoadRelated
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.apps.media.v1 import schemas
from nprOlusolaBe.utils.base_response import get_error_response, get_response
from nprOlusolaBe.apps.media.mixin import S3Handler


class MediaService:
    # Constants
    MAX_FILE_SIZE_MB = 5
    BYTE_SIZES = {"KB": 1024, "MB": 1024 * 1024}
    ALLOWED_EXTENSIONS = frozenset(["jpg", "png", "jpeg", "gif", "webp", "mp4", "mov"])

    def __init__(self):
        self._service = BaseService[Media](model=Media, model_name="Media")
        self.s3 = S3Handler()

    async def _validate_file_size(
        self, file: UploadFile, filename: Optional[str] = None
    ) -> None:
        """Validate file size is within limits"""
        if not 0 < file.size <= self.MAX_FILE_SIZE_MB * self.BYTE_SIZES["MB"]:
            msg = f"Maximum supported file size of {self.MAX_FILE_SIZE_MB}MB exceeded"
            if filename:
                msg += f" by {filename}"
            raise get_error_response(
                detail=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    async def get_file(self, file_id: uuid.UUID):
        return await self._service.get(file_id, raise_error=True)

    async def list_file(
        self,
        params: QueryTypeWithoutLoadRelated,
        is_active: bool = None,
    ):
        check_list = []
        checks = {}
        if params.filter_string:
            check_list.append(
                or_.from_kwargs(
                    file_name=params.filter_string,
                    type=params.filter_string,
                )
            )
        if not is_active is None:
            checks["is_active"] = is_active
        return await self._service.filter_and_list(
            check_list=check_list,
            check=checks,
            **params.model_dump(exclude={"filter_string"}),
        )

    async def _validate_file_type(self, file: UploadFile) -> None:
        """Validate file type using magic and extension"""
        try:
            # Read file content for magic number check
            file_content = await file.read(
                self.BYTE_SIZES["KB"]
            )  # Read just 1KB for mime type detection
            mime_type = magic.from_buffer(file_content, mime=True)
            extension = file.filename.split(".")[-1].lower()

            if extension not in self.ALLOWED_EXTENSIONS:
                raise get_error_response(
                    detail=f"Unsupported file extension: {extension}",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Reset file pointer for future operations
            await file.seek(0)

        except Exception as e:
            raise get_error_response(
                detail=f"Error validating file type: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    async def _process_single_file(self, file: UploadFile) -> Media:
        """Process and upload a single file"""
        await self._validate_file_size(file)
        await self._validate_file_type(file)

        is_created, file_url, file_name = await self.s3.upload_file(file)
        if not is_created:
            raise get_error_response(
                detail="Failed to upload file to S3",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        payload = schemas.MediaIn(
            url=file_url,
            file_name=file_name,
            type=file.content_type,
        )
        return await self._service.create(payload=payload)

    async def create(self, file: UploadFile) -> Media:
        """Create a single media entry"""
        try:
            return await self._process_single_file(file)
        except Exception as e:
            raise get_error_response(str(e)) from e

    async def create_bulk(self, files: List[UploadFile]) -> List[Media]:
        """Create multiple media entries"""
        if not files:
            raise get_error_response(
                detail="No files provided",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result_list = []
            for file in files:
                # Validate each file
                await self._validate_file_size(file, file.filename)
                await self._validate_file_type(file)

                is_created, file_url, file_name = await self.s3.upload_file(file)
                if not is_created:
                    continue

                if is_created and file_name and file_url:
                    result_list.append(
                        schemas.MediaIn(
                            url=file_url,
                            type=file.content_type,
                            file_name=file_name,
                        ).model_dump()
                    )
            if len(result_list) > 0:
                result = await self._service.bulk_create(result_list)
                if result:
                    return get_response(
                        data=result,
                        status_code=status.HTTP_201_CREATED,
                    )
            raise get_error_response(detail="Could not upload file", status_code=500)
        except Exception as e:
            raise e

    async def delete_file(self, file_id: uuid.UUID) -> dict[str, int]:
        """Delete a media file"""
        file = await self._service.get(file_id, raise_error=True)
        if not file:
            raise get_error_response(
                detail="File does not exist",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        deleted, message = await self.s3.delete_file(file.file_name)
        if not deleted:
            raise get_error_response(
                detail=f"Failed to delete file from storage: {message}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return await self._service.delete(id=file_id)

    async def update_file(self, file_id: uuid.UUID, file: UploadFile) -> Media:
        """Update a media file"""
        existing_file = await self._service.get(file_id, raise_error=True)
        if not existing_file:
            raise get_error_response(
                detail="File does not exist",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Validate new file
        await self._validate_file_size(file)
        await self._validate_file_type(file)

        is_updated, file_url, file_name = await self.s3.update_file(
            file=file,
            old_filename=existing_file.file_name,
        )

        if not is_updated:
            raise get_error_response(
                detail="Failed to update file in storage",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return existing_file
