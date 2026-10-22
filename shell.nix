# This file is to let "legacy" nix-shell command work in addition to `nix develop`
let
  lock = builtins.fromJSON (builtins.readFile ./flake.lock);
  flake-compat = fetchTarball {
    url = "https://github.com/edolstra/flake-compat/archive/${lock.nodes.flake-compat.locked.rev}.tar.gz";
    sha256 = lock.nodes.flake-compat.locked.narHash;
  };
  src = builtins.path {
    path = ./.;
    name = "source";
    filter =
      path: _type:
      builtins.elem (baseNameOf path) [
        "flake.nix"
        "flake.lock"
      ];
  };
in
(import flake-compat { inherit src; }).shellNix.default
