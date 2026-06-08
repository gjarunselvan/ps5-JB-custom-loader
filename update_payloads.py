import json
import urllib.request
import hashlib
import os
import zipfile

def get_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest().lower()

def main():
    if not os.path.exists('payloads'):
        os.makedirs('payloads')

    # Read existing payloads to avoid re-downloading things we already have
    payloads = []
    if os.path.exists('payloads.json'):
        with open('payloads.json', 'r') as f:
            payloads = json.load(f)

    # Convert to dictionary for easy lookups by repo name
    existing_dict = {p['name']: p for p in payloads}
    new_payloads_list = []
    
    # Read the master list of tracked repos
    if not os.path.exists('tracked_repos.txt'):
        print("tracked_repos.txt not found. Nothing to do.")
        return

    with open('tracked_repos.txt', 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    changed = False

    for source_url in urls:
        print(f"Checking tracked URL: {source_url}")
        
        if 'github.com' in source_url:
            parts = source_url.rstrip('/').split('/')
            owner, repo = parts[3], parts[4]
            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
            source_link = f"https://github.com/{owner}/{repo}/releases"
        elif 'git.etawen.dev' in source_url:
            parts = source_url.rstrip('/').split('/')
            owner, repo = parts[3], parts[4]
            api_url = f"https://git.etawen.dev/api/v1/repos/{owner}/{repo}/releases/latest"
            source_link = f"https://git.etawen.dev/{owner}/{repo}/releases"
        else:
            print(f"Unknown source format: {source_url}")
            continue

        # Fetch latest release data
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as response:
                release_data = json.loads(response.read().decode())
        except Exception as e:
            print(f"Failed to fetch {api_url}: {e}")
            # If it fails, keep the old data if it exists
            if repo in existing_dict:
                new_payloads_list.append(existing_dict[repo])
            continue

        latest_version = release_data.get('tag_name') or release_data.get('name')
        
        # Check if we already have this payload and if it's up to date
        if repo in existing_dict and existing_dict[repo].get('version') == latest_version:
            print(f"[{repo}] Already up to date ({latest_version}).")
            new_payloads_list.append(existing_dict[repo])
            continue

        print(f"[{repo}] New version found or newly added payload: {latest_version}")
        
        # Find asset
        target_asset = None
        for asset in release_data.get('assets', []):
            if asset['name'].endswith('.elf') or asset['name'].endswith('.zip'):
                target_asset = asset
                break
                
        if not target_asset:
            print(f"[{repo}] No suitable .elf or .zip asset found.")
            if repo in existing_dict:
                new_payloads_list.append(existing_dict[repo])
            continue

        download_url = target_asset['browser_download_url']
        filename = target_asset['name']
        temp_path = os.path.join('payloads', filename)
        
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(download_url, temp_path)
        
        checksum = ""
        final_elf_name = ""
        extract_file = None
        
        # If it's a zip we extract the ELF
        if filename.endswith('.zip'):
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                elf_name = None
                for name in zip_ref.namelist():
                    if name.endswith('.elf'):
                        elf_name = name
                        break
                if elf_name:
                    zip_ref.extract(elf_name, 'payloads')
                    extracted_path = os.path.join('payloads', elf_name)
                    checksum = get_sha256(extracted_path)
                    final_elf_name = elf_name.split('/')[-1]
                    extract_file = final_elf_name
            os.remove(temp_path)
        else:
            checksum = get_sha256(temp_path)
            final_elf_name = filename
            
        if not checksum:
            print(f"[{repo}] Failed to compute checksum.")
            if repo in existing_dict:
                new_payloads_list.append(existing_dict[repo])
            continue

        # Create or update payload entry
        description = release_data.get('body', '')
        if not description:
            description = f"{repo} payload"
        # truncate description if too long
        description = description[:150].replace('\r', '').replace('\n', ' ') + ('...' if len(description) > 150 else '')

        p = {
            "name": repo,
            "filename": final_elf_name,
            "url": f"https://gjarunselvan.github.io/ps5-JB-custom-loader/payloads/{final_elf_name}",
            "source": source_link,
            "source_direct": download_url,
            "description": description,
            "last_update": release_data['published_at'].split('T')[0],
            "version": latest_version,
            "checksum": checksum
        }
        if extract_file:
            p['extract_file'] = extract_file

        new_payloads_list.append(p)
        changed = True

    # Check if payloads were completely removed from tracked_repos.txt
    if len(new_payloads_list) != len(payloads):
        changed = True

    if changed:
        with open('payloads.json', 'w') as f:
            json.dump(new_payloads_list, f, indent=2)
        print("payloads.json updated successfully.")
    else:
        print("No updates needed.")

if __name__ == '__main__':
    main()
