#Liam Best
#lcb3455
import argparse
import os
import subprocess
import tarfile
from pathlib import Path

# PAM_BASE_URL = f"https://github.com/linux-pam/linux-pam/releases/download/v{version}"

def show_help():
    print("")
    print("Example usage: PAM.py -v 1.7.2 -p test")
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

def extract_tarball(pam_file):
    print(f"[+] Extracting {pam_file}")
    with tarfile.open(pam_file, "r:*") as tar:
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

    #FIGURE OUT HOW TO ACTUALLY WRITE THE PATCH

    print("[+] Running make")
    run_cmd(["make"], cwd=str(pam_path))

    print("[+] Build complete")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", action="store_true")
    # parser.add_argument("-?", dest="qmark", action="store_true")
    parser.add_argument("-v" "--version", required=True, type=str, help="PAM version")
    parser.add_argument("-p", dest="password")
    args = parser.parse_args()

    version = args.version.strip()
    password = args.password
    # args, unknown = parser.parse_known_args()

    print("Automatic PAM Workflow (testing, no backdoor yet :3)")
    print(f"PAM Version: {version}")
    print(f"Password: {password}")
    print("")

    global PAM_BASE_URL
    PAM_BASE_URL = f"https://github.com/linux-pam/linux-pam/releases/download/v{version}"

    try:
        pam_dir, pam_file = try_download(version)
    except RuntimeError as e:
        print(f"[!] downlaod no worky: {e}")
        return

    print(f"[+] Downloaded: {pam_file}")
    print(f"[+] Extract directory: {pam_dir}")

    # Check for patch
    result = subprocess.run(["which", "patch"])
    if result.returncode != 0:
        print("Error: patch command not found. Exiting")
        raise SystemExit(1)

    # unpacks downloaded source archive
    extract_tarball(pam_file)
    # runs the build process on the extracted source (MAKE THE MALWARE PATCH HERE)
    build_pam(pam_dir)

if __name__ == "__main__":
    main()
