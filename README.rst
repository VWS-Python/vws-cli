|Build Status| |codecov| |Updates| |PyPI| |Documentation Status|

vws-cli
=======

A CLI for Vuforia.

.. contents::
   :local:

Installation
------------

With `pip`
^^^^^^^^^^

Requires Python 3.8+.

.. code:: sh

   pip install VWS-CLI

With Homebrew (macOS, Linux, WSL)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Requires `Homebrew`_.

.. code:: sh

   brew tap adamtheturtle/vws
   brew install vws-cli

.. _Homebrew: https://docs.brew.sh/Installation

Usage example
-------------

.. code:: sh

   $ vws add-target \
       --server-access-key $SERVER_ACCESS_KEY \
       --server-secret-key $SERVER_SECRET_KEY \
       --name my_image_name \
       --width 2 \
       --image ~/Documents/my_image.png \
       --application-metadata $(echo "my_metadata" | base64) \
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

See the `full documentation <https://vws-cli.readthedocs.io/en/latest>`__ for information on all available commands.


.. |Build Status| image:: https://travis-ci.com/adamtheturtle/vws-cli.svg?branch=master
   :target: https://travis-ci.com/adamtheturtle/vws-cli
.. |codecov| image:: https://codecov.io/gh/adamtheturtle/vws-cli/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/adamtheturtle/vws-cli
.. |Updates| image:: https://pyup.io/repos/github/adamtheturtle/vws-cli/shield.svg
   :target: https://pyup.io/repos/github/adamtheturtle/vws-cli/
.. |Documentation Status| image:: https://readthedocs.org/projects/vws-cli/badge/?version=latest
   :target: https://vws-cli.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. |PyPI| image:: https://badge.fury.io/py/VWS-CLI.svg
   :target: https://badge.fury.io/py/VWS-CLI
