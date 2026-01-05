{
  pkgs,
  lib,
  config,
  inputs,
  ...
}:
let
  pkgs-unstable = import inputs.nixpkgs-unstable { system = pkgs.stdenv.system; };
in
{
  packages = [
    pkgs.gitFull
    pkgs.gnumake
    pkgs.libmysqlclient
    pkgs-unstable.opencode
    pkgs.nixd
  ];

  languages.nix.enable = true;

  languages.python.enable = true;
  languages.python.uv.enable = true;
  languages.python.uv.sync.enable = true;
  languages.python.uv.sync.allGroups = true;
  languages.python.venv.enable = true;

  git-hooks.hooks = {
    black.enable = true;
    flake8.enable = true;
    isort.enable = true;
    pyright.enable = false;
    python-debug-statements.enable = true;
    check-shebang-scripts-are-executable.enable = true;
    check-symlinks.enable = true;
    check-yaml.enable = true;
    check-merge-conflicts.enable = true;
    check-json.enable = true;
    check-executables-have-shebangs.enable = true;
    check-added-large-files.enable = true;
    check-case-conflicts.enable = true;
    markdownlint.enable = true;
    nixfmt-rfc-style.enable = true;
    prettier.enable = true;
    trufflehog.enable = true;
  };

  git-hooks.hooks.djlint = {
    enable = true;
    package = pkgs.djlint;
    args = [ "--reformat" ];
    entry = "python -m djlint";
    types = [ "html" ];
  };

  devcontainer.enable = true;
}
