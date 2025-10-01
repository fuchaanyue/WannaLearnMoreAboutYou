@echo off
set DJANGO_SETTINGS_MODULE=wannalearnmoreaboutyou.settings
set SECRET_KEY=your-test-secret-key
set DEBUG=True
set ALLOWED_HOSTS=localhost,127.0.0.1
set QUIZ_ANSWER=test
set PYTHONPATH=.
cd wannalearnmoreaboutyou
python manage.py runserver