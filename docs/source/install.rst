Installation
------------

With ``pip``
~~~~~~~~~~~~

Requires Python |minimum-python-version|\+.

.. code-block:: console

   $ pip install VWS-CLI

With Homebrew (macOS, Linux, WSL)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requires `Homebrew`_.

.. code-block:: console

   $ brew tap VWS-Python/vws
   $ brew install vws-cli

.. _Homebrew: https://docs.brew.sh/Installation

With Nix
~~~~~~~~

Requires Nix_.

.. code-block:: console
   :substitutions:

   $ nix --extra-experimental-features 'nix-command flakes' develop "github:|github-owner|/|github-repository|"

To avoid passing ``--extra-experimental-features`` every time, `enable flakes`_ permanently.

.. _Nix: https://nixos.org/download/
.. _enable flakes: https://wiki.nixos.org/wiki/Flakes#Enabling_flakes_permanently

Or add to your flake inputs:

.. code-block:: nix
   :substitutions:

   {
     inputs.vws-cli.url = "github:|github-owner|/|github-repository|";
   }

With Docker
~~~~~~~~~~~

.. code-block:: console

   $ docker run --rm ghcr.io/vws-python/vws-cli --help

To use ``vuforia-cloud-reco``:

.. code-block:: console

   $ docker run --rm --entrypoint vuforia-cloud-reco ghcr.io/vws-python/vws-cli --help

Pre-built Linux (x86) binaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console
   :substitutions:

   $ curl --fail -L "https://github.com/|github-owner|/|github-repository|/releases/download/|release|/vws-linux" -o /usr/local/bin/vws &&
       chmod +x /usr/local/bin/vws
   $ curl --fail -L "https://github.com/|github-owner|/|github-repository|/releases/download/|release|/vuforia-cloud-reco-linux" -o /usr/local/bin/vuforia-cloud-reco &&
       chmod +x /usr/local/bin/vuforia-cloud-reco

Shell completion
~~~~~~~~~~~~~~~~

Use :kbd:`<TAB>` to complete commands and options.

.. skip doccmd[shellcheck]: next
.. skip doccmd[shfmt]: next

.. code-block:: console

   $ vws get-`TAB`
   get-database-summary-report        (Get a database summary report.)
   get-duplicate-targets  (Get a list of potential duplicate targets.)
   get-target-record                            (Get a target record.)
   get-target-summary-report            (Get a target summary report.)

.. tab:: Bash

   Add this to :file:`~/.bashrc`:

   .. code-block:: console

      $ eval "$(_VWS_COMPLETE=bash_source vws)"

.. tab:: Zsh

   Add this to :file:`~/.zshrc`:

   .. code-block:: console

      $ eval "$(_VWS_COMPLETE=zsh_source vws)"

.. tab:: Fish

   Run the following command:

   .. code-block:: console

      $ _VWS_COMPLETE=fish_source vws > ~/.config/fish/completions/vws.fish

After modifying the shell configuration files, you need to start a new shell in order for the changes to be loaded.
