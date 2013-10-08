import mimetypes
from django.http import HttpResponse
from django.core.files.storage import default_storage
from myobjects.models import MyObject


def download_csv(request):
    
    my_object = MyObject.objects.get()
    file_path = my_object.form_field.name
    file_object = default_storage.open(file_path)
    
    mimetype = mimetypes.guess_type(
        file_object.name)[0]

    response = HttpResponse(
        file_object.read(),
        mimetype=mimetype)  # text/csv

    response['Content-Disposition'] = \
        'attachment; filename=%s' % file_object.name

    return response