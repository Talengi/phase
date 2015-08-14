from fabric.api import run, env, local, cd, prefix, sudo

# Create an ssh config in ~/.ssh/config
# Host phase
#     HostName phase.testing.com
#     User phase
#
# Also add this line in /etc/sudoers on the server if you want
# the phase user to be able to restart supervisor:
# phase ALL = (root) NOPASSWD:/usr/bin/supervisorctl restart phase
# phase ALL = (root) NOPASSWD:/usr/bin/supervisorctl restart celery

USERNAME = 'phase'
VENV_HOME = '/home/%s/.virtualenvs/' % USERNAME
env.use_ssh_config = True
env.hosts = ['phase']
env.activate = 'workon phase'
env.directory = '/home/%s/phase' % USERNAME
env.sudo_prefix = 'sudo '


def runserver():
    """Runs the local Django server."""
    runserver = 'python src/manage.py runserver'
    with_local_settings = ' --settings=core.settings.local'
    local(runserver + with_local_settings)


def test(module=""):
    """Launches tests for the whole project."""
    runtests = 'coverage run src/manage.py test {module}'.format(
        module=module
    )
    with_test_settings = ' --settings=core.settings.test'
    local(runtests + with_test_settings)


def docs():
    """Generates sphinx documentation for the project."""
    local('cd docs && make clean && make html')
    local('xdg-open docs/_build/html/index.html')


def check():
    """Checks that everything is fine, useful before deploying."""
    test()
    docs()
    runserver()


def restart_webserver():
    sudo('supervisorctl restart phase', shell=False)
    sudo('supervisorctl restart celery', shell=False)


def reindex_all():
    with cd(env.directory):
        with prefix(env.activate):
            reindex = 'python src/manage.py reindex_all --noinput'
            with_production_settings = ' --settings=core.settings.production'
            run(reindex + with_production_settings)


def deploy():
    """Deploys the project against staging."""
    with cd(env.directory):
        run('git pull')
        with prefix(env.activate):
            with_production_settings = ' --settings=core.settings.production'

            run('pip install -r requirements/production.txt')

            collectstatic = 'python src/manage.py collectstatic --noinput'
            run(collectstatic + with_production_settings)

            clearcache = 'python src/manage.py clearcache'
            run(clearcache + with_production_settings)

            migrate = 'python src/manage.py migrate'
            run(migrate + with_production_settings)
    restart_webserver()


def log(filename="admin/log/access.log", backlog='F'):
    """Displays access.log file from staging."""
    run("tail -%s '%s'" % (backlog, filename))


def errors(backlog=200):
    """Displays error.log file from staging."""
    return log("admin/log/error.log", backlog)
