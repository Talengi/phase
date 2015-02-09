Transmittals upload
###################

The transmittals upload feature allows a contractor to upload a bunch of
documents into a Phase instance directly from a ftp upload.

Directory definition
--------------------

The directory must be named XXX


dir content


Server configuration
--------------------

Here are the instructions to install and configure the ftp server to activate
this feature.

Note that Phase doesn't care how the files are transmitted to the server (ftp,
ssh, nfs, etc.) so this section is for information only.

Ftp server installation and configuration
.........................................

We will use the proftpd server to handle ftp communication, and configure the
server to only accept ftps (ftp over ssl) connexions.

First, install the `proftpd` ftp server::


    aptitude install proftpd

Choose the "standalone" start method.

Create the ssl certificates for the TLS connection.

::

    openssl req -x509 -newkey rsa:1024 \
         -keyout /etc/ssl/private/proftpd.key -out /etc/ssl/certs/proftpd.crt \
         -nodes -days 365
    chmod 0600 /etc/ssl/private/proftpd.key
    chmod 0640 /etc/ssl/private/proftpd.key

Configure the server, using those examples files as starting points.

`/etc/proftpd/proftpd.conf`:

.. literalinclude:: proftpd.conf.example

`/etc/proftpd/tls.conf`:

.. literalinclude:: proftpd.tls.example

`/etc/proftpd/users.conf`:

.. literalinclude:: proftpd.users.example


User creation
.............

Let's create a unix user "test_ctr" for the contractor, and configure the
directory permissions.

::

    adduser test_ctr --disabled-password --ingroup=phase --shell=/bin/false
    chmod g+rwX /home/test_ctr
    echo "umask 002" >> /home/test_ctr/.profile

Note that for safety reasons, the list authorized users are explicitely
declared in the `/etc/proftpd/users.conf` file.
