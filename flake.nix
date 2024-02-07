{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        python_packages = with pkgs; [
          python39Packages.aiofiles
          python39Packages.pyqt5
          python39Packages.tgcrypto
        ];

        dev_packages = with pkgs; [
          python39Packages.isort
        ];

        tcd = with pkgs.python39Packages;
          buildPythonApplication rec {
            pname = "tcd";
            version = "0.1dev";
            pyproject = true;

            src = ./.;

            nativeBuildInputs = [
              setuptools
              wheel
            ];

            propagatedBuildInputs = python_packages;

            doCheck = false;

            meta = {
              description = "Decrypt telegram media cache";
              license = pkgs.lib.licenses.mit;
            };
          };
      in
      {
        packages.tcd = tcd;
        packages.default = self.packages.${system}.tcd;

        apps.tcd = {
          type = "app";
          program = "${self.packages.${system}.tcd}/bin/tcd";
        };

        apps.default = self.apps.${system}.tcd;
        defaultPackage = self.packages.${system}.tcd;

        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python39
          ] ++ python_packages ++ dev_packages;
        };
      });
}
