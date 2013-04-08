from fabric.api import run, env, local, cd, prefix

USERNAME = 'scopyleft'
env.hosts = ['%s@ssh.alwaysdata.com' % USERNAME]
env.activate = 'source /home/%s/talengi/bin/activate' % USERNAME
env.directory = '/home/%s/www/talengi/EDMS' % USERNAME


def runserver():
    """Launching tests for the whole project."""
    runserver = 'python EDMS/manage.py runserver'
    local(runserver + ' --settings=EDMS.settings.local')


def test():
    """Launching tests for the whole project."""
    runtests = 'coverage run EDMS/manage.py test'
    local(runtests + ' --settings=EDMS.settings.test')


def deploy():
    """Deploying the project against AlwaysData's staging."""
    with cd(env.directory):
        run('git pull')
        with prefix(env.activate):
            collectstatic = 'python manage.py collectstatic --noinput'
            run(collectstatic + ' --settings=EDMS.settings.production')


def log(filename="admin/log/access.log", backlog='F'):
    """Displays access.log file."""
    run("tail -%s '%s'" % (backlog, filename))


def errors(backlog=200):
    """Displays error.log file."""
    return log("admin/log/error.log", backlog)
