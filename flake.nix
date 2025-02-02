{
  description = "Application packaged using poetry2nix";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
      in
      {
        # nix fmt formatter
        formatter = nixpkgs.legacyPackages.${system}.nixpkgs-fmt;

        packages = {
          asdf2nix = mkPoetryApplication {
            python = pkgs.python3;
            projectDir = self;
          };
          default = self.packages.${system}.asdf2nix;
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ self.packages.${system}.asdf2nix ];
          packages = with pkgs; [
            python3
            poetry
            pre-commit
            ruff
            black
          ];
          PYTHONDONTWRITEBYTECODE = 1;
        };
      });
}
