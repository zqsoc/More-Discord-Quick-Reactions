#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import time
import urllib.request
import zipfile
import tempfile
import glob


def run(cmd, cwd=None, env=None):
    line = subprocess.list2cmdline(cmd) if isinstance(cmd, list) else cmd
    return subprocess.run(line, shell=True, text=True, capture_output=True, cwd=cwd, env=env)


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
NODEJS_VERSION = "v20.11.1"
NODEJS_ZIP = f"https://nodejs.org/dist/{NODEJS_VERSION}/node-{NODEJS_VERSION}-win-x64.zip"


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


def kill_discord():
    step("Stopping Discord")
    names = ["discord.exe", "discordptb.exe", "discordcanary.exe", "discorddevelopment.exe", "update.exe"]
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if proc.info["name"].lower() in names:
                log(f"Stopping {proc.info['name']} ({proc.info['pid']})")
                p = psutil.Process(proc.info["pid"])
                p.terminate()
                p.wait(timeout=8)
        except Exception:
            pass
    ok("Discord stopped")


def remove_folder(path, name):
    if not os.path.exists(path):
        return
    try:
        step(f"Removing old {name}")
        shutil.rmtree(path)
        ok(f"Removed {path}")
    except Exception as e:
        warn(f"Could not fully remove {path}: {e}")


def backup_or_remove(path, name):
    if not os.path.exists(path):
        return
    step(f"Cleaning old {name}")
    try:
        backup = f"{path}_old_{int(time.time())}"
        shutil.move(path, backup)
        ok(f"Moved {path} to {backup}")
    except Exception as e:
        warn(f"Could not backup {path}, trying delete: {e}")
        remove_folder(path, name)


def clean_old_vencord():
    local = os.environ.get("LOCALAPPDATA", "")
    roaming = os.environ.get("APPDATA", "")

    # Remove old installed Vencord data
    backup_or_remove(os.path.join(local, "Vencord"), "Vencord local data")
    backup_or_remove(os.path.join(roaming, "Vencord"), "Vencord roaming data")

    # Also clean any Vencord desktop folders
    backup_or_remove(os.path.join(local, "VencordDesktop"), "Vencord Desktop data")
    backup_or_remove(os.path.join(roaming, "VencordDesktop"), "Vencord Desktop roaming data")



def download_file(url, dest, desc="Downloading"):
    step(desc)
    try:
        log(f"From: {url}")
        urllib.request.urlretrieve(url, dest)
        ok(f"Downloaded {desc}")
        return True
    except Exception as e:
        err(f"Download failed: {e}")
        return False


def extract_zip(zip_path, dest):
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(dest)
        return True
    except Exception as e:
        err(f"Extraction failed: {e}")
        return False


def find_extracted_vencord(extract_to):
    for name in os.listdir(extract_to):
        full = os.path.join(extract_to, name)
        if os.path.isdir(full) and os.path.exists(os.path.join(full, "package.json")) and os.path.isdir(os.path.join(full, "src")):
            return full
    return None


def download_vencord(target):
    if os.path.exists(target):
        backup_or_remove(target, "old Vencord source")

    os.makedirs(target, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, "vencord.zip")
        if not download_file(VENCORD_ZIP, zip_path, "Vencord source from GitHub"):
            return None

        extract_to = os.path.join(tmp, "extracted")
        if not extract_zip(zip_path, extract_to):
            return None

        src = find_extracted_vencord(extract_to)
        if not src:
            err("Could not find valid Vencord source inside the zip.")
            return None

        try:
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(target, item)
                if os.path.exists(d):
                    shutil.rmtree(d) if os.path.isdir(d) else os.remove(d)
                shutil.move(s, d)
            ok(f"Vencord source ready at {target}")
            return target
        except Exception as e:
            err(f"Could not move Vencord files: {e}")
            return None


def ensure_nodejs(tool_dir):
    import shutil
    # Check system PATH first
    existing = shutil.which("node")
    if existing:
        ok(f"Node.js found at: {existing}")
        return os.path.dirname(existing)

    step("Node.js not found. Downloading portable version")
    os.makedirs(tool_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, "nodejs.zip")
        if not download_file(NODEJS_ZIP, zip_path, f"Node.js {NODEJS_VERSION}"):
            err("Could not download Node.js. Please install it from nodejs.org and try again.")
            return None

        extract_to = os.path.join(tmp, "node")
        if not extract_zip(zip_path, extract_to):
            return None

        # Find the inner folder
        inner = None
        for name in os.listdir(extract_to):
            full = os.path.join(extract_to, name)
            if os.path.isdir(full):
                inner = full
                break

        if not inner:
            err("Could not find Node.js files in the zip.")
            return None

        # Copy all files to tool_dir
        for item in os.listdir(inner):
            s = os.path.join(inner, item)
            d = os.path.join(tool_dir, item)
            if os.path.exists(d):
                shutil.rmtree(d) if os.path.isdir(d) else os.remove(d)
            shutil.move(s, d)

    ok(f"Node.js ready at {tool_dir}")
    return tool_dir


def ensure_pnpm(tool_dir, node_dir):
    import shutil
    # Check system PATH first
    existing = shutil.which("pnpm")
    if existing:
        ok(f"pnpm found at: {existing}")
        return os.path.dirname(existing)

    step("Installing pnpm")
    npm_cmd = os.path.join(node_dir, "npm.cmd") if node_dir else "npm"

    # Install pnpm into tool_dir (no admin needed)
    r = run([npm_cmd, "install", "pnpm"], cwd=tool_dir)
    if r.returncode == 0:
        ok(f"pnpm installed in {tool_dir}")
        return os.path.join(tool_dir, "node_modules", ".bin")

    err("Could not install pnpm.")
    return None


def make_env(node_dir, pnpm_bin=None):
    env = os.environ.copy()
    paths = [node_dir]
    if pnpm_bin:
        paths.append(pnpm_bin)
    env["PATH"] = os.pathsep.join(paths) + os.pathsep + env.get("PATH", "")
    return env


def run_pnpm(args, vencord_path, env):
    step(f"Running pnpm {' '.join(args)}")
    r = run(["pnpm"] + args, cwd=vencord_path, env=env)
    if r.stdout:
        for line in r.stdout.splitlines():
            log(line)
    if r.returncode != 0:
        if r.stderr:
            for line in r.stderr.splitlines():
                err(line)
        return False
    ok(f"pnpm {' '.join(args)} done")
    return True


def install_plugin(vencord_path):
    plugin_dir = os.path.join(vencord_path, "src", "userplugins", "MoreQuickReactions")
    dest = os.path.join(plugin_dir, "index.ts")
    source = get_resource("reactions.ts")

    if not os.path.exists(source):
        err("reactions.ts not found. Make sure the .exe is in the same folder as reactions.ts")
        return None

    try:
        os.makedirs(plugin_dir, exist_ok=True)
        shutil.copy2(source, dest)
        ok(f"Plugin copied to: {dest}")
        return dest
    except Exception as e:
        err(f"Could not install plugin: {e}")
        return None


def restart_discord():
    step("Restarting Discord")
    local = os.environ.get("LOCALAPPDATA", "")
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
                ok(f"Discord started: {path}")
                return True
            except Exception as e:
                warn(f"Could not start {path}: {e}")

    warn("Could not auto-restart Discord. Please start it manually.")
    return False


def main():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    step("More Quick Reactions - Installer")
    log("This will remove old Vencord, install a fresh Vencord source, and inject it into Discord.")
    log("You should not need to type anything.")

    home = os.path.expanduser("~")
    vencord_path = os.path.join(home, "Vencord-Custom")
    tools_path = os.path.join(home, ".morequickreactions", "tools")

    # Stop Discord and clean old Vencord
    kill_discord()
    clean_old_vencord()

    # Download fresh Vencord source
    vencord_path = download_vencord(vencord_path)
    if not vencord_path:
        err("Could not download Vencord source. Check internet and try again.")
        input("Press Enter to exit...")
        return

    # Install the plugin
    if not install_plugin(vencord_path):
        input("Press Enter to exit...")
        return

    # Ensure Node.js and pnpm
    node_dir = ensure_nodejs(tools_path)
    if not node_dir:
        input("Press Enter to exit...")
        return

    pnpm_bin = ensure_pnpm(tools_path, node_dir)
    if not pnpm_bin:
        input("Press Enter to exit...")
        return

    env = make_env(node_dir, pnpm_bin if os.path.isdir(pnpm_bin) else None)

    # Build and inject
    if not run_pnpm(["install"], vencord_path, env):
        input("Press Enter to exit...")
        return

    if not run_pnpm(["build"], vencord_path, env):
        input("Press Enter to exit...")
        return

    if not run_pnpm(["inject"], vencord_path, env):
        input("Press Enter to exit...")
        return

    # Restart Discord
    restart_discord()

    step("Done")
    ok("MoreQuickReactions is installed and Vencord is injected into Discord.")
    log("Open Discord, go to Settings > Vencord > Plugins, and turn on MoreQuickReactions.")
    log(f"Log saved to: {os.path.abspath(LOG_FILE)}")
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        warn("Cancelled by user.")
