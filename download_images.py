# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
from pathlib import Path

def download_image(url, filename):
    """Download an image from URL and save it to filename"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
            
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")

def main():
    # Create images directory if it doesn't exist
    Path('images').mkdir(exist_ok=True)
    
    # List of image URLs and their filenames
    images = [
        ("https://storage.googleapis.com/generativeai-downloads/images/socks.jpg", "Socks.jpg"),
        ("https://storage.googleapis.com/generativeai-downloads/images/vegetables.jpg", "Vegetables.jpg"),
        ("https://storage.googleapis.com/generativeai-downloads/images/Japanese_Bento.png", "Japanese_bento.png"),
        ("https://storage.googleapis.com/generativeai-downloads/images/Cupcakes.jpg", "Cupcakes.jpg"),
        ("https://storage.googleapis.com/generativeai-downloads/images/origamis.jpg", "Origamis.jpg"),
        ("https://storage.googleapis.com/generativeai-downloads/images/fruits.jpg", "Fruits.jpg"),
        ("https://storage.googleapis.com/generativeai-downloads/images/cat.jpg", "Cat.jpg"),
        ("https://storage.googleapis.com/generativeai-downloads/images/pumpkins.jpg", "Pumpkins.jpg"),
        ("https://storage.googleapis.com/generativeai-downloads/images/breakfast.jpg", "Breakfast.jpg"),
        ("https://storage.googleapis.com/generativeai-downloads/images/bookshelf.jpg", "Bookshelf.jpg"),
        ("https://storage.googleapis.com/generativeai-downloads/images/spill.jpg", "Spill.jpg")
    ]
    
    print("Downloading example images...")
    for url, filename in images:
        filepath = Path('images') / filename
        download_image(url, filepath)
    
    print("\nDownload complete! Images are saved in the 'images' directory.")

if __name__ == "__main__":
    main() 