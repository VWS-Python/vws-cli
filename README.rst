|Build Status| |PyPI|

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

With Nix
^^^^^^^^

Requires `Nix`_.

.. code-block:: console

   $ nix --extra-experimental-features 'nix-command flakes' run "github:VWS-Python/vws-cli" -- --help

To avoid passing ``--extra-experimental-features`` every time, `enable flakes`_ permanently.

.. _Nix: https://nixos.org/download/
.. _enable flakes: https://wiki.nixos.org/wiki/Flakes#Enabling_flakes_permanently

Or add to your flake inputs:

.. code-block:: nix

   {
     inputs.vws-cli.url = "github:VWS-Python/vws-cli";
   }

With Docker
^^^^^^^^^^^

.. code-block:: console

   $ docker run --rm "ghcr.io/vws-python/vws-cli" --help

To use ``vumark``:

.. code-block:: console

   $ docker run --rm --entrypoint vumark "ghcr.io/vws-python/vws-cli" --help

With winget (Windows)
^^^^^^^^^^^^^^^^^^^^^

Requires `winget`_.

.. code-block:: console

   $ winget install --id VWSPython.vws-cli --source winget --exact

.. _winget: https://docs.microsoft.com/windows/package-manager/winget/

Pre-built Linux binaries
^^^^^^^^^^^^^^^^^^^^^^^^

See the `full documentation`_ for details on how to install pre-built Linux binaries.

.. _full documentation: https://vws-python.github.io/vws-cli/install.html#pre-built-linux-x86-binaries

Pre-built Windows binaries
^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the Windows executables from the `latest release`_ and place them in a directory on your ``PATH``.
The filenames are:

* ``vws-windows.exe``
* ``vumark-windows.exe``

.. _latest release: https://github.com/VWS-Python/vws-cli/releases/latest

Pre-built macOS (ARM) binaries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See the `full documentation`_ for details on how to install pre-built macOS binaries.

Usage example
-------------

.. code-block:: console

   $ vws --help
   $ vumark --help

Full documentation
------------------

See the `full documentation <https://vws-python.github.io/vws-cli/>`__ for information on:

* All available commands.
* Setting up autocompletion.
* How to contribute to this project.
* Release notes.

.. |Build Status| image:: https://github.com/VWS-Python/vws-cli/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/VWS-Python/vws-cli/actions
.. |PyPI| image:: https://badge.fury.io/py/VWS-CLI.svg
   :target: https://badge.fury.io/py/VWS-CLI
.. |minimum-python-version| replace:: 3.14
