# Video and Image Analysis with Gemini API

A Python-based tool that leverages Google's Gemini API to analyze video and image content. This project demonstrates the integration of Gemini's analysis capabilities with Python.

## Features
- Video content analysis and summarization
- Image spatial analysis with bounding box detection
- Multi-language support for labels and descriptions
- Interactive command-line interface
- Automated image processing and visualization
- Comprehensive error handling

## Project Structure 
```
project/
├── README.md                  # Project documentation
├── environment.yml           # Conda environment configuration
├── video_analyzer.py         # Video analysis implementation
├── spatial_analyzer.py       # Image spatial analysis implementation
├── download_images.py        # Utility to download example images
└── .env                     # Environment variables (create this)
```

## Prerequisites
- Python 3.10 or higher
- Conda package manager
- Google Gemini API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/video-analyzer.git
cd video-analyzer
```

2. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate video-analysis
```

3. Create a `.env` file with your Google Gemini API key:
```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

## Usage

### Video Analysis
```bash
python video_analyzer.py --video path/to/video.mp4
```

### Image Spatial Analysis
1. Download example images (optional):
```bash
python download_images.py
```

2. Analyze an image:
```bash
python spatial_analyzer.py --image path/to/image.jpg
```

3. Custom analysis prompt:
```bash
python spatial_analyzer.py --image path/to/image.jpg --prompt "Find and label all food items"
```

### Example Prompts
- General detection: "Detect all objects in this image and label them"
- Food analysis: "Find and label all food items"
- Text detection: "Identify any text or writing in the image"
- Face analysis: "Detect faces and expressions"
- Size estimation: "Label objects with their approximate sizes"

## Output
- Video analysis generates text summaries
- Image analysis creates annotated images with bounding boxes
- Results are saved with descriptive filenames
- Progress and status are displayed in the console

## Error Handling
The tools include comprehensive error handling for:
- Missing API keys
- File not found errors
- Processing failures
- API communication issues
- JSON parsing errors
- Image processing errors

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

Copyright 2024 Google LLC
