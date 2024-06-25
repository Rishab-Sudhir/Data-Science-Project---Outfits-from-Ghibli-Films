# Data Science Project: Outfits from Ghibli Films

## Overview

This project aims to analyze and visualize the color schemes used in Studio Ghibli films, each directory has analysis for a specifc film. By extracting the dominant colors from each frame of the film, we can create outfits inspired by the unique and beautiful color palettes.

## Project Structure

The repository is structured into several main directories and scripts:

### Directories

- **ExtractingColors**
  - `ExtractColors.py`: Script to extract colors from frames.
  - `ExtractColorsRemaining.py`: Script to process remaining frames in case of interruptions.
  - `ExtractColorsREADME.md`: Documentation for the extracting colors scripts.
  
- **HowlsMovingCastle**
  - `MovieFile`: Directory containing the movie file (not included due to copyright).
  - `frames`: Directory where frames are stored during extraction.
  - `.DS_Store`: System file for directory structure.
  - `Howls_Color_Analysis.ipynb`: Jupyter Notebook for color analysis.
  - `howls_dominant_colors.csv`: CSV file with extracted dominant colors.


- **ScriptToAddToGCS**
  - *Obselete Since I didn't end up using this script, so can ignore.*
  - `README_extraction_upload.md`: Documentation for uploading extracted data to Google Cloud Storage.
  - `ScriptToExtractFrames.py`: Script to extract frames from the movie.
  - `ScriptToExtractFramesWindows.py`: Windows-compatible script to extract frames.
  - `test.py`: Test script for functionality verification.

### Root Files

- `.DS_Store`: System file for directory structure.
- `.gitattributes`: Git attributes for the repository.
- `.gitignore`: Git ignore file to exclude certain files and directories.

## Getting Started

### Prerequisites

- Python 3.x
- FFmpeg
- Required Python libraries: pandas, matplotlib, seaborn, plotly, scikit-learn, colorthief, etc.

### Installation

1. Clone the repository:
   

         git clone https://github.com/Rishab-Sudhir/Data-Science-Project---Outfits-from-Ghibli-Films.git
         cd Data-Science-Project---Outfits-from-Ghibli-Films


2. Install required python libraries:
   
         pip install -r requirements.txt

3. Ensure FFmpeg is installed and available in your system path.

## Usage

### Extracting Frames & Colors

1. Run the ExtractColors.py script to extract frames from the movie and then the dominant colors from frames:
   
         python ExtractingColors/ExtractColors.py

2. If the process is interrupted, you can resume with ExtractColorsRemaining.py:
   
         python ExtractingColors/ExtractColorsRemaining.py

### Analysis

3. Open Howls_Color_Analysis.ipynb in Jupyter Notebook to perform and visualize the color analysis.

## Contributions
Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
