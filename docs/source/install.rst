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

Shell completion
~~~~~~~~~~~~~~~~

.. code:: sh

  ~/Documents ~> vws get-<TAB>
  get-database-summary-report        (Get a database summary report.)
  get-duplicate-targets  (Get a list of potential duplicate targets.)
  get-target-record                            (Get a target record.)
  get-target-summary-report            (Get a target summary report.)

.. tab:: Bash

   Add this to :file:`~/.bashrc`:

   .. code:: sh

      eval "$(_VWS_COMPLETE=bash_source vws)"

.. tab:: Zsh

   Add this to :file:`~/.zshrc`:

   .. code:: sh

      eval "$(_VWS_COMPLETE=zsh_source vws)"

.. tab:: Fish

   Run the following command:

   .. code:: sh

      _VWS_COMPLETE=fish_source vws > ~/.config/fish/completions/vws.fish

After modifying the shell configuration files, you need to start a new shell in order for the changes to be loaded.
