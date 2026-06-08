import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import hashlib
import os
import zipfile
import subprocess

PORT = 8000

def get_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest().lower()

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/add':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            source_url = data.get('url')

            if not source_url:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "No URL provided"}')
                return

            print(f"Adding payload from: {source_url}")
            
            try:
                # Same logic as update_payloads.py
                if 'github.com' in source_url:
                    parts = source_url.rstrip('/').split('/')
                    owner, repo = parts[3], parts[4]
                    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
                elif 'git.etawen.dev' in source_url:
                    parts = source_url.rstrip('/').split('/')
                    owner, repo = parts[3], parts[4]
                    api_url = f"https://git.etawen.dev/api/v1/repos/{owner}/{repo}/releases/latest"
                else:
                    raise Exception("Unsupported URL format")

                req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    release_data = json.loads(response.read().decode())

                latest_version = release_data.get('tag_name') or release_data.get('name')
                
                target_asset = None
                for asset in release_data.get('assets', []):
                    if asset['name'].endswith('.elf') or asset['name'].endswith('.zip'):
                        target_asset = asset
                        break
                        
                if not target_asset:
                    raise Exception("No .elf or .zip asset found in the latest release")

                download_url = target_asset['browser_download_url']
                filename = target_asset['name']
                
                # Make sure we're operating in the root of the repo
                root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                payloads_dir = os.path.join(root_dir, 'payloads')
                
                if not os.path.exists(payloads_dir):
                    os.makedirs(payloads_dir)
                    
                temp_path = os.path.join(payloads_dir, filename)
                urllib.request.urlretrieve(download_url, temp_path)
                
                checksum = ""
                final_elf_name = ""
                extract_file = None
                
                if filename.endswith('.zip'):
                    with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                        elf_name = None
                        for name in zip_ref.namelist():
                            if name.endswith('.elf'):
                                elf_name = name
                                break
                        if elf_name:
                            zip_ref.extract(elf_name, payloads_dir)
                            extracted_path = os.path.join(payloads_dir, elf_name)
                            checksum = get_sha256(extracted_path)
                            final_elf_name = elf_name.split('/')[-1]
                            extract_file = final_elf_name
                    os.remove(temp_path)
                else:
                    checksum = get_sha256(temp_path)
                    final_elf_name = filename

                if not checksum:
                    raise Exception("Could not process payload file")

                new_payload = {
                    "name": repo,
                    "filename": final_elf_name,
                    "url": f"https://gjarunselvan.github.io/ps5-JB-custom-loader/payloads/{final_elf_name}",
                    "source": f"https://github.com/{owner}/{repo}/releases" if 'github.com' in source_url else f"https://git.etawen.dev/{owner}/{repo}/releases",
                    "source_direct": download_url,
                    "description": release_data.get('body', f"{repo} payload")[:100] + "...",
                    "last_update": release_data['published_at'].split('T')[0],
                    "version": latest_version,
                    "checksum": checksum
                }
                if extract_file:
                    new_payload['extract_file'] = extract_file

                json_path = os.path.join(root_dir, 'payloads.json')
                with open(json_path, 'r') as f:
                    payloads = json.load(f)
                    
                exists = False
                for p in payloads:
                    if p['name'] == repo:
                        p.update(new_payload)
                        exists = True
                        break
                
                if not exists:
                    payloads.append(new_payload)

                with open(json_path, 'w') as f:
                    json.dump(payloads, f, indent=2)

                # Commit to git
                subprocess.run(["git", "add", "payloads.json", "payloads/"], cwd=root_dir, check=True)
                subprocess.run(["git", "commit", "-m", f"Add {repo} payload via local web dashboard"], cwd=root_dir, check=True)
                subprocess.run(["git", "push"], cwd=root_dir, check=True)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "payload": new_payload}).encode())

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

print(f"Starting PS5 Payload Manager Dashboard at http://localhost:{PORT}")
print("Leave this window open while using the dashboard.")
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    httpd.serve_forever()
