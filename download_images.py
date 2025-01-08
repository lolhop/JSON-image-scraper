import json
import requests
from pathlib import Path
import re
from urllib.parse import urlparse
import os

def find_urls(obj):
    """Recursively find all URLs in a JSON object"""
    urls = set()
    
    if isinstance(obj, dict):
        for value in obj.values():
            urls.update(find_urls(value))
    elif isinstance(obj, list):
        for item in obj:
            urls.update(find_urls(item))
    elif isinstance(obj, str) and (obj.startswith('http://') or obj.startswith('https://')):
        urls.add(obj)
    
    return urls

def download_images(json_file, output_dir='downloaded_images'):
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Read JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Find all URLs
    urls = find_urls(data)
    print(f"Found {len(urls)} URLs")
    
    # Download each URL
    for url in urls:
        try:
            # Get filename from URL
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                filename = f"image_{hash(url)}.jpg"
            
            filepath = output_dir / filename
            
            # Download the image
            print(f"Downloading {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"Saved to {filepath}")
            
        except Exception as e:
            print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python script.py path/to/json_file")
        sys.exit(1)
    
    download_images(sys.argv[1])