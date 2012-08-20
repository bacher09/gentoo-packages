"""This is generic application for precalculation stats.

This application add ``update_stats`` command in addition to django commands. 
This command are used for updating stats in all available models.
So if you run::

    $ ./manage.py update_stats

This will update stats in all models inherited from :class:`.StatsModel`

"""
