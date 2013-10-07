RapidSMS timelines
========================

rapidsms-timelines is a reusable RapidSMS application for sending appointment
reminders. Users can be subscribed to a timeline of milestones for future timelines. Reminders
are send to the patient or staff to remind them of the appointment. timelines
can be confirmed or rescheduled by patient or staff. It also tracks the history of confirmed
notifications and missed/made timelines.

To migrate an existing rapidsms-appointments app, be sure to backup data with
natural keys::
    python manage.py dumpdata appointments --natural --indent=4 1> appointments_backup.json


And then rename tables::
    https://gist.github.com/jamesmfriedman/6168003


.. image::
    https://secure.travis-ci.org/ewheeler/rapidsms-timelines.png?branch=master
    :alt: Build Status
        :target: https://secure.travis-ci.org/ewheeler/rapidsms-timelines


Dependencies
-----------------------------------

rapidsms-timelines currently runs on Python 2.6 and 2.7 and requires the following
Python packages:

- Django >= 1.3
- RapidSMS >= 0.11.0
- Celery >= 3.0.13


Documentation
-----------------------------------

Documentation on using rapidsms-timelines is available on
`Read The Docs <http://readthedocs.org/docs/rapidsms-timelines/>`_.


Translations
-----------------------------------

The translations for rapidsms-appointment are managed on our
`Transifex project <https://www.transifex.com/projects/p/rapidsms-timelines/>`_.
If you are interested in translating rapidsms-timelines into your native language
you can join the project and add your language.


Running the Tests
------------------------------------

With all of the dependancies installed, you can quickly run the tests with via::

    python setup.py test

or::

    python runtests.py

To test rapidsms-appointment in multiple supported environments you can make use
of the `tox <http://tox.readthedocs.org/>`_ configuration.::

    # You must have tox installed
    pip install tox
    # Build default set of environments
    tox
    # Build a single environment
    tox -e py26-1.4.X


License
--------------------------------------

rapidsms-timelines is released under the BSD License. See the
`LICENSE <https://github.com/ewheeler/rapidsms-timelines/blob/master/LICENSE>`_ file for more details.


Contributing
--------------------------------------

If you think you've found a bug or are interested in contributing to this project
check out `rapidsms-timelines on Github <https://github.com/ewheeler/rapidsms-timelines>`_.

Development sponsored by `Caktus Consulting Group, LLC
<http://www.caktusgroup.com/services>`_.
