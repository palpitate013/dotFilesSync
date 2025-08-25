# dotFilesSync
A lightweight daemon that watches user‑specified dot‑files and copies any changes into a designated Git repository. Configured via a JSON file, it handles privileged files with sudo, logs actions, runs at boot, repeats hourly, and triggers once before shutdown.

# NixOS Setup

``` nix
let
  fileSyncSrc = pkgs.fetchFromGitHub {
    owner = "yourname";
    repo = "file-sync-watcher";
    rev = "commit-or-tag-hash";     # e.g. "a1b2c3d4..."
    sha256 = "sha256-hash-goes-here";
  };
in {
  environment.systemPackages = [
    pkgs.python3
    pkgs.python3Packages.watchdog
  ];

  systemd.services.fileSync = {
    description = "File sync watcher for git repo";
    wantedBy = [ "multi-user.target" ];
    after = [ "network.target" ];

    serviceConfig = {
      ExecStart = "${pkgs.python3}/bin/python3 ${fileSyncSrc}/gitsync.py";
      Restart = "always";
      User = "root"; # root so it can read sudo-protected files
      WorkingDirectory = "/"; # run from /
    };
  };
}
```