import os
import cv2

def capture_screenshot(video_path: str, output_dir: str = "screenshots"):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the video
    vid_obj = cv2.VideoCapture(video_path)
    fps = vid_obj.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 30  # Default to 30 FPS if unable to read

    frame_interval = int(fps * 10)  # Capture every 10 seconds
    frames = []
    count = 0

    try:
        while True:
            success, frame = vid_obj.read()
            if not success:
                break
            if count % frame_interval == 0:
                frame_path = os.path.join(output_dir, f"screenshot_{count}.png")
                cv2.imwrite(frame_path, frame)
                frames.append(frame_path)
            count += 1
    except Exception as e:
        print(f"Error capturing screenshots: {e}")
    finally:
        vid_obj.release()

    return frames

import subprocess
import os

def convert_webm_to_png(webm_path: str) -> str:
    try:
        png_path = os.path.splitext(webm_path)[0] + ".png"
        command = [
            "ffmpeg",
            "-i", webm_path,
            "-vf", "fps=1",
            "-vframes", "1",
            png_path
        ]
        subprocess.run(command, check=True)
        return png_path if os.path.exists(png_path) else None
    except Exception as e:
        logging.error(f"Failed to convert webm to PNG: {e}")
        return None

