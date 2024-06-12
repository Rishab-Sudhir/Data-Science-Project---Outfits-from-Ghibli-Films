import os
import subprocess
from google.cloud import storage
from multiprocessing import Process, Queue
from threading import Thread
import time

def upload_to_gcs(bucket_name, frame_queue):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\rohan\OneDrive\Documents\GitHub\Data-Science-Project---Outfits-from-Ghibli-Films\data-science-project-ghibli-7da755faf350.json"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    def upload_frame(local_frame_path, gcs_frame_path):
        try:
            blob = bucket.blob(gcs_frame_path)
            blob.upload_from_filename(local_frame_path)
            print(f"Uploaded {local_frame_path} to GCS")
            try:
                os.remove(local_frame_path)
                print(f"Removed {local_frame_path}")
            except Exception as e:
                print(f"Failed to remove {local_frame_path}: {e}")
        except Exception as e:
            print(f"Failed to upload {local_frame_path}: {e}")

    while True:
        print("Waiting for frames to upload...")
        frames = frame_queue.get()
        if frames is None:
            print("No more frames to upload. Exiting.")
            break
        print(f"Uploading batch of {len(frames)} frames")
        threads = []
        for local_frame_path, gcs_frame_path in frames:
            thread = Thread(target=upload_frame, args=(local_frame_path, gcs_frame_path))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        print(f"Batch upload complete.")

def extract_and_queue_frames(video_path, output_dir, bucket_name, movie_name, fps=1, start_time=None, frame_queue=None, batch_size=300):
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
        os.path.join(output_dir, 'output_%05d.png')  # Adjusted to 5 digits for consistency
    ]

    # Run the FFmpeg command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("FFmpeg command started...")

    time.sleep(10)

    frame_count = 0
    processed_files = set()

    try:
        while True:
            output = process.stderr.readline()
            if process.poll() is not None:
                break
            if output:
                print(output.decode().strip())

            # Small delay to ensure frames are written to the directory
            time.sleep(0.5)

            # Collect frames and queue them in batches
            frame_files = [f for f in os.listdir(output_dir) if f.startswith('output_') and f.endswith('.png') and f not in processed_files]
            frame_files.sort()
            print(f"Found {len(frame_files)} frame files.")
            batch = []
            if frame_files:
                for frame_file in frame_files[:batch_size]:
                    frame_count += 1
                    local_frame_path = os.path.join(output_dir, frame_file)
                    gcs_frame_path = f"{movie_name}/frames/{frame_file}"
                    batch.append((local_frame_path, gcs_frame_path))
                    processed_files.add(frame_file)
                
                if batch:
                    frame_queue.put(batch)
                    print(f"Queued batch of {len(batch)} frames for upload")

                    # Wait for the uploader to finish processing the current batch
                    while not frame_queue.empty():
                        time.sleep(1)
                
                # Small delay to ensure frames are processed correctly
                time.sleep(0.5)

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
    video_path = r"C:\Users\rohan\OneDrive\Documents\GitHub\Data-Science-Project---Outfits-from-Ghibli-Films\HowlsMovingCastle\MovieFile\Howls.Moving.Castle.2004.1080p.BluRay.x264-[YTS.AM].mp4"
    output_dir = r"C:\Users\rohan\OneDrive\Documents\GitHub\Data-Science-Project---Outfits-from-Ghibli-Films\HowlsMovingCastle\frames"

    bucket_name = 'ghibli-movie-frames'
    movie_name = 'howls-moving-castle'
    start_time = '00:00:15'

    # Create a queue to handle frame paths
    frame_queue = Queue()

    # Start the upload process
    uploader_process = Process(target=upload_to_gcs, args=(bucket_name, frame_queue))
    uploader_process.start()

    # Extract frames and queue them for uploading
    extract_and_queue_frames(video_path, output_dir, bucket_name, movie_name, fps=24, start_time=start_time, frame_queue=frame_queue, batch_size=100)

    # Wait for the uploader process to finish
    uploader_process.join()
