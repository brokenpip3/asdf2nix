{
  description = "Asdf2Nix - A tool to convert asdf plugins to nix expressions";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-26.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pyproject = pkgs.lib.importTOML ./pyproject.toml;
        python = pkgs.python313;

        asdf2nix = python.pkgs.buildPythonApplication {
          pname = "asdf2nix";
          version = pyproject.tool.poetry.version;
          src = self;
          pyproject = true;
          build-system = [ python.pkgs.poetry-core ];
          propagatedBuildInputs = with python.pkgs; [
            typer
            requests
          ];
        };
      in
      {
        formatter = pkgs.nixpkgs-fmt;

        packages = {
          asdf2nix = asdf2nix;
          default = asdf2nix;
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ asdf2nix ];
          packages = with pkgs; [
            asdf2nix
            python
            python.pkgs.pytest
            poetry
            pre-commit
            ruff
            black
            go-task
          ];
          PYTHONDONTWRITEBYTECODE = 1;
        };
      });
}
