{ pkgs, lib, config, inputs, ... }:

{
  packages = [ 
      pkgs.gitFull
      pkgs.gnumake
      
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
      check-shebang-scripts-are-executable.enable = true;
      check-symlinks.enable = true;
      check-yaml.enable = true;
      check-merge-conflicts.enable = true;
      check-json.enable = true;
      check-executables-have-shebangs.enable = true;
      check-added-large-files.enable = true;
      check-case-conflicts.enable = true;
      markdownlint.enable = true;
      nixpkgs-fmt.enable = true;
      prettier.enable = true;
      trufflehog.enable = true;
  };
}
