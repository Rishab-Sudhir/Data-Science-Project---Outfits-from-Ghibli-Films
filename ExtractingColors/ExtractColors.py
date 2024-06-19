import os
import subprocess
from multiprocessing import Process, Queue
from colorthief import ColorThief
import csv
import time

def extract_dominant_colors(image_path, num_colors=10):
    try:
        color_thief = ColorThief(image_path)
        palette = color_thief.get_palette(color_count=num_colors)
        return palette  # Return the palette directly as RGB tuples
    except Exception as e:
        print(f"Error extracting colors from {image_path}: {e}")
        return []

def process_frames(frame_queue, num_colors=10):
    csv_file = "dominant_colors.csv"
    if not os.path.exists(csv_file):
        with open(csv_file, "w") as csvfile:
            writer = csv.writer(csvfile)
            header = ["frame_path"]
            for i in range(num_colors):
                header += [f"color_{i+1}_r", f"color_{i+1}_g", f"color_{i+1}_b"]
            writer.writerow(header)
            print(f"CSV header written: {header}")

    while True:
        print("Waiting for frames to process...")
        frames = frame_queue.get()
        if frames is None:
            print("Received termination signal. Exiting process_frames.")
            break
        print(f"Processing batch of {len(frames)} frames...")
        for local_frame_path in frames:
            try:
                colors = extract_dominant_colors(local_frame_path, num_colors)
                if colors:
                    with open(csv_file, "a") as csvfile:
                        writer = csv.writer(csvfile)
                        row = [local_frame_path]
                        for r, g, b in colors:
                            row += [r, g, b]
                        writer.writerow(row)
                        print(f"Written to CSV: {row}")
                    os.remove(local_frame_path)  # Remove the file after processing
                    print(f"Processed and deleted {local_frame_path}")
            except Exception as e:
                print(f"Failed to process {local_frame_path}: {e}")

def extract_and_queue_frames(video_path, output_dir, frame_queue, fps=3, start_time=None, batch_size=10):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

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
            for frame_file in frame_files:
                local_frame_path = os.path.join(output_dir, frame_file)
                batch.append(local_frame_path)
                if len(batch) >= batch_size:
                    frame_queue.put(batch)
                    print(f"Queued batch of {len(batch)} frames for processing")
                    batch = []

            time.sleep(1)  # Sleep to simulate processing time and prevent excessive loop iteration

        if batch:
            frame_queue.put(batch)
            print(f"Queued final batch of {len(batch)} frames for processing")

    except KeyboardInterrupt:
        process.terminate()
        print("Process interrupted and terminated.")

    frame_queue.put(None)
    print("Frame extraction completed.")

if __name__ == "__main__":
    video_path = '/Users/rsudhir/Documents/GitHub/Data-Science-Project---Outfits-from-Ghibli-Films/HowlsMovingCastle/MovieFile/Howls.Moving.Castle.2004.720p.BluRay.x264-x0r.mkv'
    output_dir = '/Users/rsudhir/Documents/GitHub/Data-Science-Project---Outfits-from-Ghibli-Films/HowlsMovingCastle/frames'
    start_time = '00:00:00'

    frame_queue = Queue()

    # Start the frame processing process
    processor_process = Process(target=process_frames, args=(frame_queue,))
    processor_process.start()

    # Extract frames and queue them for processing
    extract_process = Process(target=extract_and_queue_frames, args=(video_path, output_dir, frame_queue, 3, start_time, 10))
    extract_process.start()

    # Wait for the processes to finish
    extract_process.join()
    frame_queue.put(None)  # Ensure the processing loop terminates
    processor_process.join()
