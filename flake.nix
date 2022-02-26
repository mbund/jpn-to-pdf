{
  description = "Jupyter notebook + PDF generator";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    poetry2nix.url = "github:nix-community/poetry2nix";
    flake-utils.url = "github:numtide/flake-utils";
    flake-compat = { url = "github:edolstra/flake-compat"; flake = false; };
  };

  outputs = { self, nixpkgs, poetry2nix, flake-utils, ... }:
    flake-utils.lib.eachSystem
      (with flake-utils.lib.system; [
        x86_64-linux

      ])
      (system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [
              poetry2nix.overlay
            ];
          };

          poetryEnv = pkgs.poetry2nix.mkPoetryEnv {
            python = pkgs.python3;
            projectDir = ./.;
          };

          render-paper-drv = pkgs.writeShellApplication {
            name = "render-paper";
            runtimeInputs = with pkgs; [
              poetryEnv
              pandoc
              (texlive.combine { inherit (texlive) scheme-small lastpage; })
            ];
            text = builtins.readFile ./render-paper.sh;
          };

          packageName = "jupyter-notebook-pdf-generator";

        in
        {

          devShells.init = pkgs.mkShell {
            packages = with pkgs; [
              poetry
            ];
          };

          devShells.dev = pkgs.mkShell {
            buildInputs = with pkgs; [
            ];

            inputsFrom = [
              self.devShells.${system}.init
              poetryEnv.env
            ];

            shellHook = ''
              [ $STARSHIP_SHELL ] && exec $STARSHIP_SHELL
            '';

            CURRENT_PROJECT = packageName;
          };

          devShell = self.devShells.${system}.dev;

          defaultApp = { type = "app"; program = "${render-paper-drv}/bin/render-paper"; };

        });

}


