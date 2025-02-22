import os
import sys
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import json
from pathlib import Path
from dotenv import load_dotenv
import argparse

class SpatialAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # System instructions for bounding box detection
        self.system_instructions = """
        Return bounding boxes as a JSON array with labels. Never return masks or code fencing. 
        Limit to 25 objects. If an object is present multiple times, name them according to 
        their unique characteristic (colors, size, position, unique characteristics, etc.).
        """
        
        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            }
        ]

    def analyze_image(self, image_path, prompt):
        """Analyze image using Gemini API and return bounding boxes."""
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        try:
            # Load and resize image
            image = Image.open(image_path)
            image.thumbnail([1024, 1024], Image.Resampling.LANCZOS)
            
            # Combine system instructions with prompt
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

    def draw_bounding_boxes(self, image, bounding_boxes_text):
        """Draw bounding boxes and labels on image."""
        draw = ImageDraw.Draw(image)
        width, height = image.size

        # Define colors for boxes
        colors = ['red', 'green', 'blue', 'yellow', 'orange', 'pink', 'purple']
        
        # Parse JSON from response
        try:
            bounding_boxes = json.loads(self._parse_json(bounding_boxes_text))
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Received text: {bounding_boxes_text}")
            raise ValueError("Invalid JSON in analysis response")

        # Try to load a font that supports multiple languages
        try:
            font = ImageFont.truetype("NotoSansCJK-Regular.ttc", size=14)
        except:
            font = ImageFont.load_default()

        # Draw boxes and labels
        for i, box in enumerate(bounding_boxes):
            try:
                color = colors[i % len(colors)]
                
                # Convert normalized coordinates to absolute
                y1, x1, y2, x2 = [int(coord/1000 * (height if i % 2 == 0 else width)) 
                                for i, coord in enumerate(box["box_2d"])]
                
                # Ensure coordinates are in correct order
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)
                
                # Draw rectangle
                draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=4)
                
                # Add label if present
                if "label" in box:
                    draw.text((x1 + 8, y1 + 6), box["label"], fill=color, font=font)
                    
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
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Analyze images using Google Gemini API')
    parser.add_argument('--image', '-i', type=str, help='Path to the image file')
    parser.add_argument('--prompt', '-p', type=str, 
                       default="Detect all objects in this image and label them with descriptions",
                       help='Prompt for image analysis')
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    # If no image path provided, list available images and ask user to choose
    if not args.image:
        print("\nNo image path provided. Looking for images in current directory...")
        image_files = list(Path('.').glob('*.jpg')) + list(Path('.').glob('*.jpeg')) + list(Path('.').glob('*.png'))
        
        if not image_files:
            print("No image files found in current directory.")
            print("Please provide an image path using --image argument")
            print("Example: python spatial_analyzer.py --image path/to/your/image.jpg")
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

    analyzer = SpatialAnalyzer(api_key)

    try:
        # Analyze image
        print(f"\nAnalyzing image: {image_path}")
        print(f"Using prompt: {args.prompt}")
        
        result_text, image = analyzer.analyze_image(image_path, args.prompt)
        print("\nAnalysis Result:")
        print(result_text)
        
        # Draw bounding boxes
        annotated_image = analyzer.draw_bounding_boxes(image, result_text)
        
        # Save result
        output_path = f"analyzed_{Path(image_path).stem}.jpg"
        annotated_image.save(output_path)
        print(f"\nAnnotated image saved as '{output_path}'")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 