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
}
