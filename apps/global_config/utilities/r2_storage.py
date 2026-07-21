import uuid
import boto3

from django.conf import settings


def get_r2_client():
    return boto3.session.Session().client(
        's3',
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    )


def upload_file_to_r2(file_obj, folder='uploads'):
    ext = file_obj.name.rsplit('.', 1)[-1].lower() if '.' in file_obj.name else ''
    filename = f'{uuid.uuid4().hex}.{ext}' if ext else uuid.uuid4().hex
    key = f'{folder}/{filename}'

    client = get_r2_client()
    client.put_object(
        Bucket=settings.R2_BUCKET_NAME,
        Key=key,
        Body=file_obj.read(),
        ContentType=file_obj.content_type or 'application/octet-stream',
    )

    if settings.R2_PUBLIC_URL:
        url = f'{settings.R2_PUBLIC_URL.rstrip("/")}/{key}'
    else:
        url = f'/api/files/{key}'

    return {'key': key, 'url': url, 'filename': file_obj.name, 'size': file_obj.size}
