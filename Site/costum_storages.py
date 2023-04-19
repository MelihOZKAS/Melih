from  django.conf import settings

if settings.DEBUG:
    from django.core.files.storage import FileSystemStorage


    class MediaStorage(FileSystemStorage):
        file_overwrite = False
        default_acl = 'public-read'

    class DocumentStorage(FileSystemStorage):
        file_overwrite = False
        default_acl = 'public-read'

    class DocumentStorage(FileSystemStorage):
        file_overwrite = False
        default_acl = 'public-read'


else:
    from storages.backends.s3boto3 import S3Boto3Storage

    class MediaStorage(S3Boto3Storage):
        location = settings.MEDIA_LOCATION
        file_overwrite = False
        default_acl = 'public-read'

    class DocumentStorage(S3Boto3Storage):
        location = settings.Dosya_kayit_yeri
        file_overwrite = False
        default_acl = 'public-read'

    class ImageSettingStorage(S3Boto3Storage):
        location = settings.Resim_kayit_yeri
        file_overwrite = False
        default_acl = 'public-read'