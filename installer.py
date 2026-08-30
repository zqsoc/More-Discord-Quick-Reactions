#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import time
import urllib.request
import webbrowser


def run(cmd, **kwargs):
    return subprocess.run(cmd, shell=True, text=True, capture_output=True, **kwargs)


def install_python_packages():
    """if running the .py directly, make sure we have what we need"""
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


def download(url, dest):
    try:
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        err(f"Download failed: {e}")
        return False


def open_page(url):
    webbrowser.open(url)
    warn(f"Opening {url} in your browser...")


def install_node():
    step("Node.js not found")
    warn("Node.js is needed to build Vencord.")
    warn("Please install it, then run this installer again.")
    open_page("https://nodejs.org/en/download/")
    input("Press Enter after installing Node.js...")


def install_pnpm():
    if has_command("npm"):
        step("Installing pnpm via npm")
        r = run(["npm", "install", "-g", "pnpm"])
        if r.returncode == 0:
            ok("pnpm installed")
            return True
        err("Could not install pnpm with npm")
    warn("pnpm is needed. Install it from the official site.")
    open_page("https://pnpm.io/installation")
    input("Press Enter after installing pnpm...")
    return has_command("pnpm")


def install_vencord():
    step("Vencord not found")
    warn("Vencord needs to be installed first.")
    warn("This will open the Vencord download page.")
    open_page("https://vencord.dev/download")
    input("Install Vencord, then run this installer again.")
    return None


def find_vencord():
    home = os.path.expanduser("~")
    guesses = [
        os.path.join(home, "Vencord"),
        os.path.join(home, "Documents", "Vencord"),
        os.path.join(home, "Downloads", "Vencord"),
    ]
    return [p for p in guesses if os.path.isdir(p) and os.path.exists(os.path.join(p, "package.json"))]


def pick_vencord():
    found = find_vencord()
    if found:
        step("Vencord folder found")
        for i, path in enumerate(found, 1):
            log(f"  {i}. {path}")
        log(f"  {len(found) + 1}. Enter a different path")
        choice = input("Pick an option: ").strip()
        try:
            n = int(choice)
            if 1 <= n <= len(found):
                return found[n - 1]
        except ValueError:
            pass
    step("Enter Vencord folder")
    return input("Full path to your Vencord folder: ").strip()


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
    if not has_command("node"):
        install_node()
        if not has_command("node"):
            err("Node.js still not found. Exiting.")
            return False

    if not has_command("pnpm"):
        if not install_pnpm():
            err("pnpm not available. Exiting.")
            return False

    step("Running pnpm install")
    r = run(["pnpm", "install"], cwd=vencord_path)
    if r.returncode != 0:
        err(r.stdout)
        return False
    ok("pnpm install done")

    step("Running pnpm build")
    r = run(["pnpm", "build"], cwd=vencord_path)
    if r.returncode != 0:
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
    launchers = [
        os.path.join(local, "Discord", "Update.exe"),
        os.path.join(local, "DiscordPTB", "Update.exe"),
        os.path.join(local, "DiscordCanary", "Update.exe"),
        os.path.join(local, "DiscordDevelopment", "Update.exe"),
    ]

    import glob
    patterns = [
        os.path.join(local, "Discord", "app-*", "Discord.exe"),
        os.path.join(local, "DiscordPTB", "app-*", "DiscordPTB.exe"),
        os.path.join(local, "DiscordCanary", "app-*", "DiscordCanary.exe"),
    ]
    for pat in patterns:
        launchers.extend(sorted(glob.glob(pat)))

    for path in launchers:
        if os.path.exists(path):
            try:
                subprocess.Popen([path], shell=True)
                ok(f"Discord restarted: {path}")
                return True
            except Exception as e:
                warn(f"Failed to start {path}: {e}")

    warn("Could not auto-restart Discord. Please restart it manually.")
    return False


def main():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    step("More Quick Reactions - Installer")
    log("This will install the plugin and restart Discord.")

    vencord = pick_vencord()
    if not vencord or not os.path.isdir(vencord):
        err("Vencord folder is not valid.")
        vencord = install_vencord()
        if not vencord:
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
