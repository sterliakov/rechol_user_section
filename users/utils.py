from __future__ import annotations

import uuid

import boto3


def generate_upload_url(
    extra_path,
    field,
    max_size=50 * 1024 * 1024,
    expiration=24 * 60 * 60,
    extension="pdf",
):
    client = boto3.client("s3")
    filename = field.storage.get_available_name(uuid.uuid4())
    full_key = "/".join([
        field.storage.location,
        field.upload_to,
        extra_path,
        f"{filename}.{extension}",
    ])
    return client.generate_presigned_post(
        field.storage.bucket_name,
        full_key,
        Fields={"Content-Type": "application/pdf"},
        Conditions=[
            ["content-length-range", 1, max_size],
            {"Content-Type": "application/pdf"},
        ],
        ExpiresIn=expiration,
    )
