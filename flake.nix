{
  description = "A CLI for the Vuforia Web Services (VWS) API";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
      ...
    }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs lib.systems.flakeExposed;

      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

      overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel";
      };

      # Read version from VERSION file, fall back to commit hash for dev builds
      version =
        let
          versionFile = ./VERSION;
        in
        if builtins.pathExists versionFile then
          lib.strings.trim (builtins.readFile versionFile)
        else
          "0.0.0+${self.shortRev or self.dirtyShortRev or "unknown"}";

      # Override vws-cli to set the version
      vwsCliOverlay = final: prev: {
        vws-cli = prev.vws-cli.overrideAttrs (old: {
          env = (old.env or { }) // {
            SETUPTOOLS_SCM_PRETEND_VERSION = version;
          };
        });
      };

      pythonSets = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          # Get Python version from .python-version file and map to nixpkgs attribute
          pythonVersionFile = builtins.readFile ./.python-version;
          pythonVersion = builtins.replaceStrings [ "." "\n" ] [ "" "" ] pythonVersionFile;
          pythonAttr = "python${pythonVersion}";
          python = pkgs.${pythonAttr};
        in
        (pkgs.callPackage pyproject-nix.build.packages {
          inherit python;
        }).overrideScope
          (
            lib.composeManyExtensions [
              pyproject-build-systems.overlays.wheel
              overlay
              vwsCliOverlay
            ]
          )
      );

    in
    {
      packages = forAllSystems (
        system:
        let
          pythonSet = pythonSets.${system};
          virtualenv = pythonSet.mkVirtualEnv "vws-cli-env" workspace.deps.default;
        in
        {
          default = virtualenv;
          vws-cli = virtualenv;
        }
      );

      apps = forAllSystems (system: {
        default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/vws";
        };
        vws = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/vws";
        };
        vuforia-cloud-reco = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/vuforia-cloud-reco";
        };
      });

      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonSet = pythonSets.${system};
          virtualenv = pythonSet.mkVirtualEnv "vws-cli-dev-env" workspace.deps.all;
        in
        {
          default = pkgs.mkShell {
            packages = [
              virtualenv
              pkgs.uv
            ];
            env = {
              UV_NO_SYNC = "1";
              UV_PYTHON = pythonSet.python.interpreter;
              UV_PYTHON_DOWNLOADS = "never";
            };
            shellHook = ''
              unset PYTHONPATH
            '';
          };
        }
      );

      checks = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          vws-cli-smoke = pkgs.runCommand "vws-cli-smoke-test" { } ''
            ${self.packages.${system}.default}/bin/vws --help > $out
          '';
        }
      );
    };
}
