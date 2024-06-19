# Frame Extraction and Color Processing

This repository contains scripts for extracting frames from a video and processing those frames to extract the dominant colors. The results are written to a CSV file. The scripts use FFmpeg for frame extraction and the ColorThief library for color extraction. Multiprocessing is employed to handle the extraction and processing concurrently.

## Scripts

1. Frame Extraction and Processing Script
This script extracts frames from a specified video file at a defined frame rate using FFmpeg. The frames are processed to extract the dominant colors, which are then written to a CSV file. The frames are deleted after processing to save disk space.

### How it Works

### 1. Frame Extraction:

- Frames are extracted from the video file using FFmpeg.
- The frame extraction process runs concurrently with the frame processing.

### 2. Color Extraction:

- Dominant colors are extracted from each frame using the ColorThief library.
- Extracted color data is written to a CSV file.

### 3. Multiprocessing:

- The script uses multiprocessing to handle frame extraction and processing concurrently.
- Debugging information is included to track the processing flow.

### Usage

1. Clone the repository.
2. Ensure you have FFmpeg and ColorThief installed.
3. Adjust the paths and parameters in the script as needed.
4. Run the script to extract and process frames.

## 2. Script to Process Remaining Frames

This script processes frames that have already been extracted and are stored locally. It queues the remaining frames in batches and processes them concurrently. The results are appended to the existing CSV file.

### How it Works

### 1. Frame Queueing:

- Remaining frames in the specified directory are queued in batches.
- The script uses multiprocessing to handle the processing concurrently.

### 2. Color Extraction:

- Dominant colors are extracted from each frame using the ColorThief library.
- Extracted color data is appended to the existing CSV file.

### 3. Frame Deletion:

- Frames are deleted after processing to save disk space.

### Usage

1. Ensure you have frames extracted and stored locally.
2. Adjust the paths and parameters in the script as needed.
3. Run the script to process the remaining frames and append the results to the CSV.