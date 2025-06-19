import tkinter as tk
from tkinter import messagebox
import cv2
import pyautogui
import numpy as np
from PIL import Image
import time
from datetime import datetime
import os
import threading
import math

# Generate timestamp-based filename
def get_timestamp_filename(prefix="random_click", extension="gif"):
    now = datetime.now()
    timestamp = now.strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"{prefix}_{timestamp}.{extension}"
    return filename

# Pad image to match width
def pad_width(img, target_width):
    h, w = img.shape[:2]
    if w < target_width:
        pad = target_width - w
        return cv2.copyMakeBorder(img, 0, 0, 0, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    return img

# Capture logic
def capture(choice, duration, num_photos):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    if not cap.isOpened():
        print("Camera Error")
        return

    time.sleep(2)
    screenshot = pyautogui.screenshot()
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    combined_width = screenshot_cv.shape[1]
    screenshot_width = int(combined_width * 0.7)
    screenshot_height = int(screenshot_cv.shape[0] * screenshot_width / screenshot_cv.shape[1])
    screenshot_resized = cv2.resize(screenshot_cv, (screenshot_width, screenshot_height))

    frames = []
    delay_between = duration / num_photos if choice == 'gif' else 0

    for _ in range(num_photos):
        ret, frame = cap.read()
        if not ret:
            break

        selfie_width = int(combined_width * 0.3)
        selfie_height = int(frame.shape[0] * selfie_width / frame.shape[1])
        selfie_resized = cv2.resize(frame, (selfie_width, selfie_height))
        selfie_padded = pad_width(selfie_resized, combined_width)
        screenshot_padded = pad_width(screenshot_resized, combined_width)
        combined = np.vstack((selfie_padded, screenshot_padded))
        combined_rgb = cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)
        frames.append(Image.fromarray(combined_rgb))

        time.sleep(delay_between)

    cap.release()
    cv2.destroyAllWindows()

    if choice == 'gif':
        filename = get_timestamp_filename(extension="gif")
        frames[0].save(filename, save_all=True, append_images=frames[1:], duration=100, loop=0)
    else:
        filename = get_timestamp_filename(extension="png")
        frames[-1].save(filename)

# Schedule captures and update countdown
def scheduled_capture(choice, duration, num_photos, hourly_shots, label_timer):
    interval = 3600 / hourly_shots

    def loop():
        while True:
            capture(choice, duration, num_photos)
            for remaining in range(int(interval), 0, -1):
                mins, secs = divmod(remaining, 60)
                timer_text = f"Next shot in: {mins:02}:{secs:02}"
                label_timer.config(text=timer_text)
                time.sleep(1)

    threading.Thread(target=loop, daemon=True).start()

# GUI setup
def start_ui():
    root = tk.Tk()
    root.title("Random Click")
    root.geometry("300x360")
    root.resizable(False, False)

    root.iconbitmap("camera.ico")  # <-- Provide a camera icon file named camera.ico

    tk.Label(root, text="Choose Capture Type:").pack()
    var_choice = tk.StringVar(value='gif')
    tk.Radiobutton(root, text="Photo", variable=var_choice, value='photo').pack()
    tk.Radiobutton(root, text="GIF", variable=var_choice, value='gif').pack()

    tk.Label(root, text="GIF Duration (sec):").pack()
    entry_duration = tk.Entry(root)
    entry_duration.insert(0, "4")
    entry_duration.pack()

    tk.Label(root, text="Number of Shots per Capture:").pack()
    entry_num_photos = tk.Entry(root)
    entry_num_photos.insert(0, "12")
    entry_num_photos.pack()

    tk.Label(root, text="Captures per Hour:").pack()
    entry_hourly = tk.Entry(root)
    entry_hourly.insert(0, "4")
    entry_hourly.pack()

    label_timer = tk.Label(root, text="Next shot in: --:--", font=("Arial", 12, "bold"))
    label_timer.pack(pady=10)

    def on_start():
        try:
            choice = var_choice.get()
            duration = int(entry_duration.get()) if choice == 'gif' else 0
            num_photos = int(entry_num_photos.get())
            hourly_shots = int(entry_hourly.get())
            scheduled_capture(choice, duration, num_photos, hourly_shots, label_timer)
            messagebox.showinfo("Random Click", "Started background capture!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(root, text="Start Capture", command=on_start).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    start_ui()
