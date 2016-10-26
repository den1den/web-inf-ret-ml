#!/bin/sh
cd /home/webinfret
. venv/bin/activate
cd web-inf-ret-ml
pip install -r requirements.txt --upgrade
cd frontend
#export DJANGO_SETTINGS_MODULE=frontend.settings_server
python manage.py collectstatic --noinput
exec gunicorn --name web_inf_ret --workers 1 --bind unix:/home/webinfret/web-inf-ret-ml/frontend/gunicorn.sock frontend.wsgi:application
