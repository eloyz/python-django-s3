# AWS S3 Python and Django

The following is a cheat sheet I wrote for myself while doing a presentation
at [PyTexas][pytexas] and The [Python Web Development Houston Meetup][python-web].


## Install boto and ipython
    pip install boto ipython


## Connect to S3
    from boto.s3.connection import S3Connection
    conn = S3Connection(anon=True)
    conn = S3Connection('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY')

Please make sure to replace the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` with your credentials

### Shortcut to connect
    import boto
    conn = boto.connect_s3(anon=True)
    conn = boto.connect_s3('<aws access key>', '<aws secret key>')


## Set ACL


### Set ACL for bucket
    bucket = conn.get_bucket('meetuphouston')
    bucket.set_acl('public-read')


### Set ACL for key object
    bucket.set_acl('public-read', 'foobar')


### Set ACL for key object (via Key)
	from boto.s3.key import Key
    key = Key(bucket)
    key.key = 'foobar'
    key.set_acl('public-read')

## Bucket

### Create bucket
    bucket = conn.create_bucket('mybucket')

### List buckets
    buckets = conn.get_all_buckets()
    for bucket in buckets:
        print bucket.name
    
    buckets[0].name


## Create key (store data)
    key.key = 'this/whole/thing/is/a/key1'
    key.set_contents_from_string('This is my text')
    key.set_contents_from_file()
    key.set_contents_from_filename()
    key.set_contents_from_stream()
    
## Delete key (delete data)
    bucket.delete(key)

## Get data (from key)
    key.key = 'foobar'
    key.get_contents_as_string()  # returns content as string
    key.get_contents_to_file()  # returns python file object
    key.get_contents_to_filename(file_path)

## Copy files within bucket
    key.key = 'this/is/a/file'
    key.copy('mybucket', 'this/is/a/newfile')


## Get bucket access control policy
    acp = bucket.get_acl()
    acp.acl
    acp.acl.grants
    
    for grant in acp.acl.grants:
        print grant.permission, grant.grantee

## Set meta data
    key.key = 'has_metadata.txt'
    key.set_metadata('meta1', 'first value')
    key.set_metadata('meta2', 'second value')
    key.set_contents_from_filename('local-file.txt')

## Get meta data
    key.get_metadata('meta1')

## Download file
    key.key = 'some-file-on-s3.txt'
    download_path = '/Users/eloy/Desktop/some-file-from-s3.txt'

    with open(download_path, 'wb') as f:
        f.write(key.read())

# Using S3 with Django


## Install django-storages
    pip install django-storages

## Make a file called s3utils.py
    from storages.backends.s3boto import S3BotoStorage

    StaticRootS3BotoStorage = lambda: S3BotoStorage(location='static')
    MediaRootS3BotoStorage = lambda: S3BotoStorage(location='media')

Place this file in the same directory as **settings.py**

## Reference storage functions in settings.py
    STATICFILES_STORAGE='s3utils.StaticRootS3BotoStorage'  # collectstatic
    DEFAULT_FILE_STORAGE='s3utils.MediaRootS3BotoStorage'  # FileField

	AWS_ACCESS_KEY_ID = 'AKIAJKC4STM26PCFTTKA'
	AWS_SECRET_ACCESS_KEY = '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'
	AWS_STORAGE_BUCKET_NAME = 'meetuphouston'

STATICFILES_STORAGE is used when running the `collectstatic` management command.  
DEFAULT_FILE_STORAGE is used using a `FileField` object

## Django default storage
    dir_path = '/path/to/file'
    file_path = '/path/to/file/img.jpg'
    
### Check if file and directory exist
    default_storage.exists(file_path)
    default_storage.exists(dir_path)

### List files in directory
    default_storage.listdir(dir_path)

### Delete file and directory
Default storage deletes files just as easily as it deletes directories.  
You are not required to delete items in a directory before deleting the directory itself.

    default_storage.delete(file_path)  # file deleted
    default_storage.delete(dir_path)  # directory deleted

### Get file object
Get file objects by using the file.name, not the file.path

    from myobjects.models import MyObject
    
    my_object = MyObject.objects.get()
    file_path = my_object.form_field.file.name

    file_object = default_storage.open(file_path)
    print file_object.read()

`my_object.form_field.file.path` raises a NonImplementedError exception. Learn more [here][no-path].

### Create a model
	from django.db import models

	
	class MyObject(models.Model):
	    form_field = models.FileField(upload_to='dummy')

The `upload_to` attribute is required, but does nothing when using a custom backend storage such as S3.  A ticket exists for this [issue][upload-to]


###  return file response

    import mimetypes
    from django.http import HttpResponse
    from django.core.files.storage import default_storage
    from myobjects.models import MyObject


    def download_csv(request, pk):
        
        my_object = MyObject.objects.get(pk=pk)
        file_path = my_object.form_field.file.name
        file_object = default_storage.open(file_path)
        
        mimetype = mimetype.guess_type(
            file_object.name)[0]
    
        response = HttpResponse(
            file_object.read(),
            mimetype=mimetype)  # text/csv

        response['Content-Disposition'] = \
            'attachment; filename=%s' % file_object.name

		return response

You can hard-code the mime-type or you can use `mimetypes` object to guess your your mime-type based off of the file name extension.

[pytexas]: [http://pytexas.org/2013/talks/54/]
[python-web]:[http://www.meetup.com/python-web-houston/events/136739812/]

[upload-to]: [https://code.djangoproject.com/ticket/8918]
[no-path]: https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.Storage.path