from fabric.api import run, env, local, cd, prefix

USERNAME = 'scopyleft'
env.hosts = ['%s@ssh.alwaysdata.com' % USERNAME]
env.activate = 'source /home/%s/talengi/bin/activate' % USERNAME
env.directory = '/home/%s/www/talengi/EDMS' % USERNAME


def runserver():
    """Launching tests for the whole project."""
    runserver = 'python EDMS/manage.py runserver'
    with_local_settings = ' --settings=EDMS.settings.local'
    local(runserver + with_local_settings)


def test():
    """Launching tests for the whole project."""
    runtests = 'coverage run EDMS/manage.py test'
    with_test_settings = ' --settings=EDMS.settings.test'
    local(runtests + with_test_settings)


def deploy():
    """Deploying the project against AlwaysData's staging."""
    with cd(env.directory):
        run('git pull')
        with prefix(env.activate):
            collectstatic = 'python manage.py collectstatic --noinput'
            syncdb = 'python manage.py syncdb --noinput'
            with_production_settings = ' --settings=EDMS.settings.production'
            run(collectstatic + with_production_settings)
            run(syncdb + with_production_settings)


def log(filename="admin/log/access.log", backlog='F'):
    """Displays access.log file."""
    run("tail -%s '%s'" % (backlog, filename))


def errors(backlog=200):
    """Displays error.log file."""
    return log("admin/log/error.log", backlog)
