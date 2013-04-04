from fabric.api import run, env, local

USERNAME = 'scopyleft'
env.hosts = ['%s@ssh.alwaysdata.com' % USERNAME]


def test():
    """Launching tests for the whole project."""
    local('coverage run EDMS/manage.py test --settings=EDMS.settings.test')


def deploy():
    """Deploying the project against AlwaysData's staging."""
    run('cd /home/%s/www/talengi/EDMS && git pull' % USERNAME)


def log(filename="admin/log/access.log", backlog='F'):
    """Displays access.log file."""
    run("tail -%s '%s'" % (backlog, filename))


def errors(backlog=200):
    """Displays error.log file."""
    return log("admin/log/error.log", backlog)
