# 🎮 PS5 Jailbreak Custom Loader & Payload Registry

Welcome to the **PS5 JB Custom Loader** repository! This project serves as a highly customized, ultra-fast, and natively hosted payload registry (`payloads.json`) specifically curated for PS5 jailbroken consoles.

Unlike standard mirror repositories that redirect your console to external download links (which can sometimes break, return 404s, or provide incompatible `.zip` files), this repository natively hosts the raw `.elf` payloads directly via GitHub Pages for maximum reliability and speed.

---

## 🤖 The Auto-Updater Bot

The defining feature of this repository is its **100% Autonomous Payload Updater**. 

Built entirely on GitHub Actions, a custom Python script wakes up **every 2 hours** to ensure your console always has the absolute latest tools. 

### How It Works:
1. **Scans Original Sources**: The bot pings the official GitHub/Gitea APIs of the payload developers.
2. **Detects Updates**: It compares the latest release versions against your `payloads.json` registry.
3. **Smart Extraction**: If a developer releases a payload wrapped in a `.zip` file, the bot automatically downloads the zip, extracts the raw `.elf` file, and calculates its exact SHA-256 cryptographic hash.
4. **Native Hosting**: The newly extracted `.elf` file is uploaded directly to the `payloads/` directory in this repository.
5. **Registry Sync**: The bot updates `payloads.json` to point your PS5 exactly to the new, natively hosted file.

You never have to manually update a payload again.

---

## 📦 Curated Payloads

This custom loader currently tracks and natively hosts the following premium tools:

- **[ps5upload](https://github.com/phantomptr/ps5upload)** - High-performance background PS5 package uploader and installer payload.
- **[elf-arsenal](https://git.etawen.dev/soniciso/elf-arsenal)** - A collection of helpful tools, modifications, and arsenals for the PS5.
- **[Spectrum-Library](https://github.com/Phoenixx1202/Spectrum-Library)** - Local library dashboard and background download service with multi-format and DLC support.
- **[pegasus-dl](https://github.com/pegasus-ps5/pegasus-dl)** - A high-performance segmented downloader payload for PS5 with advanced queueing and merging capabilities.

---

## 🚀 Live Endpoint

Your custom PS5 Loader should be configured to pull the registry from the following endpoint:

👉 **`https://gjarunselvan.github.io/ps5-JB-custom-loader/payloads.json`**

*(Make sure GitHub Pages is enabled in the repository settings targeting the `main` branch).*

---

*Automatically maintained by GitHub Actions.*
