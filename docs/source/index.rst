|project|
=========

Installation
------------

Installing with `pip`
^^^^^^^^^^^^^^^^^^^^^

Requires Python 3.8+.

.. code:: sh

   pip install VWS-CLI

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

Reference
---------

.. toctree::
   :maxdepth: 3

   commands
   contributing
   release-process
   changelog

