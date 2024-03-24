# asdf2nix

**asdf2nix** is a tool that converts an [asdf](https://asdf-vm.com/) `.tool-versions` file into a Nix flake or run a nix shell, simplifying the process of transitioning from asdf to Nix.

## Usage

To use **asdf2nix**, run the following command in your project root where the `.tool-versions` file is located:

```bash
nix run github:brokenpip3/asdf2nix -- <command>
```

You can also specify the file location as an argument if it's in a different directory.

**Note:** Make sure Nix is installed on your system and that flakes are enabled before using this tool.

## Commands

### Flake

```bash
nix run github:brokenpip3/asdf2nix -- flake
```

This command generates a flake based on the packages listed in the `.tool-versions` file:

```bash
$ cat .tool-versions
terraform 1.5.2
nodejs 16.15.0

$ nix run github:brokenpip3/asdf2nix -- flake

{
  description = "A flake with devshell generated from .tools-version";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    terraform_1_5_2.url = github:NixOS/nixpkgs/0b9be173860cd1d107169df87f1c7af0d5fac4aa;
    nodejs_16_15_0.url = github:NixOS/nixpkgs/7b7fe29819c714bb2209c971452506e78e1d1bbd;

  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        terraform = inputs.terraform_1_5_2.legacyPackages.${system}.terraform;
        nodejs = inputs.nodejs_16_15_0.legacyPackages.${system}.nodejs;

      in
        {
          devShells.default = pkgs.mkShell {
            packages = [
              terraform
              nodejs

            ];
          };
      }
    );
}
```

### Shell

```bash
nix run github:brokenpip3/asdf2nix -- shell
```

This command generates and executes a Nix shell based on the packages specified in the `.tool-versions` file.

```bash
$ cat .tool-versions
terraform 1.5.2
nodejs 16.15.0

$ nix run github:brokenpip3/asdf2nix -- shell
Generating shell from .tool-versions: nix shell nixpkgs/0b9be173860cd1d107169df87f1c7af0d5fac4aa#terraform nixpkgs/7b7fe29819c714bb2209c971452506e78e1d1bbd#nodejs

$ terraform version
Terraform v1.5.2
on linux_amd64
...
```

## Credits

* Special thanks to `RikudouSage` for the versions [database](https://github.com/RikudouSage/NixPackageHistoryBackend).

* This repository was initialized with:

```bash
nix flake init -t github:brokenpip3/my-flake-templates#python-poetry
```
