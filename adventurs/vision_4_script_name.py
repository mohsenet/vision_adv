import ffmpeg
import subprocess
import os
import tempfile

def cut_and_concat_video(input_file, output_file, cut_start, cut_end):
    """
    Removes a specific segment from a video and concatenates the parts before and after.
    
    Args:
        input_file (str): Path to the input video file
        output_file (str): Path to save the output video
        cut_start (str): Start time of segment to remove in format "HH:MM:SS" or seconds
        cut_end (str): End time of segment to remove in format "HH:MM:SS" or seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Make sure the input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist")
        return False
    
    try:
        # Create temporary directory for intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Temp file paths
            first_part = os.path.join(temp_dir, "first_part.mp4")
            second_part = os.path.join(temp_dir, "second_part.mp4")
            concat_list = os.path.join(temp_dir, "concat_list.txt")
            
            # 1. Extract the first part (from beginning to cut_start)
            print(f"Extracting first part (0 to {cut_start})...")
            (
                ffmpeg
                .input(input_file, to=cut_start)
                .output(first_part, c='copy')
                .global_args('-y')
                .run(capture_stderr=True)
            )
            
            # 2. Extract the second part (from cut_end to end)
            print(f"Extracting second part (from {cut_end} to end)...")
            (
                ffmpeg
                .input(input_file, ss=cut_end)
                .output(second_part, c='copy')
                .global_args('-y')
                .run(capture_stderr=True)
            )
            
            # 3. Create a concat file
            with open(concat_list, 'w') as f:
                f.write(f"file '{first_part}'\n")
                f.write(f"file '{second_part}'\n")
            
            # 4. Concatenate the parts
            print("Concatenating parts...")
            cmd = [
                'ffmpeg',
                '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list,
                '-c', 'copy',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Successfully created {output_file}")
                return True
            else:
                print(f"Concatenation failed: {result.stderr}")
                
                # Try alternative approach if first method fails
                print("Trying alternative approach...")
                
                # Get file info to check streams
                probe = ffmpeg.probe(input_file)
                
                # Check if file has audio
                has_audio = any(stream['codec_type'] == 'audio' for stream in probe['streams'])
                
                # Create inputs
                input1 = ffmpeg.input(first_part)
                input2 = ffmpeg.input(second_part)
                
                # Join video streams
                v1 = input1.video
                v2 = input2.video
                joined_video = ffmpeg.concat(v1, v2, v=1, a=0)
                
                # Join audio streams if present
                if has_audio:
                    a1 = input1.audio
                    a2 = input2.audio
                    joined_audio = ffmpeg.concat(a1, a2, v=0, a=1)
                    # Output with joined video and audio
                    output = ffmpeg.output(joined_video, joined_audio, output_file)
                else:
                    # Output with only joined video
                    output = ffmpeg.output(joined_video, output_file)
                
                # Run ffmpeg
                output.global_args('-y').run(capture_stderr=True)
                
                print(f"Alternative method successful: Created {output_file}")
                return True
                
    except ffmpeg.Error as e:
        error_msg = e.stderr.decode('utf8') if hasattr(e, 'stderr') and e.stderr else str(e)
        print(f"Error during processing: {error_msg}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    
    return False

if __name__ == "__main__":
    import sys
    
    # Example usage
    input_file = "input.mp4"
    output_file = "output_with_cut.mp4"
    cut_start = "00:05:00"  # Start time of segment to remove
    cut_end = "00:10:00"    # End time of segment to remove
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    if len(sys.argv) > 3:
        cut_start = sys.argv[3]
    if len(sys.argv) > 4:
        cut_end = sys.argv[4]
    
    success = cut_and_concat_video(input_file, output_file, cut_start, cut_end)
    if success:
        print("Video processing completed successfully!")
    else:
        print("Video processing failed.")