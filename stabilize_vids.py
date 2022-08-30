"""
A smol script to apply ffmpeg vidstab stabilization in batch mode to turn all videos in a directory buttery

Example usages:
Generate stabilized vids in the /Users/matthewtse/test directory from all .MP4 files with default settings
```python3 stabilize_vids.py -p /Users/matthewtse/tsety/test```

Generate stabilized vids in the /Users/matthewtse/test directory from all .mov files, and generate side by side comparison vids
```python3 stabilize_vids.py -p /Users/matthewtse/tsety/test -c -e .mov```

Generate extra smooth stabilized vids in the /Users/matthewtse/test directory (smoothing is at 10 by default)
```python3 stabilize_vids.py -p /Users/matthewtse/tsety/test -a smoothing=30```


Pre-reqs: 
brew install ffmpeg
brew install libvidstab

Additional resources:
http://underpop.online.fr/f/ffmpeg/help/vidstabtransform.htm.gz <-- for more fine tuning the stabilization
http://underpop.online.fr/f/ffmpeg/help/vidstabdetect.htm.gz

Made by Matt Tse :)
"""

import sys
import getopt
import subprocess
import glob
import os

def get_output_path(input_vid_path, output_dir):
    """
    Takes an input video path and generate the corresponding output video path/dir
    """
    last_dash_in_path = input_vid_path.rfind("/")
    period_before_extension = input_vid_path.rfind(".")
    output_vid_path = output_dir + input_vid_path[last_dash_in_path:period_before_extension] + "-s.MP4"
    return output_vid_path

def run_stabilization_cmd(input_vid_path, output_vid_path, additional_args, generate_comparison_video = False):
    """
    Takes a video input path and run ffmpeg/vidstabtransform to generate stabilized videos to the output dir
    """
    gen_stab_data_cmd = f"ffmpeg -i {input_vid_path} -vf vidstabdetect -f null -".split()
    transforms_gen_vid_cmd = f"ffmpeg -i {input_vid_path} -vf vidstabtransform{additional_args} {output_vid_path}".split()
    

    # Generate vid transform data
    subprocess.run(gen_stab_data_cmd, check=True, text=True)

    # Use the transform data to generate a stabilized video
    subprocess.run(transforms_gen_vid_cmd, check=True, text=True)

    # Make a comparison vid
    if generate_comparison_video:
        output_comparison_vid_path = output_vid_path.replace("-s","-c")
        gen_comparison_video_command = f"ffmpeg -i {input_vid_path} -i {output_vid_path} -filter_complex hstack {output_comparison_vid_path}".split()
        subprocess.run(gen_comparison_video_command, check=True, text=True)
    
    # Clean up
    os.remove("transforms.trf")

    return True

def parse_cmd_input(args):
    """
    Parses the python script inputs: 
    dir: the path of which you want to run the stabilization 
    extension: extensions of the files in the path to apply it to
    additional_args: additional vidstabtransform arguments to be passed in
    pre__post_comparison_enabled: generates an extra side by side comparison video *takes longer to process
    """
    dir_path = ""
    extension = ".MP4" # Default to parsing videos ending in .MP4 (all caps)
    additional_args = ""
    pre_post_comparison_enabled = False

    try:
        opts, args = getopt.getopt(args, "cp:e:a:")
    except getopt.GetoptError:
        print('Usage: python3 stabilize_vids.py -p <folder_path> -c -e <optional_custom_extension>')
        sys.exit(2)
    print(f'args: {opts}')
    for opt, arg in opts:
        if opt == '-c':
            print(f'Pre/post stabilization video comparison output enabled, extra side by side comparison video will be generated')
            pre_post_comparison_enabled = True
        elif opt == '-p':
            dir_path = arg
        elif opt == '-e':
            print(f'Converting all files with {arg} extension')
            extension = arg
        elif opt == '-a':
            print(f'Using additional vidstabtransform arguments')
            additional_args = f"={arg}"

    if not dir_path:
        print('Missing path arguments! -p <folder_path> must be specified')
        sys.exit(2)
    
    return dir_path, extension, additional_args, pre_post_comparison_enabled

def get_file_names_in_folder(dir, extension):
    file_names = glob.glob(dir + f"/*{extension}")
    print(f"file_names {file_names}")
    return file_names

def main(argv):
    dir, extension, additional_args, pre_post_comparison_enabled = parse_cmd_input(argv)
    
    output_dir = dir + "/stabilized"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for input_vid_path in get_file_names_in_folder(dir, extension):
        print(f"processing {input_vid_path}")
        run_stabilization_cmd(input_vid_path, get_output_path(input_vid_path, output_dir), additional_args, pre_post_comparison_enabled)

    print(f"completed processing files in {dir}! We're all done here")

if __name__ == "__main__":
   main(sys.argv[1:])