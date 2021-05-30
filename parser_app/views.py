
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from rest_framework.decorators import api_view
from django.conf import settings
from parser_app.parser import DataParser
from parser_app.models import RegisteredModel

base_url = settings.SITE_URL+'/api'

if hasattr(settings, 'FOREIGN_KEY_CONFIG_FOR_DATA_PARSER'):
    foreign_key_config_for_data_parser = settings.FOREIGN_KEY_CONFIG_FOR_DATA_PARSER
else:
    foreign_key_config_for_data_parser = {}

def import_data_with_data_parser_view(request, model):
    foreign_key_conf = foreign_key_config_for_data_parser.get(model.model_name,None)
    template = loader.get_template('parser_admin/base.html')
    context = {
        'title': f'Select file for model {model.model_name}',
        'base_url': base_url,
        'model': model.model_name,
        'opts': model._meta,
        'change': True,
        'is_popup': False,
        'save_as': False,
        'has_delete_permission': False,
        'has_add_permission': False,
        'has_change_permission': False}

    if foreign_key_conf is not None:
        context['foreign_key_config_for_data_parser'] =  foreign_key_config_for_data_parser[model.model_name]
    return HttpResponse(template.render(context, request))

@api_view(["POST"])
def map_columns(request):
    model_name = request.POST.get('model_name')
    model_columns = request.POST.get('model_columns')
    file_columns = request.POST.get('file_columns')
    required_fields = request.POST.get('required_fields').split(',')
    model_columns = model_columns.split(',')
    file_columns = file_columns.split(',')
    template = loader.get_template('parser_admin/column_mapping.html')
    context = {
        'title': f'Map your speadsheet columns with database columns',
        'base_url': base_url,
        'model': model_name,
        # 'opts': model._meta,
        'model_columns': model_columns,
        'file_columns': file_columns, 
        'required_fields': required_fields,
        'change': True,
        'is_popup': False,
        'save_as': False,
        'has_delete_permission': False,
        'has_add_permission': False,
        'has_change_permission': False}
    return HttpResponse(template.render(context, request))