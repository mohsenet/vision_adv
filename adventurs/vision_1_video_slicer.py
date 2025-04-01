import ffmpeg
import subprocess
import os
import sys

def slice_video(input_file, output_file, start_time, end_time):
    """
    Slice a video using multiple methods, ensuring audio is preserved.
    
    Args:
        input_file (str): Path to the input video file
        output_file (str): Path to save the output video
        start_time (str): Start time in format "HH:MM:SS" or seconds
        end_time (str): End time in format "HH:MM:SS" or seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Make sure the input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist")
        return False
    
    # Method 1: Using filter_complex with audio streams explicitly mapped
    try:
        print(f"Attempting Method 1: filter complex with explicit audio mapping...")
        
        # Get information about input file
        probe = ffmpeg.probe(input_file)
        
        # Check if file has audio
        has_audio = any(stream['codec_type'] == 'audio' for stream in probe['streams'])
        
        # Create base input
        input_stream = ffmpeg.input(input_file)
        
        # Apply trim filter to video and audio separately
        video = (
            input_stream.video
            .trim(start=start_time, end=end_time)
            .setpts('PTS-STARTPTS')
        )
        
        if has_audio:
            audio = (
                input_stream.audio
                .filter_('atrim', start=start_time, end=end_time)
                .filter_('asetpts', 'PTS-STARTPTS')
            )
            # Join video and audio
            output = ffmpeg.output(video, audio, output_file)
        else:
            output = ffmpeg.output(video, output_file)
        
        # Run with overwrite and capture stderr
        output.global_args('-y').run(capture_stderr=True)
        
        print(f"Method 1 successful: Created {output_file}")
        return True
    except ffmpeg.Error as e:
        error_msg = e.stderr.decode('utf8') if hasattr(e, 'stderr') and e.stderr else str(e)
        print(f"Method 1 failed: {error_msg}")
    
    # Method 2: Using ss and to with separate audio and video streams
    try:
        print(f"Attempting Method 2: ss/to with explicit audio mapping...")
        
        # Get information about input file
        probe = ffmpeg.probe(input_file)
        
        # Check if file has audio
        has_audio = any(stream['codec_type'] == 'audio' for stream in probe['streams'])
        
        # Create base input with seeking
        input_stream = ffmpeg.input(input_file, ss=start_time, to=end_time)
        
        # Map all streams
        args = {
            'map': '0',      # Include all streams
            'c:v': 'copy',   # Copy video codec
        }
        
        if has_audio:
            args['c:a'] = 'copy'  # Copy audio codec
        
        # Output with global args
        (
            input_stream
            .output(output_file, **args)
            .global_args('-y')
            .run(capture_stderr=True)
        )
        
        print(f"Method 2 successful: Created {output_file}")
        return True
    except ffmpeg.Error as e:
        error_msg = e.stderr.decode('utf8') if hasattr(e, 'stderr') and e.stderr else str(e)
        print(f"Method 2 failed: {error_msg}")
    
    # Method 3: Two-pass approach with explicit audio encoding (most reliable)
    try:
        print(f"Attempting Method 3: Two-pass approach with explicit audio...")
        cmd = [
            'ffmpeg',
            '-y',
            '-ss', start_time,
            '-i', input_file,
            '-to', f"{end_time}",
            '-map', '0',          # Include all streams
            '-c:v', 'libx264',    # Re-encode video
            '-c:a', 'aac',        # Re-encode audio to AAC
            '-strict', 'experimental',
            '-b:a', '192k',       # Good audio quality
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Method 3 successful: Created {output_file}")
            return True
        else:
            print(f"Method 3 failed: {result.stderr}")
    except Exception as e:
        print(f"Method 3 failed with exception: {str(e)}")
    
    # Method 4: Using direct subprocess call with precise options
    try:
        print(f"Attempting Method 4: Direct FFmpeg with precise options...")
        
        # Calculate duration if times are in HH:MM:SS format
        if ":" in start_time and ":" in end_time:
            # Convert HH:MM:SS to seconds
            def time_to_seconds(time_str):
                h, m, s = time_str.split(':')
                return int(h) * 3600 + int(m) * 60 + float(s)
            
            duration = time_to_seconds(end_time) - time_to_seconds(start_time)
        else:
            # Assume they're already in seconds
            duration = float(end_time) - float(start_time)
        
        cmd = [
            'ffmpeg',
            '-y',
            '-i', input_file,
            '-ss', start_time,
            '-t', str(duration),
            '-map', '0:v:0',     # Map video stream
            '-map', '0:a?',      # Map audio stream if present
            '-c:v', 'libx264',   # Video codec 
            '-c:a', 'aac',       # Audio codec
            '-b:a', '192k',      # Audio bitrate
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Method 4 successful: Created {output_file}")
            return True
        else:
            print(f"Method 4 failed: {result.stderr}")
    except Exception as e:
        print(f"Method 4 failed with exception: {str(e)}")
    
    # If all methods failed
    print("All slicing methods failed.")
    return False

if __name__ == "__main__":
    # Example usage
    input_file = "input.mp4"
    output_file = "output.mp4"
    start_time = "00:18:10"
    end_time = "00:24:10"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    if len(sys.argv) > 3:
        start_time = sys.argv[3]
    if len(sys.argv) > 4:
        end_time = sys.argv[4]
    
    success = slice_video(input_file, output_file, start_time, end_time)
    if success:
        print("Video slicing completed successfully with audio preserved.")
    else:
        print("Video slicing failed.")