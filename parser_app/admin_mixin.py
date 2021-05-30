from django.contrib import messages
from django.utils.translation import ngettext
from django.http import Http404
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import path, include
from parser_app.views import import_data_with_data_parser_view

class AdminMixin(object):
    
    def import_with_data_parser(self, request, queryset):
        if len(queryset) > 1:
            self.message_user(request, 'Please select only one model', messages.WARNING)
        else:
            return import_data_with_data_parser_view(request, queryset[0]) 
