from __future__ import annotations

from django.conf import settings
from django.core.files.storage import storages

from storages.backends.s3 import S3Storage


class CachedS3Storage(S3Storage):
    """S3 storage backend that saves the files locally, too."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.local_storage = storages.create_storage({
            "BACKEND": "compressor.storage.CompressorFileStorage",
            "OPTIONS": {
                "location": f"{settings.COMPRESS_ROOT}/{settings.STATIC_PREFIX}"
            },
        })

    def save(self, name, content):
        self.local_storage.save(name, content)
        super().save(name, self.local_storage._open(name))  # noqa: SLF001
        return name
