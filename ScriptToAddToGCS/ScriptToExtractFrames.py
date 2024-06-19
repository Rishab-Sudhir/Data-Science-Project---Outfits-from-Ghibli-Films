import os
import subprocess
from google.cloud import storage
from multiprocessing import Process, Queue
import time

def upload_to_gcs(bucket_name, frame_queue):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    while True:
        frames = frame_queue.get()
        if frames is None:
            break
        for local_frame_path, gcs_frame_path in frames:
            try:
                blob = bucket.blob(gcs_frame_path)
                blob.upload_from_filename(local_frame_path)
                os.remove(local_frame_path)  # Remove the file after uploading
                print(f"Uploaded {local_frame_path} to GCS")
            except Exception as e:
                print(f"Failed to upload {local_frame_path}: {e}")

def extract_and_queue_frames(video_path, output_dir, bucket_name, movie_name, fps=1, start_time=None, frame_queue=None, batch_size=100):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Construct the FFmpeg command
    command = ['ffmpeg']
    if start_time:
        command += ['-ss', start_time]
    command += [
        '-i', video_path,
        '-vf', f'fps={fps}',
        os.path.join(output_dir, 'output_%04d.png')
    ]

    # Run the FFmpeg command
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

            # Collect frames and queue them in batches
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

if __name__ == "__main__":
    # Example usage
    video_path = '/Users/rsudhir/Documents/GitHub/Data-Science-Project---Outfits-from-Ghibli-Films/HowlsMovingCastle/MovieFile/Howls.Moving.Castle.2004.720p.BluRay.x264-x0r.mkv'
    output_dir = '/Users/rsudhir/Documents/GitHub/Data-Science-Project---Outfits-from-Ghibli-Films/HowlsMovingCastle/frames'
    bucket_name = 'ghibli-movie-frames'
    movie_name = 'howls-moving-castle'
    start_time = '00:00:00'

    # Create a queue to handle frame paths
    frame_queue = Queue()

    # Start the upload process
    uploader_process = Process(target=upload_to_gcs, args=(bucket_name, frame_queue))
    uploader_process.start()

    # Extract frames and queue them for uploading
    extract_and_queue_frames(video_path, output_dir, bucket_name, movie_name, fps=24, start_time=start_time, frame_queue=frame_queue, batch_size=300)

    # Wait for the uploader process to finish
    uploader_process.join()
