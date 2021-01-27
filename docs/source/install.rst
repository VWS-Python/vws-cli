Installation
------------

With ``pip``
~~~~~~~~~~~~

Requires Python 3.9+.

.. code:: sh

   pip install VWS-CLI

With Homebrew (macOS, Linux, WSL)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requires `Homebrew`_.

.. code:: sh

   brew tap VWS-Python/vws
   brew install vws-cli

.. _Homebrew: https://docs.brew.sh/Installation

Pre-built Linux binaries
~~~~~~~~~~~~~~~~~~~~~~~~

.. prompt:: bash
   :substitutions:

   curl --fail -L https://github.com/|github-owner|/|github-repository|/releases/download/|release|/vws -o /usr/local/bin/vws && \
   chmod +x /usr/local/bin/vws
   curl --fail -L https://github.com/|github-owner|/|github-repository|/releases/download/|release|/vuforia-cloud-reco -o /usr/local/bin/vuforia-cloud-reco && \
   chmod +x /usr/local/bin/vuforia-cloud-reco
