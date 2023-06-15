import subprocess
import os
import glob
import logging
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

# Get the path to the script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))

# Set the log file path relative to the script's directory
log_file_path = os.path.join(script_dir, 'ripit.log')

# Configure the logging
logging.basicConfig(filename=log_file_path, level=logging.INFO)

# Create a function to handle the button click event
def merge_files():
    # Get the YouTube URL from the entry widget
    youtube_url = url_entry.get()

    # Close the dialog box
    prompt_window.destroy()

    # Download the video and audio separately using yt-dlp
    video_file = os.path.expanduser("~/Desktop/%(title)s_video.%(ext)s")
    audio_file = os.path.expanduser("~/Desktop/%(title)s_audio.%(ext)s")
    download_video = subprocess.run(["yt-dlp", "-o", video_file, "-f", "bestvideo[ext=mp4]", youtube_url], capture_output=True)
    download_audio = subprocess.run(["yt-dlp", "-o", audio_file, "-f", "bestaudio[ext=m4a]", youtube_url], capture_output=True)

    # Check if there are any errors during the subprocess calls
    if download_video.returncode != 0 or download_audio.returncode != 0:
        error_msg = "Failed to download video or audio file."
        logging.error(error_msg)
        messagebox.showerror("Error", error_msg)
        return

    # Find the downloaded video and audio files
    video_file = glob.glob(os.path.expanduser("~/Desktop/*_video.mp4"))
    audio_file = glob.glob(os.path.expanduser("~/Desktop/*_audio.m4a"))

    # Check if the video and audio files exist
    if not video_file or not audio_file:
        error_msg = "Failed to find video or audio file."
        logging.error(error_msg)
        messagebox.showerror("Error", error_msg)
        return

    # Extract the filename without the extension
    video_file_name = os.path.splitext(os.path.basename(video_file[0]))[0]

    # Define the output filename
    output_file = os.path.expanduser(f"~/Desktop/{video_file_name}_merged.mp4")

    # Check if the output file already exists
    if os.path.exists(output_file):
        overwrite = messagebox.askyesno("Confirmation", "The output file already exists. Do you want to overwrite it?")
        if not overwrite:
            print("Merge operation aborted.")
            return

    # Merge the video and audio using FFmpeg with progress indicator
    merge_command = [
        "ffmpeg",
        "-i", video_file[0],
        "-i", audio_file[0],
        "-c:v", "copy",
        "-c:a", "copy",
        "-y",  # Automatically overwrite the output file
        output_file
    ]

    execute_ffmpeg_command(merge_command)

    # Handle potential errors during the merge process
    if os.path.exists(output_file):
        # Remove the temporary video and audio files
        os.remove(video_file[0])
        os.remove(audio_file[0])
        success_msg = "Video downloaded and merged successfully!"
        logging.info(success_msg)
        messagebox.showinfo("Success", success_msg)
        print(success_msg)
        print("Output file saved as:", output_file)
    else:
        error_msg = "Failed to merge the video and audio files."
        logging.error(error_msg)
        messagebox.showerror("Error", error_msg)

# Merge the video and audio using FFmpeg with progress indicator
def execute_ffmpeg_command(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    output_lines = []
    total_lines = 0
    for line in p.stdout:
        output_lines.append(line)
        total_lines += 1

    # Create a progress window to display the progress
    progress_window = Tk()
    progress_window.title("Merging Files")

    # Calculate the center position of the screen
    window_width = 400
    window_height = 100
    screen_width = progress_window.winfo_screenwidth()
    screen_height = progress_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    progress_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    progress_bar = ttk.Progressbar(progress_window, length=300, mode="determinate")
    progress_bar.pack(pady=10)

    for i, line in enumerate(output_lines):
        progress = (i + 1) / total_lines * 100
        progress_bar["value"] = progress
        progress_window.update()
        print(line, end="")  # Print the line to the console

    # Close the progress window
    progress_window.destroy()

# Create the dialog box for entering the video URL
prompt_window = Tk()
prompt_window.title("Rip It Beta v1")

# Calculate the center position of the screen
window_width = 400
window_height = 150
screen_width = prompt_window.winfo_screenwidth()
screen_height = prompt_window.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

prompt_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

url_label = Label(prompt_window, text="Enter the URL here:")
url_label.pack(pady=10)

url_frame = Frame(prompt_window, padx=10)  # Create a frame with padding
url_frame.pack(pady=5)

url_entry = Entry(url_frame, width=50)
url_entry.pack()

merge_button = Button(prompt_window, text="Rip it!", command=merge_files)
merge_button.pack(pady=10)

prompt_window.mainloop()
