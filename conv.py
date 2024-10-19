import os
import cv2
import ffmpeg
from PIL import Image

def get_video_metadata(video_file):
    """Extract video metadata like width, height, bitrate, framerate, etc."""
    probe = ffmpeg.probe(video_file)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    
    if video_stream is None:
        raise ValueError("No video stream found in the file.")
    
    metadata = {
        'width': int(video_stream['width']),
        'height': int(video_stream['height']),
        'bit_rate': int(video_stream['bit_rate']),
        'frame_rate': eval(video_stream['r_frame_rate']),  # '30000/1001' to float
        'duration': float(video_stream['duration']),
    }
    
    return metadata

def extract_frames(video_file, output_folder, target_width, target_height, bit_depth):
    """Extract frames from a video and save them as PNG images with consistent bit depth."""
    # open vid
    cap = cv2.VideoCapture(video_file)

    if not cap.isOpened():
        print("Error: Could not open video file.")
        return
    
    # create folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # exit when vid end
        
        # resize
        resized_frame = cv2.resize(frame, (target_width, target_height))

        # Convert the frame from BGR (OpenCV format) to RGB (PIL format)
        image = Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB))
        
        # Set consistent bit depth (if needed, adjust here based on your requirement)
        if bit_depth == 8:
            image = image.convert('RGB')  # 8-bit depth for standard images
        elif bit_depth == 16:
            image = image.convert('I;16')  # 16-bit depth
        
        # Save the image as PNG
        output_file = os.path.join(output_folder, f"frame_{frame_count:04d}.png")
        image.save(output_file)
        frame_count += 1
    
    cap.release()
    print(f"Extracted {frame_count} frames to {output_folder}")

if __name__ == "__main__":
    # Input video file
    video_file = 'badapple.mp4'
    
    # Target output folder
    output_folder = 'apple'

    # Specify target width, height, and bit depth
    target_width = 64
    target_height = 36
    bit_depth = 8  # Set to 8 or 16 depending on your requirement

    # Get video metadata
    metadata = get_video_metadata(video_file)
    print("Video Metadata:", metadata)

    # Extract frames and save as PNG images
    extract_frames(video_file, output_folder, target_width, target_height, bit_depth)
