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

import os
import sys
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import json
from pathlib import Path
from dotenv import load_dotenv
import argparse

# Load environment variables from .env file
# Look for .env file in parent directory if it's not in current directory
load_dotenv()  # First try the current directory
if not os.getenv("GEMINI_API_KEY"):
    # Try parent directory
    parent_env_path = Path(__file__).parent.parent / '.env'
    if parent_env_path.exists():
        load_dotenv(parent_env_path)

class EmotionAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # System instructions for emotion detection
        self.system_instructions = """
        Return bounding boxes as a JSON array with labels. Never return masks or code fencing. 
        Limit to 25 objects. For each person detected, analyze their facial expression and 
        select exactly one emotion from: [happy, sad, angry, surprise, disgust, fear, neutral].
        Label format should be "Person: [emotion]".
        """
        
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            }
        ]

    def analyze_emotions(self, image_path, prompt=None):
        """Analyze emotions in image using Gemini API."""
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        try:
            # Load and resize image
            image = Image.open(image_path)
            image.thumbnail([1024, 1024], Image.Resampling.LANCZOS)
            
            # Default prompt if none provided
            if prompt is None:
                prompt = "Detect all people in this image and analyze their emotions."
            
            full_prompt = f"{self.system_instructions}\n\n{prompt}"
            
            # Generate content
            response = self.model.generate_content(
                contents=[full_prompt, image],
                generation_config={
                    "temperature": 0.5,
                },
                safety_settings=self.safety_settings
            )
            
            return response.text, image
            
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            raise

    def draw_emotion_boxes(self, image, analysis_text):
        """Draw bounding boxes with emotion labels."""
        draw = ImageDraw.Draw(image)
        width, height = image.size

        # Colors for different emotions
        emotion_colors = {
            'happy': 'green',
            'sad': 'blue',
            'angry': 'red',
            'surprise': 'yellow',
            'disgust': 'purple',
            'fear': 'orange',
            'neutral': 'gray'
        }
        
        try:
            bounding_boxes = json.loads(self._parse_json(analysis_text))
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Received text: {analysis_text}")
            raise ValueError("Invalid JSON in analysis response")

        # Increased font size from 14 to 36
        try:
            font = ImageFont.truetype("NotoSansCJK-Regular.ttc", size=36)
        except:
            try:
                # Fallback to default font with larger size
                font = ImageFont.load_default().font_variant(size=36)
            except:
                font = ImageFont.load_default()

        # Draw boxes and emotion labels
        for i, box in enumerate(bounding_boxes):
            try:
                if "label" not in box or "Person:" not in box["label"]:
                    continue
                
                # Extract emotion from label
                emotion = box["label"].split(": ")[1].lower()
                color = emotion_colors.get(emotion, 'white')
                
                # Convert coordinates
                y1, x1, y2, x2 = [int(coord/1000 * (height if i % 2 == 0 else width)) 
                                for i, coord in enumerate(box["box_2d"])]
                
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)
                
                # Draw thicker rectangle
                draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=6)
                
                # Draw text with larger offset and background
                text = f"{emotion}"
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # Position text below the box
                text_x = x1 + (x2 - x1 - text_width) // 2  # Center text horizontally
                text_y = y2 + 10  # Place text 10 pixels below the box
                
                # Draw text background
                draw.rectangle(
                    [(text_x - 5, text_y - 5), 
                     (text_x + text_width + 5, text_y + text_height + 5)],
                    fill='black'
                )
                
                # Draw text
                draw.text((text_x, text_y), text, fill=color, font=font)
                    
            except Exception as e:
                print(f"Error drawing box {i}: {str(e)}")
                continue

        return image

    def _parse_json(self, json_output):
        """Parse JSON from model output."""
        lines = json_output.splitlines()
        for i, line in enumerate(lines):
            if line == "```json":
                json_output = "\n".join(lines[i+1:])
                return json_output.split("```")[0]
        return json_output

def main():
    parser = argparse.ArgumentParser(description='Analyze emotions in images using Google Gemini API')
    parser.add_argument('--image', '-i', type=str, help='Path to the image file')
    parser.add_argument('--prompt', '-p', type=str, 
                       default="Detect all people and analyze their emotions",
                       help='Custom prompt for emotion analysis')
    parser.add_argument('--api-key', type=str, help='Gemini API key (overrides environment variable)')
    args = parser.parse_args()

    # Get API key from command line argument or environment variable
    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in .env file or use --api-key argument.")
    
    # Handle image path
    if not args.image:
        print("\nNo image path provided. Looking for images in current directory...")
        image_files = list(Path('.').glob('*.jpg')) + list(Path('.').glob('*.jpeg')) + list(Path('.').glob('*.png'))
        
        if not image_files:
            print("No image files found in current directory.")
            print("Please provide an image path using --image argument")
            sys.exit(1)
            
        print("\nAvailable images:")
        for i, img in enumerate(image_files, 1):
            print(f"{i}. {img}")
            
        while True:
            try:
                choice = int(input("\nChoose an image number (or 0 to exit): "))
                if choice == 0:
                    sys.exit(0)
                if 1 <= choice <= len(image_files):
                    image_path = str(image_files[choice - 1])
                    break
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    else:
        image_path = args.image

    analyzer = EmotionAnalyzer(api_key)

    try:
        print(f"\nAnalyzing emotions in image: {image_path}")
        result_text, image = analyzer.analyze_emotions(image_path, args.prompt)
        print("\nAnalysis Result:")
        print(result_text)
        
        annotated_image = analyzer.draw_emotion_boxes(image, result_text)
        output_path = f"emotion_analyzed_{Path(image_path).stem}.jpg"
        annotated_image.save(output_path)
        print(f"\nAnnotated image saved as '{output_path}'")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 