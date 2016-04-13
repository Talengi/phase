Phase deployment
################

Phase is designed to be a lightweight alternative to traditional bloated and slow
DMS. Hence a Phase instance can be run on a single virtual machine.

A single dedicated server can host several environments (pre-production,
production).

Hosting Phase on a dedicated server
-----------------------------------

The recommanded settings is to install Phase in an LXC container on a debian
stable (currently Jessie) host.

Also use a jessie container::

    apt-get install lxc
    lxc-create -n <name> -t debian -- -a amd64 -r jessie

Server installation
-------------------

If you created an OpenVZ container from the debian wheezy template, you need to
install the following packages::

    apt-get purge apache2 apache2-doc apache2-mpm-prefork apache2-utils apache2.2-bin apache2.2-common
    apt-get update
    apt-get upgrade
    apt-get install build-essential libpq-dev python-dev
    apt-get install vim postgresql postgresql-contrib nginx git supervisor rabbitmq-server

NodeJS installation
-------------------

Some tools used in Phase require a node.js installation. Get the `latest
version url on the Node.js site <http://nodejs.org/dist/v0.10.25/node-v0.10.25.tar.gz>`_.
Let's install it::

    apt-get install nodejs-legacy wget curl
    wget https://www.npmjs.org/install.sh
    bash install.sh


Memcache installation
---------------------

Phase uses Memcached as a cache tool. To install pylibmc, the python memcached
backend, you need to install the libs first.

::

    aptitude install memcached libmemcached-dev


Database creation
-----------------

::

    su - postgres
    createuser -P phase

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
    workon phase
    export DJANGO_SETTINGS_MODULE=core.settings.production

Then::

    source ~/.profile


Elasticsearch configuration
---------------------------

Phase uses `Elasticsearch <http://www.elasticsearch.org/>`_ to index documents
and provides search features.

You need to install java for ES to work::

    aptitude install openjdk-7-jre

You can install ES by downloading the apt package on the elastic site::

    wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | apt-key add -
    wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.6.2.deb
    dpkg -i elasticsearch-1.6.2.deb

The default Elasticsearch installation is enough, but remember that ES listens
on 0.0.0.0 by default, which can be inconvenient.

To limit ES connections to localhost, one can update the config file
``/etc/elasticsearch/elasticsearch.yml`` as this::

    …
    network.host: 127.0.0.1
    …

You also need to make sure that your virtual machine has enough memory
available.

Also, make sure ES starts after boot::

    update-rc.d elasticsearch defaults

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
    python manage.py migrate

You can load initial testing data if you need it::

    python manage.py loaddata initial_accounts initial_values_lists initial_categories initial_documents

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


Troubleshooting
---------------

RabbitMQ won't start after installation
.......................................

If RabbitMQ fails to start after being installed, make sure the server hostname
is set in `/etc/hosts`. You can also check the exact hostname used by RabbitMQ
by getting the failure detail in `/var/log/rabbitmq/startup_log`.

No public key available
.......................

If you receive the "No public key available" upon the first `apt-get update`,
run the following command::

    apt-get install debian-keyring debian-archive-keyring

Then proceed normally.


Missing jpeg libs for Pillow
............................

When you pip install requirements, Pillow might fail to install with an error
related to jpeg management. To fix this, run this command as root::

    apt-get install libjpeg-dev
