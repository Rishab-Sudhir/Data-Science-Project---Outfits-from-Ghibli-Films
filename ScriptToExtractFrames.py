import os
import subprocess

def extract_frames(video_path, output_dir, fps=1, start_time=None):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Construct the FFmpeg command
    command = [
        'ffmpeg'
    ]

    if start_time:
        command += ['-ss', start_time]

    command += [
        '-i', video_path,
        '-vf', f'fps={fps}',
        '-start_number', str(start_number),
        os.path.join(output_dir, 'output_%04d.png')
    ]

    # Run the command
    subprocess.run(command, check=True)

def get_last_frame_number(output_dir):
    # Get the list of existing frame files
    frame_files = [f for f in os.listdir(output_dir) if f.startswith('output_') and f.endswith('.png')]
    if not frame_files:
        return 0
    
    # Extract frame numbers from file names
    frame_numbers = [int(f.split('_')[1].split('.')[0]) for f in frame_files]
    return max(frame_numbers) + 1

# Example usage
video_path = '/Users/rsudhir/Documents/GitHub/Data-Science-Project---Outfits-from-Ghibli-Films/HowlsMovingCastle/MovieFile/Howls.Moving.Castle.2004.720p.BluRay.x264-x0r.mkv'
output_dir = '/Users/rsudhir/Documents/GitHub/Data-Science-Project---Outfits-from-Ghibli-Films/HowlsMovingCastle/frames'
start_time = '01:54:39.039'
start_number = get_last_frame_number(output_dir)
extract_frames(video_path, output_dir, fps=24, start_time=start_time)


