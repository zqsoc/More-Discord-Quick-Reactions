# More Quick Reactions

A Vencord plugin that shows more reactions in the quick-reaction hover menu on Discord messages.

By default, Discord only shows **3 quick reactions** when you hover over a message. This plugin lets you show up to **8** (or any number between 0 and 42) and change it from the plugin settings.

Made by zqsoc  
Credits to i am me

---

## What it does

When you hover over a message in Discord, a small menu of emoji reactions appears. Discord normally limits this to 3 options. This plugin increases that count and lets you customize it.

- Default quick reactions: **3**
- New default with this plugin: **8**
- Custom range: **0 to 42**

You can adjust the exact number in the Vencord plugin settings at any time.

---

## Official Resources

Before installing, make sure you have Vencord installed.

- **Vencord GitHub:** [https://github.com/Vendicated/Vencord](https://github.com/Vendicated/Vencord)
- **Vencord Docs / Install Guide:** [https://vencord.dev/](https://vencord.dev/)
- **Vencord Discord server:** [https://discord.gg/vencord](https://discord.gg/vencord)

> This plugin only works with the desktop version of Discord running the Vencord client mod.

---

## How to install

### 1. Install Vencord

If you have not installed Vencord yet, follow the official Vencord install guide first:

[https://vencord.dev/download](https://vencord.dev/download)

![Install Vencord button](https://placehold.co/800x100/2e3440/88c0d0?text=Install+Vencord+from+the+official+website)

### 2. Open the userplugins folder

Open your Vencord source folder on your computer and find this path:

```
Vencord/src/userplugins
```

If the `userplugins` folder does not exist, create it.

### 3. Copy the plugin

Create a new folder called `MoreQuickReactions` inside `src/userplugins`.

Copy the `reactions.ts` file into that folder. If Vencord does not load it, rename it to `index.ts`.

```
Vencord/
└── src/
    └── userplugins/
        └── MoreQuickReactions/
            └── index.ts
```

![Create the plugin folder](https://placehold.co/800x100/2e3440/88c0d0?text=Create+MoreQuickReactions+folder)

### 4. Build Vencord

Open a terminal in the Vencord folder and run the following commands to install dependencies and rebuild:

```bash
pnpm install
pnpm build
```

If you do not have `pnpm`, install it from the official site:

[https://pnpm.io/installation](https://pnpm.io/installation)

![Build Vencord](https://placehold.co/800x100/2e3440/88c0d0?text=Run+pnpm+build+in+terminal)

---

## How to use

### 1. Turn on the plugin

Open Discord and go to:

```
User Settings → Vencord → Plugins
```

Search for **MoreQuickReactions** and turn on the toggle.

![Enable the plugin toggle](https://placehold.co/800x100/2e3440/88c0d0?text=Enable+MoreQuickReactions+in+plugins+list)

### 2. Hover over a message

Hover over any message in a channel. You should now see up to 8 quick reaction emojis instead of the usual 3.

### 3. Change the number

Open the plugin settings by clicking the **Settings** button next to the plugin toggle.

![Open plugin settings button](https://placehold.co/800x100/2e3440/88c0d0?text=Click+Settings+next+to+MoreQuickReactions)

You will see a number input. Type any value from **0 to 42** to control how many reactions show in the hover menu.

---

## Notes

- Make sure Discord and Vencord are up to date.
- If the plugin does not load, double-check that the file is inside `src/userplugins/MoreQuickReactions/` and is named `index.ts`.
- This plugin is only for Vencord and will not work on the default Discord app.
- Replace the placeholder screenshots in this README with real images of the Vencord plugins page and the settings button for a better user guide.

---
