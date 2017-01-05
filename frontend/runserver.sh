#!/bin/sh
cd /home/webinfret
. venv/bin/activate
cd web-inf-ret-ml
pip install -r requirements.txt --upgrade
#export DJANGO_SETTINGS_MODULE=frontend.settings_server
python manage.py collectstatic --noinput
python manage.py migrate
#TOOD: could be done beter: http://stackoverflow.com/questions/33791722/supervisor-cant-start-supervisorctl-as-root-or-user-user-is-set-in-config
exec gunicorn --name web_inf_ret --workers 2 --bind unix:/home/webinfret/web-inf-ret-ml/frontend/gunicorn.sock frontend.base.wsgi:application
