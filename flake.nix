{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        # Get Python version from .python-version file and map to nixpkgs attribute
        pythonVersionFile = builtins.readFile ./.python-version;
        pythonVersion = builtins.replaceStrings [ "." "\n" ] [ "" "" ] pythonVersionFile;
        pythonAttr = "python${pythonVersion}";
        python = pkgs.${pythonAttr};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pkgs.actionlint
            pkgs.enchant
            pkgs.gh
            pkgs.git
            pkgs.jujutsu
            pkgs.nixfmt
            pkgs.nodejs_22
            pkgs.uv
            python
          ];

          shellHook = "";
        };
      }
    );
}
