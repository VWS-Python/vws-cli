Release process
===============

Outcomes
~~~~~~~~

* A new ``git`` tag available to install.
* A new package on PyPI.
* A new Homebrew recipe available to install.
* A new Docker image on GitHub Container Registry.
* New binary assets attached to the GitHub release.
* New Winget packages available to install for ``vws`` and
  ``vuforia-cloud-reco``.

Perform a Release
~~~~~~~~~~~~~~~~~

#. `Install GitHub CLI`_.

#. Perform a release:

   .. code-block:: console
      :substitutions:

      $ gh workflow run release.yml --repo "|github-owner|/|github-repository|"

.. _Install GitHub CLI: https://cli.github.com/

WinGet for ``vumark``
~~~~~~~~~~~~~~~~~~~~~

The first WinGet PR for a new package ID must be created manually.
For ``vumark``, do this after the first release that contains
``vumark-windows.exe``, then automation can be added for subsequent releases.
This is tracked in `issue #1984 <https://github.com/VWS-Python/vws-cli/issues/1984>`_.
