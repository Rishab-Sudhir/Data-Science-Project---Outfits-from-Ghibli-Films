import os
import subprocess
from multiprocessing import Process, Queue
from colorthief import ColorThief
import csv

"""
os: Provides a way of using operating system-dependent functionality like reading or writing to the file system.
subprocess: Allows you to spawn new processes, connect to their input/output/error pipes, and obtain their return codes.
multiprocessing: Supports spawning processes using an API similar to the threading module. It offers both local and remote concurrency.
colorthief: A library to extract the dominant color or a representative color palette from an image.
csv: Provides functionality to write and read data in CSV (Comma-Separated Values) format.

"""

def extract_dominant_colors(image_path, num_colors=10):
    color_thief = ColorThief(image_path)
    palette = color_thief.get_palette(color_count=num_colors)
    hex_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in palette]
    return hex_colors

"""
extract_dominant_colors: A function to extract the dominant colors from an image.
ColorThief(image_path): Creates an instance of ColorThief for the given image.
get_palette(color_count=num_colors): Gets a palette of num_colors dominant colors.
hex_colors: Converts the RGB values of the palette to hexadecimal format.
"""

def process_frames(output_dir, frame_queue, num_colors=10):
    while True:
        frames = frame_queue.get()
        if frames is None:
            break
        for local_frame_path in frames:
            try:
                colors = extract_dominant_colors(local_frame_path, num_colors)
                with open("dominant_colors.csv", "a") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([local_frame_path] + colors)
                os.remove(local_frame_path)  # Remove the file after processing
                print(f"Processed {local_frame_path}")
            except Exception as e:
                print(f"Failed to process {local_frame_path}: {e}")

"""
process_frames: A function to process frames from the queue.
frame_queue.get(): Retrieves a batch of frames from the queue.
if frames is None: Checks if there are no more frames to process.
extract_dominant_colors: Extracts the dominant colors from each frame.
with open("dominant_colors.csv", "a") as csvfile: Opens the CSV file in append mode.
writer.writerow([local_frame_path] + colors): Writes the frame path and its dominant colors to the CSV file.
os.remove(local_frame_path): Deletes the frame file after processing.
print(f"Processed {local_frame_path}"): Prints a message indicating the frame has been processed.
except Exception as e: Catches any exceptions that occur during processing.
"""

def extract_and_queue_frames(video_path, output_dir, frame_queue, fps=1, start_time=None, batch_size=100):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    command = ['ffmpeg']
    if start_time:
        command += ['-ss', start_time]
    command += [
        '-i', video_path,
        '-vf', f'fps={fps}',
        os.path.join(output_dir, 'output_%07d.png')
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
            if frame_files:
                for frame_file in frame_files:
                    local_frame_path = os.path.join(output_dir, frame_file)
                    batch.append(local_frame_path)
                    if len(batch) >= batch_size:
                        frame_queue.put(batch)
                        print(f"Queued batch of {len(batch)} frames for processing")
                        batch = []
        
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
    start_time = '00:00:15'

    frame_queue = Queue()

    processor_process = Process(target=process_frames, args=(output_dir, frame_queue))
    processor_process.start()

    extract_and_queue_frames(video_path, output_dir, frame_queue, fps=24, start_time=start_time, batch_size=300)

    processor_process.join()
