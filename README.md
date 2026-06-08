# 🎮 PS5 Jailbreak Custom Loader & Payload Registry

Welcome to the **PS5 JB Custom Loader** repository! This project serves as a highly customized, ultra-fast, and natively hosted payload registry (`payloads.json`) specifically curated for PS5 jailbroken consoles.

Unlike standard mirror repositories that redirect your console to external download links (which can sometimes break, return 404s, or provide incompatible `.zip` files), this repository natively hosts the raw `.elf` payloads directly via GitHub Pages for maximum reliability and speed.

---

## ☁️ Managing Payloads Online (Zero Setup Required)

You do not need any local scripts or web dashboards to add new payloads. The entire repository is controlled by a single master database file: **`tracked_repos.txt`**.

### How to Add or Remove a Payload:
1. Open **`tracked_repos.txt`** on the GitHub website.
2. Click the ✏️ **Pencil icon** to edit the file.
3. **To Add:** Paste the GitHub URL of the new payload developer's repository onto a new line (e.g., `https://github.com/phantomptr/ps5upload`).
4. **To Remove:** Simply delete the line containing the URL.
5. Click the green **"Commit changes"** button.

The second you save the file, the **Auto-Updater Bot** takes over.

---

## 🤖 The Auto-Updater Bot

The defining feature of this repository is its **100% Autonomous Payload Updater**. 

Built entirely on GitHub Actions, a custom Python script automatically runs every time you modify `tracked_repos.txt`, and it also wakes up **every 2 hours** to ensure your console always has the absolute latest tools. 

### How It Works:
1. **Scans Original Sources**: The bot reads your `tracked_repos.txt` list and pings the official GitHub/Gitea APIs of the payload developers.
2. **Detects Updates**: It compares the latest release versions against your `payloads.json` registry.
3. **Smart Extraction**: If a developer releases a payload wrapped in a `.zip` file, the bot automatically downloads the zip, extracts the raw `.elf` file, and calculates its exact SHA-256 cryptographic hash.
4. **Native Hosting**: The newly extracted `.elf` file is uploaded directly to the `payloads/` directory in this repository.
5. **Registry Sync**: The bot updates `payloads.json` to point your PS5 exactly to the new, natively hosted file and commits all changes automatically.

You never have to manually download, extract, hash, or update a payload again.

---

## 🚀 Live Endpoint

Your custom PS5 Loader should be configured to pull the registry from the following endpoint:

👉 **`https://gjarunselvan.github.io/ps5-JB-custom-loader/payloads.json`**

*(Make sure GitHub Pages is enabled in the repository settings targeting the `main` branch).*

---

*Automatically maintained by GitHub Actions.*
