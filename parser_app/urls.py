from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework import routers

from parser_app.api.views import RegisteredModelViewSet
from parser_app.views import import_data_with_data_parser_view, map_columns

router = routers.DefaultRouter()

router.register(r'data_parser',RegisteredModelViewSet,'data_parser')


urlpatterns = [
    path('', include(router.urls)),
    path('import_data_with_data_parser_view/', import_data_with_data_parser_view, name='import_with_data_parser'),
    path('map_columns/', map_columns, name='map_columns'),
]