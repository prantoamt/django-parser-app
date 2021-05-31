django-parser-app
=================

parser_app has been created intending to upload Excel files in a convenient manner.
This is a rest_framework based packege and is usuable in many projects.

Detailed documentation is in the "docs" directory.

##### Table of Contents  
----------------------------------------------------------------
- [Quick start](#quick-start)
    + [Install the App](#install-the-app)
    + [Configure Project](#configure-project)
    + [Register Models](#register-models)
      - [models.py](#modelspy)
      - [admin.py](#adminpy)
    + [Run Project](#run-project)
  * [Import data through Django admin panel](#import-data-through-django-admin-panel)

<small>*Feel free to contribute in the ``parser_app``. Your contributions are always appreciated!*</small>


# Quick start
-----------
### Install the app
------------------------
1. Install django-parser-app ``pip install django-parser-app``

### Configure Project
----------------------
1. Add ``parser_app`` and it's dependencies to your ``INSTALLED_APPS`` setting like this::
    ```
    INSTALLED_APPS = [
        ...
        'parser_app',
        'rest_framework',
        'corsheaders',
    ]
    ```
2. Add SITE_URL in setting::
    ```
    SITE_URL = 'http://yoursiteurl.com'
    ```

3. Implement Django Dependancy Settings:
    - [Django Rest Framework](http://www.django-rest-framework.org/)
    - [Django Cors Headers](https://github.com/ottoyiu/django-cors-headers)

    Such as:
    ```
    MIDDLEWARE = [
        ...
        'django.contrib.sessions.middleware.SessionMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        ...
    ]

    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
            'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        ),
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.SessionAuthentication',
        ),
    }

    CORS_ORIGIN_ALLOW_ALL = True
    ```



4. parser_app is a api based packege. Include it's URLconf in your project urls.py exactly like below::
    ```
    path('api/', include('parser_app.urls')),
    ```

5. Run ``python manage.py migrate`` to create the parser_app models.

### Register Models
-------------------

1. Register your models in ``admin.py`` file. A demo model and it's admin.py file is given below:: 
    #### models.py
    ```
    class Area(models.Model):
        code = models.IntegerField(
            null=False, blank=False, unique=True, verbose_name="Location Code", db_column='Code', default=0)
        name = models.CharField(null=False, blank=False,
                                max_length=50, db_column='Name', default='')
        location_type = models.CharField(
            choices=LOCATION_TYPE, default='', max_length=20, verbose_name="Location type", db_column='LocationType')
        parent_code = models.IntegerField(null=True, blank=True, default=0, verbose_name="Parent Code", db_column='ParentCode')
        class Meta:
            verbose_name_plural = "Area"

        def __str__(self):
            return str(self.code)
    ```
    #### admin.py
    ```
    from django.contrib import admin

    # Register your models here.
    from .models import Area
    from parser_app.parser import DataParser

    DataParser.register_model(Area)
    ```  
### Run Project
---------------
1. Start the development server ``python manage.py runserver 0.0.0.0:8000`` and visit http://yoursiteurl:8000/admin/. 
After logging in, you will see a new model named ``Registered Models`` under ``parser_app`` section. All your registered models will be listed here.

## Import data through Django admin panel
------------------------------------------

<img src="https://github.com/prantoamt/django-parser-app/blob/main/images/upload_via_admin_panel.gif" width="100%" height="300"/>

1. Click on the ``Registred Models`` that is located inside ``parser_app`` section.
2. You will see the ``Area`` model listed there.
3. Select the check box and then click on the django admin action panel.
4. Select ``import with parser app`` and click on ``go``.
5. Select your desired Excel file and submit.
6. In the next step, you will be given the model's columns and the columns available in the Excel file.
7. Map the columns to specify which column of the Excel file means which column of the Model and then submit.
8. You will the shown the estimated data type validation errors in the next step. For example, your model field accept ``int`` value but your file contains ``string``.
9. If no validation errors are found, you will be asked to confirm upload.
10. After confirmation, your data wil be imported in the desired model (in case of this example, ``Area`` model).

