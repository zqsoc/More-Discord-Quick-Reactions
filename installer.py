#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import time
import urllib.request
import webbrowser
import zipfile
import tempfile


def run(cmd, **kwargs):
    return subprocess.run(cmd, shell=True, text=True, capture_output=True, **kwargs)


def install_python_packages():
    if getattr(sys, "frozen", False):
        return
    try:
        import colorama, psutil
    except ImportError:
        print("Installing missing Python packages...")
        run([sys.executable, "-m", "pip", "install", "colorama", "psutil"])


install_python_packages()

import psutil
from colorama import init, Fore, Style

init()

LOG_FILE = "install_log.txt"
VENCORD_ZIP = "https://github.com/Vendicated/Vencord/archive/refs/heads/main.zip"


def log(msg, level="INFO"):
    timestamp = time.strftime("%H:%M:%S")
    line = f"[{timestamp}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def ok(msg):
    log(msg, f"{Fore.GREEN}OK{Style.RESET_ALL}")


def warn(msg):
    log(msg, f"{Fore.YELLOW}WARN{Style.RESET_ALL}")


def err(msg):
    log(msg, f"{Fore.RED}ERR{Style.RESET_ALL}")


def step(title):
    print()
    log(f"=== {title} ===")


def get_resource(name):
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, name)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)


def has_command(cmd):
    return run([cmd, "--version"]).returncode == 0 or run([cmd, "-v"]).returncode == 0


def open_page(url):
    webbrowser.open(url)
    warn(f"Opened {url} in your browser.")


def is_valid_vencord(path):
    if not path or not os.path.isdir(path):
        return False
    pkg = os.path.join(path, "package.json")
    src = os.path.join(path, "src")
    return os.path.exists(pkg) and os.path.isdir(src)


def ensure_node():
    if has_command("node"):
        return True
    step("Node.js not found")
    warn("Node.js is needed to build Vencord.")
    warn("Please install it, then run this installer again.")
    open_page("https://nodejs.org/en/download/")
    input("Press Enter after installing Node.js...")
    return has_command("node")


def ensure_pnpm():
    if has_command("pnpm"):
        return True
    step("Installing pnpm")
    if has_command("npm"):
        r = run(["npm", "install", "-g", "pnpm"])
        if r.returncode == 0:
            ok("pnpm installed")
            return True
        err("Could not install pnpm with npm")
    warn("pnpm is needed. Install it from the official site.")
    open_page("https://pnpm.io/installation")
    input("Press Enter after installing pnpm...")
    return has_command("pnpm")


def download_file(url, dest, desc="Downloading"):
    step(desc)
    try:
        urllib.request.urlretrieve(url, dest)
        ok(f"Downloaded to {dest}")
        return True
    except Exception as e:
        err(f"Download failed: {e}")
        return False


def extract_zip(zip_path, dest):
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(dest)
        ok(f"Extracted to {dest}")
        return True
    except Exception as e:
        err(f"Extraction failed: {e}")
        return False


def find_extracted_vencord(extract_to):
    for name in os.listdir(extract_to):
        full = os.path.join(extract_to, name)
        if os.path.isdir(full) and is_valid_vencord(full):
            return full
    return None


def download_vencord(target_folder):
    step("Downloading Vencord source")
    if os.path.exists(target_folder):
        warn(f"Folder exists: {target_folder}")
        warn("I will delete it and download a fresh copy.")
        confirm = input("Type 'yes' to continue: ").strip().lower()
        if confirm != "yes":
            warn("Cancelled. Vencord was not downloaded.")
            return None
        try:
            shutil.rmtree(target_folder)
            ok("Old folder removed")
        except Exception as e:
            err(f"Could not remove old folder: {e}")
            return None

    os.makedirs(target_folder, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, "vencord.zip")
        if not download_file(VENCORD_ZIP, zip_path, "Downloading Vencord from GitHub"):
            return None

        extract_to = os.path.join(tmp, "extracted")
        if not extract_zip(zip_path, extract_to):
            return None

        src = find_extracted_vencord(extract_to)
        if not src:
            err("Could not find valid Vencord source inside the zip.")
            return None

        try:
            # Move contents from the Vencord-main folder to target
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(target_folder, item)
                if os.path.isdir(s):
                    shutil.move(s, d)
                else:
                    shutil.move(s, d)
            ok(f"Vencord source ready at {target_folder}")
            return target_folder
        except Exception as e:
            err(f"Could not move Vencord files: {e}")
            return None


def pick_vencord():
    home = os.path.expanduser("~")
    guesses = [
        os.path.join(home, "Vencord"),
        os.path.join(home, "Documents", "Vencord"),
        os.path.join(home, "Downloads", "Vencord"),
    ]
    found = [p for p in guesses if is_valid_vencord(p)]

    if found:
        step("Vencord source found")
        for i, path in enumerate(found, 1):
            log(f"  {i}. {path}")
        log(f"  {len(found) + 1}. Enter a different path")
        log(f"  {len(found) + 2}. Download Vencord source to a new folder")
        choice = input("Pick an option: ").strip()
        try:
            n = int(choice)
            if 1 <= n <= len(found):
                return found[n - 1]
            if n == len(found) + 1:
                path = input("Full path to Vencord source: ").strip()
                if is_valid_vencord(path):
                    return path
                return fix_vencord(path)
            if n == len(found) + 2:
                return download_vencord(input("Where to download Vencord (e.g. C:\\Users\\you\\Vencord): ").strip())
        except ValueError:
            pass
    else:
        step("Vencord not found")
        log("Vencord source was not found in the usual places.")
        use_default = input(f"Download Vencord source to {os.path.join(home, 'Vencord')}? (yes/no): ").strip().lower()
        if use_default == "yes":
            return download_vencord(os.path.join(home, "Vencord"))

    step("Enter Vencord source folder")
    path = input("Full path to your Vencord source folder: ").strip()
    if is_valid_vencord(path):
        return path
    return fix_vencord(path)


def fix_vencord(path):
    if not path or not os.path.isdir(path):
        warn("That path does not exist or is not a folder.")
    else:
        warn(f"This does not look like a Vencord source folder: {path}")
        warn("It needs a package.json and src/ folder.")

    log("Options:")
    log("  1. Download fresh Vencord source to this path")
    log("  2. Enter a different path")
    log("  3. Cancel")
    choice = input("Pick an option: ").strip()

    if choice == "1":
        return download_vencord(path)
    if choice == "2":
        return pick_vencord()
    warn("Cancelled by user.")
    return None


def install_plugin(vencord_path):
    plugin_dir = os.path.join(vencord_path, "src", "userplugins", "MoreQuickReactions")
    dest = os.path.join(plugin_dir, "index.ts")
    source = get_resource("reactions.ts")

    if not os.path.exists(source):
        err("reactions.ts not found next to installer.")
        return None

    os.makedirs(plugin_dir, exist_ok=True)
    shutil.copy2(source, dest)
    ok(f"Plugin installed to: {dest}")
    return dest


def build_vencord(vencord_path):
    if not ensure_node():
        return False
    if not ensure_pnpm():
        return False

    step("Running pnpm install")
    r = run(["pnpm", "install"], cwd=vencord_path)
    if r.returncode != 0:
        err("pnpm install failed")
        if r.stdout:
            err(r.stdout)
        return False
    ok("pnpm install done")

    step("Running pnpm build")
    r = run(["pnpm", "build"], cwd=vencord_path)
    if r.returncode != 0:
        err("pnpm build failed")
        if r.stdout:
            err(r.stdout)
        return False
    ok("pnpm build done")
    return True


def restart_discord():
    step("Restarting Discord")
    discord_names = ["discord.exe", "discordptb.exe", "discordcanary.exe", "discorddevelopment.exe"]
    killed = False

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = proc.info["name"].lower()
            if name in discord_names:
                log(f"Stopping {proc.info['name']} (PID {proc.info['pid']})")
                p = psutil.Process(proc.info["pid"])
                p.terminate()
                p.wait(timeout=5)
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass

    if not killed:
        warn("Discord was not running or could not be stopped.")

    local = os.environ.get("LOCALAPPDATA", "")
    import glob
    patterns = [
        os.path.join(local, "Discord", "Update.exe"),
        os.path.join(local, "DiscordPTB", "Update.exe"),
        os.path.join(local, "DiscordCanary", "Update.exe"),
        os.path.join(local, "DiscordDevelopment", "Update.exe"),
        os.path.join(local, "Discord", "app-*", "Discord.exe"),
        os.path.join(local, "DiscordPTB", "app-*", "DiscordPTB.exe"),
        os.path.join(local, "DiscordCanary", "app-*", "DiscordCanary.exe"),
    ]
    launchers = []
    for pat in patterns:
        launchers.extend(sorted(glob.glob(pat)))

    for path in launchers:
        if os.path.exists(path):
            try:
                subprocess.Popen([path], shell=True)
                ok(f"Discord restarted: {path}")
                return True
            except Exception as e:
                warn(f"Could not start {path}: {e}")

    warn("Could not auto-restart Discord. Please start it manually.")
    return False


def main():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    step("More Quick Reactions - Installer")
    log("This will install the plugin and restart Discord.")
    log("If anything is missing, it will help you fix it or download it.")

    vencord = pick_vencord()
    if not vencord or not is_valid_vencord(vencord):
        err("No valid Vencord source was found. Exiting.")
        input("Press Enter to exit...")
        return

    log(f"Using Vencord at: {vencord}")

    if not install_plugin(vencord):
        input("Press Enter to exit...")
        return

    if not build_vencord(vencord):
        input("Press Enter to exit...")
        return

    restart_discord()

    step("Done")
    ok("MoreQuickReactions is installed.")
    log("Enable it in Discord: Settings > Vencord > Plugins > MoreQuickReactions")
    log(f"Log saved to: {os.path.abspath(LOG_FILE)}")
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        warn("Cancelled by user.")
