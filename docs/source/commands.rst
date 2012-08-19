.. _commands:

Commands
============

In addition to django commands this programs such commands:

    * `addmising`_
    * `generatestyle`_
    * `listrepos`_
    * `scanherds`_
    * `scanlicensetext`_
    * `scannews`_
    * `scanpackages`_
    * `scanrepoinfo`_
    * `scanusedesc`_
    * `setlatestebuilds`_
    * `simplestats`_
    * `updateebuildmask`_
    * `update_stats`_
    
.. _addmising:

addmising command
--------------------

Detecting updated package is done by manifest hash. If manifest hash is changed,
package is updated.  But sometimes  may happen such situation -- when manifest 
changed and include hash of new ebuilds but new ebuilds files are not commited.
Then new hash of package would be in database, but when these ebuilds will be
added to that package, they would be not detected as updated, because manifest 
was not changed.

You could update all packages by scanning with ``--force-update`` flag, but 
this would change package update time and many other info. So for fixing such 
issues use **addmising** command.


.. _generatestyle:

generatestyle command
---------------------

This command will generate and print CSS style for package changelog. 
In most cases you don't need it.


.. _listrepos:

listrepos command
------------------

Will output list of available repositories and full path to them.

Example::

    [gentoo]                       /usr/portage
    [gentoo-haskell]               /var/lib/layman/haskell
    [sunrise]                      /var/lib/layman/sunrise
    [sabayon]                      /var/lib/layman/sabayon
    [pentoo]                       /var/lib/layman/pentoo

.. _scanherds:

scanherds command
------------------

Will scan only herds.xml data.

.. note::

   By default scanpackages allways scan herds data, so use this command if you 
   want update only herds data without packages.
   For updating herds with package use :ref:`scanpackages <scanpackages>` command.


.. _scanlicensetext:

scanlicensetext command
-----------------------

Will set license text for each license in database. Execute it when you have
licenses in database.


.. _scannews:

scannews command
----------------

Will scan package news.

.. _scanpackages:

scanpackages command
--------------------

This is main scanning command. It scan packages data.
It accept repository names as arguments.

Have following flags:
    * ``-a``, ``--all`` -- Scan all repositories
    * ``--force-update`` -- Force updating
    * ``--not-scan-herds`` -- not scan herds.xml
    * ``-r``, ``--update-repo`` -- Update repository info
    * ``--not-show-time`` -- Show time of scanning
    * ``--not-del`` -- Don't delete
    * ``--clear-cache`` -- Clear cache
    * ``--not-license-groups`` -- Not scan license groups
    * ``-h``, ``--help`` -- show this help message and exit
    * ``-v VERBOSITY``, ``--verbosity=VERBOSITY`` -- set verbosity level

Examples:

    * ``./manage.py scanpackages gentoo`` -- scan packages in main repository
    * ``./manage.py scanpackages gentoo sunrise`` -- scan packages in main repository and sunrise overlay
    * ``./manage.py scanpackages -a`` -- scan packages in all repositories
    * ``./manage.py scanpackages -a -v 0`` -- scan packages in all repositories, quiet mode


.. _scanrepoinfo:

scanrepoinfo command
--------------------

Will scan only repository metadata(not packages). Without args scan metadata in 
all repositories, with args use them as repositories names.

Have following flags:

    * ``--not-show-time`` -- Show time of scanning
    * ``--del`` -- Delete unavailable repositories


.. note::

   By default scanpackages allways scan repository data, so use this command if you 
   want update only repositories metadata without packages.
   For updating repositories metadata with packages use :ref:`scanpackages <scanpackages>` command.

.. _scanusedesc:

scanusedesc command
-------------------

Will scan use flag descriptions

.. _setlatestebuilds:

setlatestebuilds command
------------------------

Will set link to last ebuild in package model for showing some ebuild data in
package view. Should done periodically.

.. _simplestats:

simplestats command
-------------------

Will output simple repositories stats

Example::

    "Repo name"               "Packages"  "Ebuilds" "Maintainers" "Herds"
    gentoo                        15733     31805       473       143
    gentoo-haskell                  872      1203         3         4
    sunrise                         681       719         2         0
    sabayon                         430       830        61        36
    pentoo                          325       475        17         7
    

.. _updateebuildmask:
   
updateebuildmask command
------------------------

Will update mask of each ebuild.

.. _update_stats:

update_stats command
--------------------

Will update precomputed stats info in database.
