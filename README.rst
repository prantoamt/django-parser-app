django-parser-app
=====

parser_app has been created intending to upload XL files in a convenient manner.
This is a rest_framework based packege and is usuable in many projects.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Install django-parser-app ``pip install django-parser-app``

2. Add ``parser_app`` and it's dependencies to your ``INSTALLED_APPS`` setting like this::
    ```
    INSTALLED_APPS = [
        ...
        'parser_app',
        'rest_framework',
        'corsheaders',
    ]
    ```
3. Add SITE_URL in setting::
    ```
    SITE_URL = 'http://yoursiteurl.com'
    ```

4. Implement Django Dependancy Settings:
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



5. parser_app is a api based packege. Include it's URLconf in your project urls.py exactly like this::
    ```
    path('api/', include('parser_app.urls')),
    ```

6. Run ``python manage.py migrate`` to create the parser_app models.

7. Register your models which your want to import data using XL files in ``admin.py`` file. A demo model and it's admin.py file is given below:: 
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

8. Start the development server ``python manage.py runserver 0.0.0.0:8000`` and visit http://127.0.0.1:8000/admin/. 
After login, you will see a new model named ``RegisteredModels``. All your registered models will be listed here.

9. Visit http://github.com/prantoamt/django-parser-app/ to participate in the parser_app.