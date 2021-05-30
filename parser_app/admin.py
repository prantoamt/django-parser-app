from django.contrib import admin
from parser_app.models import RegisteredModel
from parser_app.admin_mixin import AdminMixin
# Register your models here.
        
class RegisteredModelAdmin(admin.ModelAdmin, AdminMixin):
    list_display = ['model_name','app_label_name']
    search_fields = ['model_name']
    list_filter = []
    readonly_fields= ['model_name','app_label_name', 'model_fields', 'mapped_fields']
    fields = ['model_name','app_label_name', 'model_fields', 'mapped_fields']

    actions = ["import_with_parser_app"]

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True
        

admin.site.register(RegisteredModel, RegisteredModelAdmin)