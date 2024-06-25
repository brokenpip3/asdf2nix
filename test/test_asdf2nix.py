from pathlib import Path

from typer.testing import CliRunner

from asdf2nix.asdf2nix import app
from asdf2nix.asdf2nix import asf2nix_version
from asdf2nix.asdf2nix import version

runner = CliRunner()


def test_version(capsys):
    version()
    captured = capsys.readouterr()
    assert captured.out.strip() == f"asdf2nix version: {asf2nix_version}"


def test_flake_not_found(capsys):
    result = runner.invoke(app, ["flake"])
    assert result.exit_code == 1
    assert ".tool-versions not found." in result.output


def test_flake_generation(capsys):
    with runner.isolated_filesystem():
        tool_versions = Path.cwd() / ".tool-versions"
        with open(tool_versions, "w") as file:
            file.write("terraform 1.5.2\n")
            file.write("nodejs 16.15.0\n")
        result = runner.invoke(app, ["flake"])
        assert result.exit_code == 0
        assert (
            "terraform_1_5_2.url = github:NixOS/nixpkgs/0b9be173860cd1d107169df87f1c7af0d5fac4aa;"
            in result.output
        )
        assert (
            "nodejs_16_15_0.url = github:NixOS/nixpkgs/7b7fe29819c714bb2209c971452506e78e1d1bbd;"
            in result.output
        )


def test_flake_generation_minor(capsys):
    with runner.isolated_filesystem():
        tool_versions = Path.cwd() / ".tool-versions"
        with open(tool_versions, "w") as file:
            file.write("go-task 3.34.3\n")
            file.write("terraform 1.6.4\n")
        result = runner.invoke(app, ["flake"])
        assert result.exit_code == 0
        assert (
            "go-task_3_34_1.url = github:NixOS/nixpkgs/88c9301627b0e216d6db9c5292c9109811fed576;"
            in result.output
        )
        assert (
            "terraform_1_6_4.url = github:NixOS/nixpkgs/b88a55f26d39acd3026b350657f119092a5c948b;"
            in result.output
        )
        assert (
            "terraform = inputs.terraform_1_6_4.legacyPackages.${system}.terraform;"
            in result.output
        )


def test_shell_file_not_found(capsys):
    result = runner.invoke(app, ["shell", "nonexistent_file.txt"])
    assert result.exit_code == 1
    assert "nonexistent_file.txt not found." in result.output
