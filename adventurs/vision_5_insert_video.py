import ffmpeg
import subprocess
import os
import tempfile

def insert_video_at_time(main_video, insert_video, output_file, insert_time):
    """
    Inserts a video clip at a specific time position in the main video.
    
    Args:
        main_video (str): Path to the main video file
        insert_video (str): Path to the video clip to insert
        output_file (str): Path to save the resulting video
        insert_time (str): Position to insert the clip in format "HH:MM:SS" or seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(main_video):
        print(f"Error: Main video '{main_video}' does not exist")
        return False
    if not os.path.exists(insert_video):
        print(f"Error: Insert video '{insert_video}' does not exist")
        return False
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            first_part = os.path.join(temp_dir, "first_part.mp4")
            second_part = os.path.join(temp_dir, "second_part.mp4")
            concat_list = os.path.join(temp_dir, "concat_list.txt")

            # Extract the first part (from start to insert_time)
            print(f"Extracting first part (0 to {insert_time})...")
            ffmpeg.input(main_video).output(first_part, vcodec='libx264', acodec='aac', r=30, g=30, to=insert_time).overwrite_output().run()
            # (
            #     ffmpeg
            #     .input(main_video)
            #     .output(first_part, c='copy', to=insert_time)
            #     .overwrite_output()
            #     .run(capture_stderr=True)
            # )
            
            # Extract the second part (from insert_time to end)
            print(f"Extracting second part (from {insert_time} to end)...")
            ffmpeg.input(main_video, ss=insert_time).output(second_part, vcodec='libx264', acodec='aac', r=30, g=30).overwrite_output().run()
            # (
            #     ffmpeg
            #     .input(main_video, ss=insert_time)
            #     .output(second_part, c='copy')
            #     .overwrite_output()
            #     .run(capture_stderr=True)
            # )

            # Ensure all files have the same codec by re-encoding them if necessary
            reencoded_insert = os.path.join(temp_dir, "insert_video_reencoded.mp4")
            print("Re-encoding insert video for compatibility...")
            reencoded_insert = os.path.join(temp_dir, "reencoded_insert.mp4")
            
            (
                ffmpeg
                .input(insert_video)
                .output(reencoded_insert, vcodec='libx264', acodec='aac', **{'b:a': '192k'}, g=30, r=30)
                .overwrite_output()
                .run(capture_stderr=True)
            )


            # Create a concat file
            with open(concat_list, 'w') as f:
                f.write(f"file '{first_part}'\n")
                f.write(f"file '{reencoded_insert}'\n")
                f.write(f"file '{second_part}'\n")
            
            
            # Concatenate all parts
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
                
                # Try alternative approach with re-encoding if first method fails
                print("Trying alternative approach with re-encoding...")
                cmd_alt = [
                    'ffmpeg',
                    '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concat_list,
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    output_file
                ]
                
                result_alt = subprocess.run(cmd_alt, capture_output=True, text=True)
                
                if result_alt.returncode == 0:
                    print(f"Alternative method successful: Created {output_file}")
                    return True
                else:
                    print(f"Alternative method failed: {result_alt.stderr}")
                    return False
                
    except ffmpeg.Error as e:
        error_msg = e.stderr.decode('utf8') if hasattr(e, 'stderr') and e.stderr else str(e)
        print(f"Error during processing: {error_msg}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    
    return False

if __name__ == "__main__":
    import sys
    
    # Example usage
    main_video = "input.mp4"
    insert_video = "part_1.mp4"
    output_file = "insert_video.mp4"
    insert_time = "00:00:10"  # Position to insert the clip
    
    if len(sys.argv) > 1:
        main_video = sys.argv[1]
    if len(sys.argv) > 2:
        insert_video = sys.argv[2]
    if len(sys.argv) > 3:
        output_file = sys.argv[3]
    if len(sys.argv) > 4:
        insert_time = sys.argv[4]
    
    success = insert_video_at_time(main_video, insert_video, output_file, insert_time)
    if success:
        print("Video insertion completed successfully!")
    else:
        print("Video insertion failed.")
