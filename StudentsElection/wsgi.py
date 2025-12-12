"""
WSGI config for StudentsElection project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StudentsElection.settings')

application = get_wsgi_application()
/*************  ✨ Smart Paste 📚  *************/
# Run the WSGI application
if __name__ == '__main__':
    import sys
    from wsgiref import run
    run(application, sys.argv[1:])
/*******  0a641373-4583-4812-bce4-7e44ca567a86  *******/it 