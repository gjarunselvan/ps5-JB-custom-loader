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
    with open('payloads.json', 'r') as f:
        payloads = json.load(f)

    changed = False

    for p in payloads:
        source = p['source']
        print(f"Checking {p['name']}...")
        
        if 'github.com' in source:
            parts = source.split('/')
            owner, repo = parts[3], parts[4]
            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        elif 'git.etawen.dev' in source:
            parts = source.split('/')
            owner, repo = parts[3], parts[4]
            api_url = f"https://git.etawen.dev/api/v1/repos/{owner}/{repo}/releases/latest"
        else:
            print("Unknown source format")
            continue

        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as response:
                release_data = json.loads(response.read().decode())
        except Exception as e:
            print(f"Failed to fetch {api_url}: {e}")
            continue

        latest_version = release_data.get('tag_name') or release_data.get('name')
        
        if latest_version == p['version']:
            print("Already up to date.")
            continue

        print(f"New version found: {latest_version}")
        
        # Find asset
        target_asset = None
        for asset in release_data.get('assets', []):
            if asset['name'].endswith('.elf') or asset['name'].endswith('.zip'):
                target_asset = asset
                break
                
        if not target_asset:
            print("No suitable asset found.")
            continue

        download_url = target_asset['browser_download_url']
        filename = target_asset['name']
        
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(download_url, filename)
        
        checksum = ""
        # If it's a zip and we need to extract an ELF
        if filename.endswith('.zip') and 'extract_file' in p:
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                elf_name = None
                for name in zip_ref.namelist():
                    if name.endswith('.elf'):
                        elf_name = name
                        break
                if elf_name:
                    zip_ref.extract(elf_name, ".")
                    checksum = get_sha256(elf_name)
                    os.remove(elf_name)
                    p['extract_file'] = elf_name.split('/')[-1]
        else:
            checksum = get_sha256(filename)
            
        os.remove(filename)
        
        if not checksum:
            print("Failed to compute checksum.")
            continue

        # Update JSON
        p['version'] = latest_version
        p['checksum'] = checksum
        p['url'] = download_url
        p['source_direct'] = download_url
        p['filename'] = filename
        p['last_update'] = release_data['published_at'].split('T')[0]
        changed = True

    if changed:
        with open('payloads.json', 'w') as f:
            json.dump(payloads, f, indent=2)
        print("payloads.json updated successfully.")
    else:
        print("No updates needed.")

if __name__ == '__main__':
    main()
