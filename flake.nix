{
  description = "Library for accessing 'ar' files";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-compat = {
    url = "github:edolstra/flake-compat";
    flake = false;
  };
  inputs.shell-hooks.url = "github:vlaci/nix-shell-hooks";

  outputs =
    { nixpkgs, shell-hooks, ... }:
    let
      # nixpkgs-unstable dropped x86_64-darwin
      forAllSystems = nixpkgs.lib.genAttrs [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];
      pkgsFor =
        system:
        import nixpkgs {
          inherit system;
          overlays = [ shell-hooks.overlays.default ];
        };
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              python3
              python3Packages.uvVenvShellHook
              python3Packages.autoPatchelfVenvShellHook
              deadnix
              statix
              nodejs # for pyright
            ];
            # All Python dependencies come from the uv-managed virtualenv
            dontAddPythonPath = true;
          };
        }
      );

      formatter = forAllSystems (system: nixpkgs.legacyPackages.${system}.nixfmt);
    };
}
