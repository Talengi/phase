from fabric.api import run, env, local, cd, prefix

USERNAME = 'scopyleft'
env.hosts = ['%s@ssh.alwaysdata.com' % USERNAME]
env.activate = 'source /home/%s/venvs/phase/bin/activate' % USERNAME
env.directory = '/home/%s/www/talengi/EDMS' % USERNAME


def runserver():
    """Runs the local Django server."""
    runserver = 'python EDMS/manage.py runserver'
    with_local_settings = ' --settings=core.settings.local'
    local(runserver + with_local_settings)


def test(module=""):
    """Launches tests for the whole project."""
    runtests = 'coverage run EDMS/manage.py test {module}'.format(
        module=module
    )
    with_test_settings = ' --settings=core.settings.test'
    local(runtests + with_test_settings)


def docs():
    """Generates sphinx documentation for the project."""
    local('cd docs && make clean && make html')
    local('open docs/_build/html/index.html')


def check():
    """Checks that everything is fine, useful before deploying."""
    test()
    docs()
    runserver()


def deploy(without_data=False):
    """Deploys the project against staging."""
    with cd(env.directory):
        run('git pull')
        with prefix(env.activate):
            collectstatic = 'python manage.py collectstatic --noinput'
            syncdb = 'python manage.py syncdb --noinput'
            generate = 'python manage.py generate_documents 5500'
            with_production_settings = ' --settings=core.settings.production'
            run('pip install -r ../requirements/production.txt')
            run(collectstatic + with_production_settings)
            if not without_data:
                run('rm edms.db')
                run(syncdb + with_production_settings)
                run(generate + with_production_settings)
                run('rm media/*')


def log(filename="admin/log/access.log", backlog='F'):
    """Displays access.log file from staging."""
    run("tail -%s '%s'" % (backlog, filename))


def errors(backlog=200):
    """Displays error.log file from staging."""
    return log("admin/log/error.log", backlog)
