# More Quick Reactions

A Vencord plugin that gives you more quick reactions when you hover over a message.

Discord normally shows 3 quick reactions, but this plugin lets you have up to 8 by default. You can change it to anything between 0 and 42 in the plugin settings.

Made by zqsoc  
Credits to i am me

---

## What it does

When you hover over a message, a small menu of emoji reactions pops up. This plugin lets you control how many reactions show up there.

- Discord default: 3
- Plugin default: 8
- You can set it from 0 to 42

---

## Quick links

- Vencord: [https://vencord.dev](https://vencord.dev)
- Vencord GitHub: [https://github.com/Vendicated/Vencord](https://github.com/Vendicated/Vencord)
- pnpm install help: [https://pnpm.io/installation](https://pnpm.io/installation)

This plugin works with the desktop version of Discord when Vencord is installed.

---

## Easy install

The easiest way is to use the `MoreQuickReactions-Installer.exe` included in this package.

1. Run the `.exe`
2. It will detect your Vencord folder or ask you for the path
3. It will install the plugin, build Vencord, and restart Discord for you
4. If Node.js, pnpm, or Vencord is missing, it will tell you where to get them

After it finishes, open Discord, go to `Settings > Vencord > Plugins`, and turn on `MoreQuickReactions`.

---

## Manual install

If you prefer to do it yourself:

### 1. Install Vencord

Download and install Vencord from [https://vencord.dev/download](https://vencord.dev/download).

### 2. Open the userplugins folder

In your Vencord source folder, find or make this folder:

```
Vencord/src/userplugins
```

### 3. Copy the plugin

Create a new folder called `MoreQuickReactions` inside `src/userplugins`.

Copy `reactions.ts` into it. If Vencord does not load it, rename it to `index.ts`.

```
Vencord/
└── src/
    └── userplugins/
        └── MoreQuickReactions/
            └── index.ts
```

### 4. Build Vencord

Open a terminal in the Vencord folder and run:

```bash
pnpm install
pnpm build
```

If you do not have `pnpm`, install it from [https://pnpm.io/installation](https://pnpm.io/installation).

---

## How to use

1. Open Discord and go to `Settings > Vencord > Plugins`
2. Find `MoreQuickReactions` and turn it on
3. Hover over a message. You should see more quick reactions now
4. Click the settings icon next to the plugin to change how many reactions you want

---

## Notes

- Keep Discord and Vencord updated
- If the plugin does not load, check that the file is in `src/userplugins/MoreQuickReactions/` and named `index.ts`
- This is a Vencord plugin, so it needs Vencord to work
- You can replace the placeholder screenshots in this README with real ones later

---
