#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "adl_lrs.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


# If no such file python then
# on terminal: sudo ln -s /usr/bin/python3 /usr/bin/python

# install serveral packages
# python3 -m pip install celery
# python3 -m pip install captcha jsonify django-cors-headers  django-defender psycopg2-binary
# isodate oauth2 pycryptodome django-recaptcha rfc3987 bcoding