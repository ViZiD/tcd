{
  description = "NixOS flake for poetry project";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
    utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      poetry2nix,
      utils,
    }:
    utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ poetry2nix.overlays.default ];
        };
        p2n = import poetry2nix { inherit pkgs; };

        overrides = p2n.defaultPoetryOverrides.extend (
          self: super: {
            types-tgcrypto = super.types-tgcrypto.overridePythonAttrs (old: {
              buildInputs = old.buildInputs or [ ] ++ [ super.setuptools ];
            });
            pyqt5-qt5 = super.pyqt5-qt5.overridePythonAttrs (old: {
              buildInputs = old.buildInputs or [ ] ++ [ pkgs.libsForQt5.qt5.qtlottie ];
              preFixup = ''
                patchelf --replace-needed libtiff.so.5 libtiff.so $out/${self.python.sitePackages}/PyQt5/Qt5/plugins/imageformats/libqtiff.so
              '';
            });
            pyqt5 = super.pyqt5.override { preferWheel = true; };
            ruff = super.ruff.override { preferWheel = true; };

          }
        );

        python = pkgs.python312;

        pythonEnv = p2n.mkPoetryEnv {
          projectDir = self;
          editablePackageSources = {
            tcd = "tcd";
          };
          python = python;
          overrides = overrides;
        };
        pythonApp = p2n.mkPoetryApplication {
          projectDir = self;
          python = python;
          overrides = overrides;
          meta = with pkgs.lib; {
            description = "tool for decrypted telegram desktop media cache";
            homepage = "https://github.com/ViZiD/tcd";
            license = licenses.mit;
            maintainers = with maintainers; [ vizid ];
          };
        };
      in
      rec {
        packages.default = pythonApp;

        defaultPackage = packages.default;

        apps.default = {
          type = "app";
          program = "${self.defaultPackage."${system}"}/bin/tcd";
        };

        defaultApp = apps.default;

        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.poetry
          ];
        };
      }
    );
}
