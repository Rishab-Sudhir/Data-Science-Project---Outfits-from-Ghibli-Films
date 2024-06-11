# Frame Extraction and Upload Script

This script is designed to extract frames from a video file and upload them to Google Cloud Storage (GCS). The process is optimized using batching and multiprocessing to handle large video files efficiently.

## How It Works

The script performs the following steps:

1. **Extract Frames**: Using FFmpeg, the script extracts frames from the video file at a specified frame rate.
2. **Batch Uploads**: Frames are collected into batches and uploaded to GCS. This reduces the number of API calls and optimizes the upload process.
3. **Multiprocessing**: The extraction and uploading processes run in parallel using Python's multiprocessing module, enhancing performance.

## Script Components

### 1. Upload Function

The `upload_to_gcs` function handles uploading frames to GCS as they are created.

```python
def upload_to_gcs(bucket_name, frame_queue):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    while True:
        frames = frame_queue.get()
        if frames are None:
            break
        for local_frame_path, gcs_frame_path in frames:
            try:
                blob = bucket.blob(gcs_frame_path)
                blob.upload_from_filename(local_frame_path)
                os.remove(local_frame_path)  # Remove the file after uploading
                print(f"Uploaded {local_frame_path} to GCS")
            except Exception as e:
                print(f"Failed to upload {local_frame_path}: {e}")
```

### 2. Frame Extraction and Queuing Function

The extract_and_queue_frames function extracts frames from the video and queues them in batches for uploading.

```python
def extract_and_queue_frames(video_path, output_dir, bucket_name, movie_name, fps=1, start_time=None, frame_queue=None, batch_size=100):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    command = ['ffmpeg']
    if start_time:
        command += ['-ss', start_time]
    command += [
        '-i', video_path,
        '-vf', f'fps={fps}',
        os.path.join(output_dir, 'output_%04d.png')
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("FFmpeg command started...")

    frame_count = 0
    batch = []

    try:
        while True:
            output = process.stderr.readline()
            if process.poll() is not None:
                break
            if output:
                print(output.decode().strip())

            frame_files = [f for f in os.listdir(output_dir) if f.startswith('output_') and f.endswith('.png')]
            frame_files.sort()
            if frame_files:
                for frame_file in frame_files:
                    frame_count += 1
                    local_frame_path = os.path.join(output_dir, frame_file)
                    gcs_frame_path = f"{movie_name}/frames/{frame_file}"
                    batch.append((local_frame_path, gcs_frame_path))
                    if len(batch) >= batch_size:
                        frame_queue.put(batch)
                        print(f"Queued batch of {len(batch)} frames for upload")
                        batch = []
        
        if batch:
            frame_queue.put(batch)
            print(f"Queued final batch of {len(batch)} frames for upload")

    except KeyboardInterrupt:
        process.terminate()
        print("Process interrupted and terminated.")
    
    frame_queue.put(None)
    print(f"Total frames processed: {frame_count}")
```

### 3. Main Execution
Starts the processes and manages the overall workflow.

```python
if __name__ == "__main__":
    # Example usage
    video_path = '/path/to/your/video/file.mkv'
    output_dir = '/path/to/output/directory'
    bucket_name = 'your-gcs-bucket-name'
    movie_name = 'your-movie-name'
    start_time = '00:00:00'

    frame_queue = Queue()

    uploader_process = Process(target=upload_to_gcs, args=(bucket_name, frame_queue))
    uploader_process.start()

    extract_and_queue_frames(video_path, output_dir, bucket_name, movie_name, fps=24, start_time=start_time, frame_queue=frame_queue, batch_size=300)

    uploader_process.join()

```

## Configuration

- **video_path**: Path to the video file.
- **output_dir**: Directory to store extracted frames.
- **bucket_name**: Google Cloud Storage bucket name.
- **movie_name**: Name of the movie for organizing frames in GCS.
- **start_time**: Starting time for frame extraction.
- **fps**: Frames per second for extraction.
- **batch_size**: Number of frames per batch for uploading.

## How to Use

1. **Set Up Google Cloud Storage**: Ensure you have a GCS bucket and appropriate credentials.
2. **Install Dependencies**: Ensure you have FFmpeg and `google-cloud-storage` installed.
3. **Run the Script**: Execute the script with the appropriate parameters.

### Setting Up Google Cloud Storage

- **Create a Bucket**: Create a GCS bucket to store the frames.
- **Service Account**: Create a service account with necessary permissions and download the JSON key file.
- **Environment Variable**: Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your service account JSON key file.

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-file.json"
```

### Installing Dependencies

```bash
pip install google-cloud-storage
pip install ffmpeg
```

### Running the Script
Ensure the script is executed with correct paths and parameters as shown in the example usage.

### Notes

**Performance**: Adjust the batch_size based on your system's memory and network performance.
**Monitoring**: Monitor the process for any interruptions or errors and adjust parameters as needed.