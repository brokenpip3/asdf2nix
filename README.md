# asdf2nix

**asdf2nix** is a tool that converts an [asdf](https://asdf-vm.com/) `.tool-versions` file into a Nix flake, simplifying the process of transitioning from asdf to Nix.

## Usage

To use **asdf2nix**, run the following command in your project root where the `.tool-versions` file is located:

```bash
nix run github:brokenpip3/asdf2nix -- flake
```

You can also specify the file location as an argument if it's in a different directory.

**Note:** Make sure Nix is installed on your system and that flakes are enabled before using this tool.

## Credits

* Special thanks to `RikudouSage` for the versions [database](https://github.com/RikudouSage/NixPackageHistoryBackend).

* This repository was initialized with:

```bash
nix flake init -t github:brokenpip3/my-flake-templates#python-poetry
```
