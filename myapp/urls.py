from django.urls import path
from myapp.views import *

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
]
