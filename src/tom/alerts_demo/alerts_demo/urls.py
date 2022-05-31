from django.urls import path, include
import os

base_path = os.environ.get('URL_BASE_PATH', '').strip('/')
trailing_slash = ''
if base_path:
    trailing_slash = '/'

urlpatterns = [
    path(f'''{base_path}{trailing_slash}oidc/''', include('mozilla_django_oidc.urls')),
    # path(f'''{base_path}{trailing_slash}targets/<int:pk>/''', AlertsDemoTargetDetailView.as_view(), name='detail'),
    path(f'''{base_path}{trailing_slash}''', include('tom_common.urls'), name="home"),
]
