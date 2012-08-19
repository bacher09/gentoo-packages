Installation
============

First you should insall all required depences see it in Requirements.

.. literalinclude:: ../../Requirements

Next you should configure database and create ``local_settings.py`` in ``gpackages/main/`` dir, you could see ``local_settings.py.example`` as example.

.. literalinclude:: ../../gpackages/main/local_settings.py.example
   :language: python

After creating configuration you need create tables in your database, for this execute these commands::

    $ cd gpackages
    $ ./manage.py syncdb
    $ ./manage.py migrate

Then maybe you want collect first packages data, for this you need execute that command::
    
    $ ./manage.py scanpackages -a

This will collect info about all packages in all overlays.
If you want check what overlays available, then type this command::

    $ ./manage.py listrepos

After first scanning you should also add info about use flags and licenses text
You could do this with such commands::

    $ ./manage.py scanusedesc
    $ ./manage.py scanlicensetext

Now you could run demo web-server::
    
    $ ./manage.py runserver

For deployment check `django deployment docs`_.
For more commands see :ref:`commands`.

.. _`django deployment docs`: https://docs.djangoproject.com/en/1.4/howto/deployment/wsgi/modwsgi/
