=====
django-parser-app
=====

parser_app has been created intending to upload XL files in a convenient manner.
This is a rest_framework based packege and is usuable in many projects.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "parser_app" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'parser_app',
        'rest_framework',
        'corsheaders',
    ]

2. Add corsheaders middleware class to listen in on responses like this::

    MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
    ]

3. parser_app is a api based packege. Include it's URLconf in your project urls.py like this::

    path('api/', include('parser_app.urls')),

4. Run ``python manage.py migrate`` to create the parser_app models.

5. Start the development server and visit http://127.0.0.1:8000/admin/. 
After login, you will see a new model named ``RegisteredModels``.

5. Visit http://github.com/prantoamt/django-parser-app/ to participate in the parser_app.