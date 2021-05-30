from django.db import transaction
from rest_framework.exceptions import APIException,ParseError,NotFound
from rest_framework.response import Response
from rest_framework.status import (HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_204_NO_CONTENT)
from django.apps import apps
from parser_app.models import RegisteredModel
import pandas as pd
import numpy as np
from parser_app.api.serializers import MappingErrorSerializer, ValidationErrorSerializer
class DataParser(object):
    '''The parser takes an excel file as input and stores the data in the corresponsing registered 
    model. The parser is used in two stage: 1) configuration, 2) execution
    ----------------------------------------configuration----------------------------------------------
    1) register a moder using the register_model() static function in admin.py file.
     -> example: DataParser.register_model(Area)
    2) after registering, restart the server.
    3) the model's necessary data will be recorded in 'RegisteredModel' model. All registered models 
    can be seen in "Registered models" model Under the DATAPARSER section
    ------------------------------------------execution-----------------------------------------------
    1) after that, make an api POST request with two parameters. 
        'model': 'the model's name you are wishing to import data using xl'.
        'file': 'the xl file'.
        ---------------------
        Example input:
        {
            'model': 'Area'
            'file': 'area.xls'
        }    
        ---------------------
        if the model has foreign keys, then those should be passed in this step with referenced column
        ---------------------
        Example input:
        {
            'model': 'Area'
            'file': 'area.xls'
            'foreign_key_map': [{'parent_code':'code',....}]
        }    
        ---------------------
    2) the parser will return you the model's meta data and the xl file's column names under the keys:
        'model_columns', 'file_columns', 'required_fields', 'foreign_key_fields'
        ---------------------
        Example output:
        {
            'model_columns': ['code', 'location_name', 'location_type', 'parent_code'],
            'file_columns': ['code', 'name', 'type', 'parent'],
            'required_fields': ['code', 'parent_code'],
            'foreign_key_fields': ['parent_code']
        }
        ---------------------
    3) In the next step, the front-end developer should map the model columns and file columns. 
        The developer must force the users to map required fileds' columns. After that, the developer 
        will make the second POST request with the 'model name' and 'mapped columns'.
        ---------------------
        Example input:
        {
            'model': 'Area',
            'mapped_columns': [{'file_column':'code', 'model_column':'code'}, 
                            {'file_column':'name', 'model_column':'location_name'}, 
                            {'file_column':'type', 'model_column':'location_type'}, 
                            {'file_column':'parent', 'model_column':'parent_code'}]
        }
        ---------------------
    4) With this response, the parser will validate the file's input data and return the response as 
        follows if any validation error encouters:
        ---------------------
        Example output:
        {
            'detail': 'error': [{'Field 'code' expected int but got 'Amtali' at row no 4'}],
            'total_errors': 1,
        }
        ---------------------
        Example output:
        if no validation error found:
        {
            'detail' : 'errors': [{'error': 'No validation error encountered. Your input file has 30 
            items which already exists in the database. Therefore, 50 new items will be created.'}]
        }
        ---------------------
    5) Front-end should not allow users to confirm upload untill validation errors are fixed. Once the 
        step 4 returns No validation error message, the front-end can make it's final POST request with
        model name and confirmed upload key as follows:
        ---------------------
        Example input:
        {
            'model': 'Area',
            'confirmed_upload': true,
        }
    '''
    def __init__(self, model_name):
        self.__settings(model_name)

    def __settings(self, model_name):
        '''Takes model name as argument and extract all meta deta of the model from registered 
        model and from the model itself as well'''
        self.__model_fields = [] ##list of all fields of the model that is registred in Data Perser
        self.__model_fields, self.__model_object_in_register_model, app_name = self.__get_model_data(model_name)
        self.__model = apps.get_model(app_name, model_name) ## returns the original model which is registered
        self.__foreign_key_field = self.__get_foreign_key_fields()
        self.__required_fields = self.__get_required_fields()
        self.__successful_upload_response = {'detail': 'Data successfully uploaded to '+ str(self.__model.__name__) + ' model.'}

    def __get_model_data(self,model_name):
        '''Takes model name as input and checks if the model is registered in Data Parser or not.
        If registered, returns all fields of the registerd model, the registered model's object,
        and the app level name of the registered model'''
        model_object_in_register_model = RegisteredModel.objects.filter(model_name=model_name)
        if model_object_in_register_model.exists():
            return model_object_in_register_model[0].model_fields, model_object_in_register_model[0], model_object_in_register_model[0].app_label_name
        else:
            raise APIException('The model ' + "'"+str(self.__model.__name__)+"'" + ' is not registered. Please use '+ "'"+'DataParser.register_model('+str(self.__model.__name__)+')'+"'"+ ' inside your admin.py file to register it.')
    
    def get_model_object_in_register_model(self):
        return self.__model_object_in_register_model


    @staticmethod
    def get_model_name_and_fields(model):
        '''Retruns the model's name and all the fields of the model'''
        name = model.__name__
        fields = [f.name for f in model._meta.fields]
        return name, fields            
    
    @staticmethod
    def register_model(model_to_be_registered):
        '''Registers the model in DataParser's records. That means, 
        1) the method first takes which model to be registered as argumnet. 
        2) then extracts the the model's and fields name.
        3) checks if the model [model name] is already registered or not.
        4) if registered:
            5)checks if any new fields are added or old fields are removed from this model.
            6) if added or removed:
                7) delete the old record in DataParser's RegisteredModel and create new record with new informantion
        '''
        name_of_the_model_to_be_registered, fields_of_the_model_to_be_registered = DataParser.get_model_name_and_fields(model_to_be_registered)
        if 'id' in fields_of_the_model_to_be_registered:
            fields_of_the_model_to_be_registered.remove('id')

        #check if the model is already registered
        registered_model_object = RegisteredModel.objects.filter(model_name=name_of_the_model_to_be_registered)
        if registered_model_object.exists():
            existing_objects_fields = registered_model_object[0].model_fields

            #if new field is added, then delete old registration and add new    
            for item in fields_of_the_model_to_be_registered:
                if item not in existing_objects_fields:
                    with transaction.atomic():
                        registered_model_object.delete()
                        RegisteredModel.objects.create(model_name = name_of_the_model_to_be_registered, model_fields = fields_of_the_model_to_be_registered, app_label_name = model_to_be_registered._meta.app_label)

            #if old field is removed, then delete old registration and add new         
            for item in existing_objects_fields:
                if item not in fields_of_the_model_to_be_registered:
                    with transaction.atomic():
                        registered_model_object.delete()
                        RegisteredModel.objects.create(model_name = name_of_the_model_to_be_registered, model_fields = fields_of_the_model_to_be_registered, app_label_name = model_to_be_registered._meta.app_label)     
            return True
        else:
            new_register = RegisteredModel.objects.create(model_name=name_of_the_model_to_be_registered,model_fields=fields_of_the_model_to_be_registered, app_label_name = model_to_be_registered._meta.app_label)
            return True

    def save_file(self, file_input, *args, **kwargs):
        self.__model_object_in_register_model.file_input = file_input
        self.__model_object_in_register_model.save()

    
    def parse_data_in_api_call(self, *args, **kwargs):
        '''Takes file type, mapped columns, foriegn key mapped, confirmed_upload value as not mandatory
        arguments and performs several actions based on the values.
        1) If mapped_columns and confirmed_upload kwargs is not found, the method will consider that
            invoker is in the first step and wants to map file/spreadsheet columns vs model columns.
            Therefore, the function will return necessary data by invoking  '''
        file_type = kwargs['file_type']
        mapped_columns = kwargs['mapped_columns']
        foreign_key_map = kwargs['foreign_key_map']
        confirmed_upload = kwargs['confirmed_upload']

        #open file
        if(file_type not in ['csv','xls','xlsx']):
            raise APIException('Only csv, xls and xlsx format is supported')
        df = pd.read_excel(self.__model_object_in_register_model.file_input)

        # df = df.replace(to_replace='None', value=np.nan).dropna()

        ## The first time request, when only file is passed without mapping
        if mapped_columns is None and confirmed_upload is None:
            return self.__perform_action_for_unmapped_columns(df, foreign_key_map)

        ## The second time request, when model column vs spreadseet column mapping is passed
        if mapped_columns is not None and confirmed_upload is None:
            return self.__validate_inputs(df, mapped_columns)

        ## The thrid time request, when all validation is completed and upload is confirmed
        if mapped_columns is None and confirmed_upload is not None:
            saved_mapped_fields = self.__model_object_in_register_model.mapped_fields
            return self.__perform_action_for_mapped_columns(df, saved_mapped_fields)
        return self.__successful_upload_response 

    def __perform_action_for_unmapped_columns(self, df, foreign_key_map):
        '''check if all columns in xl matches with columns in registered models'''
        if len(self.__foreign_key_field) > 0 and foreign_key_map is None:
            res = {'detail': 'The model have unspecified foreign key fileds. Please ask your developer team to map them first.'}
            return res
        elif len(self.__foreign_key_field) > 0 and foreign_key_map is not None:
            try:
                self.__model_object_in_register_model.foreign_key_mapped_fields = foreign_key_map
                self.__model_object_in_register_model.save()  
            except Exception as e:
                raise APIException('Error encourtered during foreign key mapping storage: '+str(e))    
        elif len(self.__foreign_key_field) <= 0:
            self.__model_object_in_register_model.foreign_key_mapped_fields = None
            self.__model_object_in_register_model.save()

        columns = df.columns.values
        context = {
            'model_columns':self.__model_fields,
            'file_columns':columns,
            'required_fields': self.__required_fields,
            'foreign_key_fields': self.__foreign_key_field
        }
        print(context,'-----------')
        serializer = MappingErrorSerializer(data=context)
        serializer.is_valid(raise_exception=True)
        return (serializer.data)    
    
    def __validate_inputs(self, df, mapped_columns):
        foreign_key_map_stored_map = None
        if len(self.__foreign_key_field) > 0:
            foreign_key_map_stored_map = self.__model_object_in_register_model.foreign_key_mapped_fields
        errors = []
        existing_counts = 0
        data = {}
        columns = df.columns.values
        for (idx, row) in df.iterrows():
            kwargs={}
            try:
                for column_in_file in columns:
                    for item_in_map in mapped_columns:
                        if item_in_map['file_column'] == column_in_file:
                            if item_in_map['file_column'].lower() != 'ignore' and item_in_map['model_column'].lower() != 'ignore':
                                if foreign_key_map_stored_map is not None:
                                    for obj in foreign_key_map_stored_map:
                                        if item_in_map['model_column'] in obj.keys():
                                            foreign_field_of_the_model = self.__model._meta.get_field(item_in_map['model_column']).remote_field.model
                                            filter_kwrags = {}
                                            filter_kwrags[str(obj[item_in_map['model_column']])] = row.loc[item_in_map['file_column']]
                                            foreign_field_of_the_model_obj = foreign_field_of_the_model.objects.filter(**filter_kwrags).first()
                                            if foreign_field_of_the_model_obj is None:
                                                field_name = item_in_map['model_column']
                                                msg = f'No entry found named {row.loc[item_in_map["file_column"]]} in {field_name} model. Please create at least one object with this name to make reference.'
                                                self.__raise_exceptions(**{'msg':msg})
                                            model_foreign_key_column = item_in_map['model_column'] + "__" + str(obj[item_in_map['model_column']])
                                            kwargs[model_foreign_key_column] = row.loc[item_in_map['file_column']]
                                        else:
                                            kwargs[item_in_map['model_column']] = row.loc[item_in_map['file_column']]    
                                else:
                                    kwargs[item_in_map['model_column']] = row.loc[item_in_map['file_column']]
                existing_item = self.__model.objects.filter(**kwargs)
                existing_counts = existing_counts + len(existing_item)
            except Exception as e:
                error = {
                    'error': "At row no. "+ str(idx+1) + ", " + str(e)
                }
                errors.append(error)

        context = {
            'detail': errors
        }
        self.__model_object_in_register_model.mapped_fields = mapped_columns
        self.__model_object_in_register_model.save()
        total_errors = len(errors)   
        data = ValidationErrorSerializer(context).data
        data['total_errors'] = len(errors)
        if total_errors <= 0:
            total_counts = df.shape[0]
            will_create_count = int(total_counts) - int(existing_counts)
            data['detail'] = [{'error':f'No validation errors were encountered. Your input file has total {total_counts} items from which {existing_counts} item(s) already exist(s) in the database. Therefore, {will_create_count} new item(s) will be created.'}]
        return data


    @transaction.atomic
    def __perform_action_for_mapped_columns(self, df, mapped_columns):
        foreign_key_map_stored_map = None
        if len(self.__foreign_key_field) > 0:
            foreign_key_map_stored_map = self.__model_object_in_register_model.foreign_key_mapped_fields
        columns = df.columns.values
        try:
            for (idx, row) in df.iterrows():
                kwargs={}
                for column_in_file in columns:
                    for item_in_map in mapped_columns:
                        if item_in_map['file_column'] == column_in_file:
                            if item_in_map['file_column'].lower() != 'ignore' and item_in_map['model_column'].lower() != 'ignore':
                                if foreign_key_map_stored_map is not None:
                                    for obj in foreign_key_map_stored_map:
                                        if item_in_map['model_column'] in obj.keys():
                                            field_name = str(item_in_map['model_column'])
                                            foreign_field_of_the_model = self.__model._meta.get_field(field_name).remote_field.model
                                            kwargs_1 = {}
                                            kwargs_1[obj[field_name]] = row.loc[item_in_map['file_column']]
                                            foreign_field_of_the_model_object = foreign_field_of_the_model.objects.filter(**kwargs_1).first()
                                            # if foreign_field_of_the_model_object is None:
                                            #     msg = f'No entry found named {row.loc[item_in_map["file_column"]]} in {field_name} model. Please create at least one object with this name to make reference.'
                                            #     self.__raise_exceptions(**{'msg':msg})
                                            kwargs[field_name] = foreign_field_of_the_model_object
                                        else:
                                            kwargs[item_in_map['model_column']] = row.loc[item_in_map['file_column']]
                                else:
                                    kwargs[item_in_map['model_column']] = row.loc[item_in_map['file_column']]
                
                new_item = self.__model.objects.get_or_create(**kwargs)    
        except Exception as e:
            raise APIException('Error while parsing the file: '+str(e))
        self.__model_object_in_register_model.delete_file_input()
        return self.__successful_upload_response


    def __get_foreign_key_fields(self):
        info = []
        for field in self.__model._meta.fields:
            if field.get_internal_type() == 'ForeignKey':
                field_splitted = str(field).split('.')
                info.append(field_splitted[-1])
        return info 

    def __get_required_fields(self):
        fields = self.__model._meta.get_fields()
        required_fields = []
        # Required means `blank` is False
        for f in fields:
            # Note - if the field doesn't have a `blank` attribute it is probably
            # a ManyToOne relation (reverse foreign key), which you probably want to ignore.
            if False == getattr(f, 'blank', False) or False == getattr(f, 'null', False):
                field_splitted = str(f).split('.')
                if field_splitted[1] == str(self.__model.__name__) and field_splitted[-1] != 'id':
                    required_fields.append(field_splitted[-1])        
        return required_fields

    def __raise_exceptions(self, **kwargs):
        msg = kwargs['msg']
        raise APIException(msg)