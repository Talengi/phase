Install
=========

Steps to initialize the project on a local machine:

1. git clone https://github.com/Talengi/EDMS.git src
2. virtualenv venv
3. . venv/bin/activate
4. pip install -r src/requirements/local.txt
5. cd src
6. python EDMS/manage.py syncdb --noinput --settings=EDMS.settings.local
6. fab runserver
