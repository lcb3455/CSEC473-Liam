#Liam Best
#lcb3455
import argparse
import os
import subprocess
import tarfile
from pathlib import Path

PAM_BASE_URL = "https://github.com/linux-pam/linux-pam/releases/downloads/v{version}"

def show_help():
    print("")
    print("Example usage: script.py -v 1.3.0 -p some_s3cr3t_p455word")
    print("For a list of supported versions: https://github.com/linux-pam/linux-pam/releases")

def run_cmd(cmd, cwd=None):
    print(f"[+] Running: {' '.join(cmd)} (cwd={cwd or os.getcwd()})")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result

def download_file(url, dest):
    print(f"[+] Downloading {url} -> {dest}")
    run_cmd(["wget", "-c", url])

def try_download(version):
    # tar.gz format
    # pam_dir = f"linux-pam-{version}"
    pam_file = f"Linux-PAM-{version}.tar.gz"
    url = f"{PAM_BASE_URL}/{pam_file}"
    try:
        download_file(url, pam_file)
        pam_dir = f"Linux-PAM-{version}"
        return pam_dir, pam_file
    except RuntimeError:
        print("tar.gz no work :( ")

    # tar.xz format
    # pam_dir = f"linux-pam-Linux-PAM-{version}"
    pam_file = f"Linux-PAM-{version}.tar.xz"
    url = f"{PAM_BASE_URL}/{pam_file}"
    try:
        download_file(url, pam_file)
        pam_dir = f"Linux-PAM-{version}"
        return pam_dir, pam_file
    except RuntimeError:
        print("well thats not good uhhhh tar.xz no work gg")

def extract_tarball(pam_file: str):
    print(f"[+] Extracting {pam_file}")
    with tarfile.open(pam_file, "r:gz") as tar:
        tar.extractall()

def build_pam(pam_dir: str):
    pam_path = Path(pam_dir)
    if not pam_path.exists():
        raise FileNotFoundError(f"{pam_dir} does not exist after extraction")

    # If ./configure does not exist, run ./autogen.sh
    configure_path = pam_path / "configure"
    if not configure_path.exists():
        print("[+] ./configure not found, running ./autogen.sh")
        run_cmd(["./autogen.sh"], cwd=str(pam_path))

    print("[+] Running ./configure")
    run_cmd(["./configure"], cwd=str(pam_path))

    print("[+] Running make")
    run_cmd(["make"], cwd=str(pam_path))

    print("[+] Build complete (no patching performed).")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", action="store_true")
    parser.add_argument("-?", dest="qmark", action="store_true")
    parser.add_argument("-v", dest="pam_version")
    parser.add_argument("-p", dest="password")

    args, unknown = parser.parse_known_args()

    if args.h or args.qmark:
        show_help()
        return

    if not args.pam_version:
        print("[!] PAM version is required.")
        show_help()
        raise SystemExit(1)

    if not args.password:
        print("[!] Password is required (treated as plain input here, no patching).")
        show_help()
        raise SystemExit(1)

    pam_version = args.pam_version
    password = args.password  # Not used for any modification here

    print("Automatic PAM Workflow (safe, no backdoor)")
    print(f"PAM Version: {pam_version}")
    print(f"Password (unused in this safe version): {password}")
    print("")

    # Check for 'patch' just like the original, but only to mirror behavior
    result = subprocess.run(["which", "patch"])
    if result.returncode != 0:
        print("Error: patch command not found. Exiting (mirroring original script behavior)...")
        raise SystemExit(1)

    pam_dir, pam_file = try_download_variants(pam_version)
    extract_tarball(pam_file)
    build_pam(pam_dir)

    print("")
    print("No backdoor created. This script only:")
    print("- parsed arguments")
    print("- downloaded the PAM source")
    print("- extracted it")
    print("- optionally built it")
    print("You now have a clean PAM source/build tree for analysis or defensive work.")

if __name__ == "__main__":
    main()
