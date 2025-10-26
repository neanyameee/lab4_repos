"""
WSGI config for book_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

path = 'C:/Users/User/Desktop/2 курс.1 семестр/Разработка/books_4/book_project/book_project'
if path not in sys.path:
    sys.path.append(path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_project.settings')

application = get_wsgi_application()
