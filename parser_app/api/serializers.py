from rest_framework import serializers
from rest_framework import serializers
from rest_framework.fields import SkipField
from rest_framework.fields import ChoiceField
import six
from parser_app.models import RegisteredModel


class ChoiceDisplayField(ChoiceField):
    def __init__(self, *args, **kwargs):
        super(ChoiceDisplayField, self).__init__(*args, **kwargs)
        self.choice_strings_to_display = {
            six.text_type(key): value for key, value in self.choices.items()
        }

    def to_representation(self, value):
        if value is None:
            return value
        return {
            'value': self.choice_strings_to_values.get(six.text_type(value), value),
            'name': self.choice_strings_to_display.get(six.text_type(value), value),
        }


class DefaultModelSerializer(serializers.ModelSerializer):
    serializer_choice_field = ChoiceDisplayField


class RegisteredModelSerializer(DefaultModelSerializer):
    class Meta:
        model = RegisteredModel
        fields = '__all__'


class MappingErrorSerializer(serializers.Serializer):
    detail = serializers.CharField(max_length=256, required=False)
    model_columns = serializers.ListField(child=serializers.CharField())
    file_columns = serializers.ListField(child=serializers.CharField())
    required_fields = serializers.ListField(child=serializers.CharField())
    foreign_key_fields = serializers.ListField(child=serializers.CharField())

class ValidationErrorSerializer(serializers.Serializer):
    detail = serializers.ListField(child=serializers.JSONField())