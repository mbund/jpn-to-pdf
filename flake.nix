{
  description = "M3C Environment set up";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in rec {
        apps.render-latex = flake-utils.lib.mkApp {
          drv = pkgs.writeShellApplication {
            name = "render-latex";
            runtimeInputs = with pkgs; [
              poetry
              pandoc
              (texlive.combine {
                inherit (texlive)
                scheme-small
                adjustbox
                caption
                collectbox
                enumitem
                environ
                eurosym
                jknapltx
                parskip
                pgf
                rsfs
                tcolorbox
                titling
                trimspaces
                ucs
                ulem
                upquote;
              })
            ];
            text = ./render-latex.sh;
          };
        };

        defaultApp = apps.render-latex;

        devShell = pkgs.mkShell {
          buildInputs = [
            # install poetry for python environment handling
            pkgs.poetry

            # install pandas separately because visual studio code runs
            # `POETRY_PYTHON_DIRECTORY/bin/python -c "import pandas;print(pandas.__version__)"`
            # to detect if pandas exists for the data viewer
            pkgs.python3Packages.pandas
          ];

          # libstdc++ is required by...jupyter probably, anyways we have to link it
          LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib/";
        };
      });
}
