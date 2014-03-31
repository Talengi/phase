#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.local")

    # Let's check that the correct settings module is used
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
    if 'test' in sys.argv and not settings_module.endswith('test'):
        confirm = raw_input("""
Wow! Wow! WOW!

It looks like you are running tests, but you did'nt set the
testing settings module.

Maybe you forgot to export the correct environment variable?

    export DJANGO_SETTINGS_MODULE="core.settings.test"

Are you sure you want to continue? [y/N] """)
        if confirm != 'y':
            sys.exit()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
