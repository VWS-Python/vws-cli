Changelog
=========

.. towncrier release notes start

2026.08.16
----------

- Drop Python 3.13 support, and update VWS Python so that the documented ``ProjectHasNoApiAccess`` result code spelling gives a friendly error message.

- Add Model Target dataset commands: ``vws create-model-target-dataset``, ``vws get-model-target-dataset-status``, ``vws wait-for-model-target-dataset-generated``, ``vws download-model-target-dataset`` and ``vws delete-model-target-dataset``.

- Add a ``vws get-database-reco-counts-report`` command, which requests a per-target recognition counts report for a month, waits for Vuforia to generate it, and writes the CSV to stdout or to a given path.

2026.02.22
----------


2026.02.15.2
------------


2026.02.15.1
------------


2026.02.15
----------


2026.02.07.2
------------


2026.02.07.1
------------


2026.02.07
----------


* Add support for installing with winget on Windows.

2026.01.25.1
------------


2026.01.25
----------


2026.01.22.3
------------


2026.01.22.2
------------


2026.01.22.1
------------


2026.01.22
----------


2025.03.10
----------

* Move documentation to GitHub Pages.

2021.10.08.0
------------

Initial release.
