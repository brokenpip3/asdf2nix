import re
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import List
from typing import Optional

import requests
import typer
from typing_extensions import Annotated


@dataclass
class Tool:
    name: str
    version: str
    revision: Optional[str] = None


asf2nix_version = "0.1.0"
app = typer.Typer()
nix_packages_api = "https://api.history.nix-packages.com/packages"


def get_revision(tool: Tool) -> Optional[Tool]:
    # First, try to fetch the specific version directly
    specific_version_url = f"{nix_packages_api}/{tool.name}/{tool.version}"
    response = requests.get(specific_version_url)
    if response.status_code == 200 and response.json() != {}:
        data = response.json()
        revision = data.get("revision")
        if revision is not None:
            return Tool(name=tool.name, version=tool.version, revision=revision)
    elif response.json() == {}:
        url = f"{nix_packages_api}/{tool.name}"
        response = requests.get(url)
        if response.status_code == 200:
            releases = response.json()
            for release in releases:
                compare, result_version = compare_versions(
                    release["version"], tool.version
                )
                if compare:
                    return Tool(
                        name=tool.name,
                        version=result_version,
                        revision=(release.get("revision")),
                    )
            raise ValueError(
                f"Warning: version {tool.version} not found for package {tool.name}."
            )
    else:
        raise ValueError(
            f"Error: failed to fetch data for package {tool.name}. Status code: {response.status_code}"
        )


def compare_versions(version1: str, version2: str) -> tuple[bool, str]:
    major1, minor1, patch1 = map(int, re.split(r"[.-]", version1)[:3])
    major2, minor2, patch2 = map(int, re.split(r"[.-]", version2)[:3])
    if major1 == major2 and minor1 == minor2:
        if patch1 != patch2:
            warn = f"The patch version is different: {version2} vs {version1}, using {patch1}."
            warnings.warn(warn, UserWarning)
            return True, version1
        else:
            return True, version2
    else:
        return False, ""


def generate_flake_from_tools_version(tools: List[Tool]) -> str:
    system = "${system}"
    flake_content = """
{
  description = "A flake with devshell generated from .tools-version";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
"""

    for tool in tools:
        _version = re.sub(r"[.-]", "_", tool.version)
        flake_content += (
            f"    {tool.name}_{_version}.url = github:NixOS/nixpkgs/{tool.revision};\n"
        )

    flake_content += """
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
"""

    for tool in tools:
        _version = re.sub(r"[.-]", "_", tool.version)
        flake_content += f"        {tool.name} = inputs.{tool.name}_{_version}.legacyPackages.{system}.{tool.name};\n"

    flake_content += """
      in
        {
          devShells.default = pkgs.mkShell {
            packages = [
"""

    for tool in tools:
        flake_content += f"              {tool.name}\n"

    flake_content += """
            ];
          };
      }
    );
}
"""

    return flake_content


@app.command()
def flake(
    file: Annotated[Optional[str], typer.Argument(help=".tool-versions file")] = None
) -> str:
    """
    Generate a flake from .tool-versions file.

    You can optional pass an argument to specify the path to the .tool-versions file.
    """
    if file is None:
        file = Path.cwd() / ".tool-versions"
    try:
        with open(file, "r") as file:
            tools_lines = file.readlines()
    except FileNotFoundError:
        typer.echo(f"File {file} not found.")
        raise typer.Exit(code=1)

    tools = []
    for line in tools_lines:
        name, version = line.strip("").split()
        tool = Tool(name=name, version=version)
        try:
            revised_tool = get_revision(tool)
            if revised_tool:
                tools.append(revised_tool)
        except ValueError as err:
            typer.echo(err)

    flake_content = generate_flake_from_tools_version(tools)
    typer.echo(flake_content)


@app.command()
def version() -> str:
    """
    Show the version of asdf2nix.
    """
    typer.echo(f"asdf2nix version: {asf2nix_version}")


if __name__ == "__main__":
    app()
