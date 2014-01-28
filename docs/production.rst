Phase in production
###################

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
    apt-get install build-essential postgresql postgresql-contrib nginx git

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

Phase installation
------------------

::

    cd
    mkvirtualenv phase
    git clone https://github.com/Talengi/phase.git
    cd phase
    pip install -r requirements/production.txt
