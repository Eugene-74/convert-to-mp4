import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from datetime import datetime
import threading
import platform  # Add this import

def check_ffmpeg_installed():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise FileNotFoundError("ffmpeg is not installed or not found in PATH")

def get_video_duration(file_path):
    result = subprocess.run(
        ['ffmpeg', '-i', file_path],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True
    )
    duration_line = [x for x in result.stderr.split('\n') if 'Duration' in x]
    if duration_line:
        duration_str = duration_line[0].split('Duration: ')[1].split(',')[0]
        h, m, s = duration_str.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 0

def convert_vob_to_mp4(input_vob, output_mp4, file_progress_callback=None):
    video_label['text'] = f"Converting: {os.path.basename(input_vob)}"
    if os.path.exists(output_mp4):
        overwrite = messagebox.askyesno("File exists", f"File '{output_mp4}' already exists. Overwrite?")
        if not overwrite:
            print(f'Skipped {output_mp4}')
            return
    start_time = datetime.now()
    command = [
        'ffmpeg',
        '-y',  # Automatically overwrite output files
        '-i', input_vob,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_mp4
    ]
    if platform.system() == "Windows":
        command = ['cmd', '/c'] + command  # Adjust command for Windows
    total_duration = get_video_duration(input_vob)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    global current_process
    current_process = process
    for line in process.stdout:
        if file_progress_callback:
            file_progress_callback(line, total_duration, start_time)
    process.wait()
    end_time = datetime.now()
    duration = end_time - start_time
    print(f'Converted {input_vob} to {output_mp4} in {duration}')
    video_label['text'] = ""
    current_process = None

def convert_all_vob_in_directory(directory, overall_progress_callback=None, file_progress_callback=None):
    total_files = sum([len(files) for _, _, files in os.walk(directory) if any(f.endswith('.VOB') for f in files)])
    converted_files = 0
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.VOB'):
                input_vob = os.path.join(root, filename)
                output_mp4 = os.path.splitext(input_vob)[0] + '.mp4'
                convert_vob_to_mp4(input_vob, output_mp4, file_progress_callback)
                converted_files += 1
                if overall_progress_callback:
                    overall_progress_callback(converted_files, total_files)
                print(f'Converted {input_vob} to {output_mp4}')
        for subdir in dirs:
            convert_all_vob_in_directory(os.path.join(root, subdir), overall_progress_callback, file_progress_callback)

def start_conversion():
    directory = filedialog.askdirectory()
    if not directory:
        return

    progress_bar['value'] = 0
    progress_label['text'] = "0%"
    
    def update_overall_progress(converted, total):
        progress = int((converted / total) * 100)
        progress_bar['value'] = progress
        progress_label['text'] = f"{progress}%"
        root.update_idletasks()

    def update_file_progress(line, total_duration, start_time):
        if "time=" in line:
            time_str = line.split("time=")[1].split(" ")[0]
            if time_str.count(':') == 2:  # Ensure the time string has the correct format
                h, m, s = time_str.split(':')
                current_time = int(h) * 3600 + int(m) * 60 + float(s)
                progress = int((current_time / total_duration) * 100)
                progress_bar['value'] = progress
                progress_label['text'] = f"{progress}%"
                root.update_idletasks()
                # Estimate remaining time for the current file
                elapsed_time = datetime.now() - start_time
                remaining_time = elapsed_time / (current_time / total_duration) - elapsed_time
                remaining_minutes, remaining_seconds = divmod(remaining_time.total_seconds(), 60)
                remaining_label['text'] = f"Remaining time for current file: {int(remaining_minutes)}m {int(remaining_seconds)}s"

    def do_conversions():
        try:
            check_ffmpeg_installed()
            total_files = sum([len(files) for _, _, files in os.walk(directory) if any(f.endswith('.VOB') for f in files)])
            converted_files = 0
            start_time = datetime.now()
            convert_all_vob_in_directory(directory, update_overall_progress, update_file_progress)
            end_time = datetime.now()
            total_duration = end_time - start_time
            messagebox.showinfo("Success", f"All VOB files have been converted in {total_duration}.")
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))

    threading.Thread(target=do_conversions, daemon=True).start()

def close_app():
    global current_process
    if current_process:
        current_process.terminate()
        current_process = None
    root.quit()

current_process = None
root = tk.Tk()
root.title("VOB to MP4 Converter")
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")  # Set the window size to full screen

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

select_button = tk.Button(frame, text="Select Directory and Convert", command=start_conversion)
select_button.pack(pady=10)

progress_bar = Progressbar(frame, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

progress_label = tk.Label(frame, text="0%")
progress_label.pack(pady=10)

video_label = tk.Label(frame, text="")
video_label.pack(pady=10)

remaining_label = tk.Label(frame, text="Remaining time for current file: N/A")
remaining_label.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", close_app)

root.mainloop()
