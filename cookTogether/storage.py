from django.core.files.storage import Storage
from rest_framework.response import Response
from rest_framework import status
from supabase import create_client
from django.conf import settings

class SupabaseStorage(Storage):
    def __init__(self, bucket_name=f"{settings.SB_BUCKET_NAME}", **kwargs):
        self.bucket_name = bucket_name

        self.supabase = create_client(settings.SB_URL, settings.SB_KEY)
        self.storage_client = self.supabase.storage.from_(self.bucket_name)

    def _open(self, name, mode="rb"):
        # Implement the method to open a file from Supabase
        pass

    def _save(self, name, content):
        # Implement the method to save a file to Supabase
        content_file = content.file
        content_file.seek(0)  # Move the file pointer to the beginning
        content_bytes = content_file.read()
        response = self.supabase.storage.from_(self.bucket_name).upload(
            f"{settings.SB_BUCKET_PATH}{name}", content_bytes, {"content-type": content.content_type}
        )

        if not response.is_success:
            return Response({"error": "Falha ao enviar arquivo para armazenamento remoto."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response.json()["Key"]  # name/path of the file

    def exists(self, name):
        # Implement the method to check if a file exists in Supabase
        pass

    def url(self, name):
        # Implement the method to return the URL for a file in Supabase
        return f"{settings.SB_URL}/storage/v1/object/public/{name}"

    def get_available_name(self, name, *args, **kwargs):
        return name