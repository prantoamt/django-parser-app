from django.shortcuts import get_object_or_404

from rest_framework.status import (HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_204_NO_CONTENT)
from rest_framework.decorators import api_view, permission_classes, action
from django.http import HttpResponse
from django.http import HttpResponseForbidden, JsonResponse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.status import *
from rest_framework import viewsets
from rest_framework.exceptions import APIException,ParseError,NotFound

from parser_app.models import RegisteredModel
from parser_app.api.serializers import RegisteredModelSerializer
from django.db.models import Count

from parser_app.parser import DataParser

class RegisteredModelViewSet(viewsets.ModelViewSet):
    queryset = RegisteredModel.objects.all()
    serializer_class = RegisteredModelSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = RegisteredModel.objects.all()
        serializer = RegisteredModelSerializer(queryset, many=True, context={'request':request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        mapped_columns = request.data.get('mapped_columns')
        model_name = request.data.get('model')
        confirmed_upload = request.data.get('confirmed_upload') 
        foreign_key_map = request.data.get('foreign_key_map')
        kwargs = {'file_type': 'xls'}
        print('sadasdas')
        if confirmed_upload is not None:
            kwargs['confirmed_upload']= confirmed_upload
        elif confirmed_upload is None:
            kwargs['confirmed_upload']= None

        if mapped_columns is not None:
            mapped_columns = list(eval(mapped_columns))
            kwargs['mapped_columns'] = mapped_columns     
        else:
            kwargs['mapped_columns'] = None

        if foreign_key_map is not None:
            foreign_key_map = list(eval(foreign_key_map))
            kwargs['foreign_key_map'] = foreign_key_map
        else:
            kwargs['foreign_key_map'] = None

        if model_name is not None:
            data_parser = DataParser(model_name)
        else:
            res = {'detail': 'Please provide the model name'}
            return Response(res, status=HTTP_404_NOT_FOUND) 
            

        if mapped_columns is None and confirmed_upload is None:
            try:
                file_object = request.FILES['file']
                data_parser.save_file(file_object)
                kwargs['mapped_columns'] = None
            except Exception as e:
                raise APIException('No file received, please start from the beginning'+str(e))

        res = data_parser.parse_data_in_api_call(**kwargs)
        return Response(res, status=HTTP_201_CREATED)
