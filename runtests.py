#!/usr/bin/env python
import sys

from django.conf import settings


if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'rapidsms',
            'rapidsms.contrib.handlers',
            'django_tables2',
            'timelines',
        ),
        TEMPLATE_CONTEXT_PROCESSORS = (
            'django.contrib.auth.context_processors.auth',
            'django.core.context_processors.debug',
            'django.core.context_processors.i18n',
            'django.core.context_processors.media',
            'django.core.context_processors.static',
            'django.contrib.messages.context_processors.messages',
            'django.core.context_processors.request',
        ),
        ROOT_URLCONF='timelines.tests.urls',
        PROJECT_NAME='Timelines Test',
        SITE_ID=1,
        SECRET_KEY='this-is-just-for-tests-so-not-that-secret',
        INSTALLED_BACKENDS = {
            "message_tester": {
                "ENGINE": "rapidsms.contrib.httptester.backend",
            },
        },
        RAPIDSMS_HANDLERS = (
            'timelines.handlers.confirm.ConfirmHandler',
            'timelines.handlers.move.MoveHandler',
            'timelines.handlers.new.NewHandler',
            'timelines.handlers.quit.QuitHandler',
            'timelines.handlers.status.StatusHandler',
            'timelines.handlers.subscribe.SubscribeHandler',
            'timelines.handlers.shift.ShiftHandler',
        )
    )


from django.test.utils import get_runner


def runtests():
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    args = sys.argv[1:] or ['timelines', ]
    failures = test_runner.run_tests(args)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()

