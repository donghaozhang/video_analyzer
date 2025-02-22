import os
import time
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

class VideoAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_video(self, video_path, prompt):
        """Analyze video using Gemini API."""
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        try:
            print(f"Processing video: {video_path}")
            
            # Upload the video file to Gemini
            print("Uploading file...")
            video_file = genai.upload_file(path=video_path)
            print(f"Completed upload: {video_file.uri}")

            # Wait for processing
            while video_file.state.name == "PROCESSING":
                print('Waiting for video to be processed...')
                time.sleep(10)
                video_file = genai.get_file(video_file.name)

            if video_file.state.name == "FAILED":
                raise ValueError(f"Video processing failed: {video_file.state.name}")

            # Generate content from the video
            print("Making inference request...")
            response = self.model.generate_content(
                [prompt, video_file],
                request_options={"timeout": 600}
            )

            print('Video processing complete')
            
            # Cleanup the uploaded file
            genai.delete_file(video_file.name)
            
            return response.text

        except Exception as e:
            print(f"Error during video analysis: {str(e)}")
            raise

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
        
    analyzer = VideoAnalyzer(api_key)

    try:
        # Using 7news.mp4 from the current directory
        video_path = "./7news.mp4"
        prompt = "Please analyze this news video and provide a detailed summary of the main story, including key points and any significant quotes or statements."
        
        result = analyzer.analyze_video(video_path, prompt)
        print("\nAnalysis Result:")
        print(result)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 