from django.conf import settings
from django.core.exceptions import ValidationError


if hasattr(settings, 'SITE_URL'):
    pass
else:
    raise ValidationError("Please define your site url inside settings.py file like this: SITE_URL=http://yoursiteurl.com. It is a requirement for dataparser.")