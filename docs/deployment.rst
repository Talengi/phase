Phase deployment
################

Phase is designed to be a lightweight alternative to traditional bloated and slow
DMS. Hence a Phase instance can be run on a single virtual machine.

A single dedicated server can host several environments (pre-production,
production).

Hosting Phase on a dedicated server
-----------------------------------

If you choose to manage your own dedicated server, you can use
`OpenVZ containers <http://openvz.org>`_ to contain different Phase installations.

Follow the `OpenVZ installation instructions <http://openvz.org/Installation_on_Debian>`_.

Server installation
-------------------

If you created an OpenVZ container from the debian wheezy template, you need to
install the following packages::

    apt-get update
    apt-get upgrade
    apt-get purge apache2
    apt-get install build-essential libpq-dev python-dev
    apt-get install postgresql postgresql-contrib nginx git supervisor rabbitmq-server

NodeJS installation
-------------------

Some tools used in Phase require a node.js installation. Get the `latest
version url on the Node.js site <http://nodejs.org/dist/v0.10.25/node-v0.10.25.tar.gz>`_.
Let's install it::

    cd /opt/
    wget http://nodejs.org/dist/latest/node-v0.10.25.tar.gz
    tar -zvxf node-v0.10.25.tar.gz
    cd node-v0.10.25
    ./configure
    make
    make install


Database creation
-----------------

::

    su - postgres
    createuser -P

        Enter name of role to add: phase
        Enter password for new role: phase
        Enter it again: phase
        Shall the new role be a superuser? (y/n) n
        Shall the new role be allowed to create databases? (y/n) n
        Shall the new role be allowed to create more new roles? (y/n) n

    createdb --owner phase phase


Python configuration
--------------------

Install pip and virtualenv::

    cd
    wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
    python get-pip.py
    pip install virtualenv virtualenvwrapper

Create user::

    adduser phase --disabled-password
    su - phase

Add those lines in the ``~/.profile`` file::

    export WORKON_HOME=~/.virtualenvs
    mkdir -p $WORKON_HOME
    source `which virtualenvwrapper.sh`

Then::

    source ~.profile


Elasticsearch configuration
---------------------------

Phase uses `Elasticsearch <http://www.elasticsearch.org/>`_ to index documents
and provides search features.

The default Elasticsearch installation is enough, but remember that ES listens
on 0.0.0.0 by default, which can be inconveniant.

To limit ES connections to localhost, one can update the config file
``/etc/elasticsearch/elasticsearch.yml`` as is:

    …
    network.host: 127.0.0.1
    …

You also need to make sure that your virtual machine has enough memory
available.

Phase installation
------------------

As root::

    npm install -g cssmin uglify-js

As phase user::

    cd
    mkvirtualenv phase
    git clone https://github.com/Talengi/phase.git
    cd phase/src
    pip install -r ../requirements/production.txt
    export DJANGO_SETTINGS_MODULE=core.settings.production
    python manage.py collectstatic
    python manage.py syncdb

Web server configuration
------------------------

If you don't host any other site on the same server, you can replace nginx's
default virtual host in */etc/nginx/sites-available/default*::

    server {
            listen 80 default_server;
            return 444;
    }

Create the Phase configuration file in ``/etc/nginx/sites-available/phase``.
Here is a working sample.

.. literalinclude:: nginx_example

Then create a link to enable it::

    ln -s /etc/nginx/sites-available/phase /etc/nginx/sites-enabled/

Don't forget to restart nginx::

    /etc/init.d/nginx restart

Running the application
-----------------------

`Gunicorn <http://gunicorn.org/>`_ is the recommanded WSGI HTTP server to run Phase.
`Supervisor <http://supervisord.org/>`_ will be used to monitor it.

Create the ``/etc/supervisor/conf.d/phase.conf`` config file. here is a working sample.

.. literalinclude:: supervisor_example

Phase uses celery as a task queue. Here is the corresponding supervisor file.

.. literalinclude:: supervisor_celery

Run this thing with::

    supervisorctl reread
    supervisorctl reload
