import os
from multiprocessing import Process, Queue
from colorthief import ColorThief
import csv

def extract_dominant_colors(image_path, num_colors=10):
    try:
        color_thief = ColorThief(image_path)
        palette = color_thief.get_palette(color_count=num_colors)
        return palette  # Return the palette directly as RGB tuples
    except Exception as e:
        print(f"Error extracting colors from {image_path}: {e}")
        return []

def process_frames(frame_queue, csv_file, num_colors=10):
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

def queue_remaining_frames(output_dir, frame_queue, batch_size=10):
    frame_files = [f for f in os.listdir(output_dir) if f.startswith('output_') and f.endswith('.png')]
    frame_files.sort()
    batch = []

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

    frame_queue.put(None)
    print("All frames have been queued.")

if __name__ == "__main__":
    output_dir = '/Users/rsudhir/Documents/GitHub/Data-Science-Project---Outfits-from-Ghibli-Films/HowlsMovingCastle/frames'
    csv_file = "dominant_colors.csv"  # Existing CSV file

    frame_queue = Queue()

    # Start the frame processing process
    processor_process = Process(target=process_frames, args=(frame_queue, csv_file))
    processor_process.start()

    # Queue remaining frames for processing
    queue_remaining_frames(output_dir, frame_queue, batch_size=10)

    # Wait for the processing process to finish
    processor_process.join()
