|Build Status| |codecov| |PyPI|

vws-cli
=======

A CLI for `Vuforia Web Services`_.

.. _Vuforia Web Services: https://developer.vuforia.com/library/web-api/cloud-targets-web-services-api

.. contents::
   :local:

Installation
------------

With ``pip``
^^^^^^^^^^^^

Requires Python |minimum-python-version|\+.

.. code-block:: console

   $ pip install VWS-CLI

With Homebrew (macOS, Linux, WSL)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Requires `Homebrew`_.

.. code-block:: console

   $ brew tap VWS-Python/vws
   $ brew install vws-cli

.. _Homebrew: https://docs.brew.sh/Installation

Pre-built Linux binaries
^^^^^^^^^^^^^^^^^^^^^^^^

See the `full documentation`_ for details on how to install pre-built Linux binaries.

.. _full documentation: https://vws-python.github.io/vws-cli/install.html#pre-built-linux-x86-binaries

Usage example
-------------

.. skip doccmd[shellcheck]: next

.. code-block:: console

   $ vws add-target \
       --server-access-key "$SERVER_ACCESS_KEY" \
       --server-secret-key "$SERVER_SECRET_KEY" \
       --name my_image_name \
       --width 2 \
       --image ~/Documents/my_image.png \
       --application-metadata "$(echo 'my_metadata' | base64)" \
       --active-flag true
   03b99df0-78cf-4b01-b929-f1860d4f8ed1
   $ vws --help
   ...
   $ vuforia-cloud-reco my_image.jpg \
       --max-num-results 5 \
       --include-target-data none
   - target_id: b60f60121d37418eb1de123c381b2af9
   - target_id: e3a6e1a216ad4df3aaae1f6dd309c800
   $

Full documentation
------------------

See the `full documentation <https://vws-python.github.io/vws-cli/>`__ for information on:

* All available commands.
* Setting up autocompletion.
* How to contribute to this project.
* Release notes.

.. |Build Status| image:: https://github.com/VWS-Python/vws-cli/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/VWS-Python/vws-cli/actions
.. |codecov| image:: https://codecov.io/gh/VWS-Python/vws-cli/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/VWS-Python/vws-cli
.. |PyPI| image:: https://badge.fury.io/py/VWS-CLI.svg
   :target: https://badge.fury.io/py/VWS-CLI
.. |minimum-python-version| replace:: 3.13
