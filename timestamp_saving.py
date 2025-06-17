import cv2
import pyautogui
import numpy as np
from PIL import Image
import time
from datetime import datetime  # ✅ added for timestamp

# Function to get user input
def get_user_input():
    print("\033[1;37;40m")  # Set text color to white on black background
    username = input("Enter your username: ")
    choice = input("Do you want a burst GIF or a single photo? (Enter 'gif' or 'photo'): ").strip().lower()
    
    if choice == 'gif':
        duration = int(input("How many seconds for the GIF? "))
        num_photos = int(input("How many photos in that many seconds? "))
    else:
        duration = 0
        num_photos = 1  # Default to 1 photo for single photo option

    random_captures = int(input("How many times to capture randomly in 1 hour? "))
    
    print("\033[0m")  # Reset text color
    return choice, duration, num_photos, random_captures

# Get formatted timestamp for filename
def get_timestamp_filename(prefix="rc"):
    now = datetime.now()
    return f"{prefix}-{now.strftime('%Y_%m_%d_%H_%M_%S')}"


# ----- Capture screenshot once -----
screenshot = pyautogui.screenshot()
screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

# Target width for layout
combined_width = screenshot_cv.shape[1]

# Resize screenshot to ~70% of width
screenshot_width = int(combined_width * 0.7)
screenshot_height = int(screenshot_cv.shape[0] * screenshot_width / screenshot_cv.shape[1])
screenshot_resized = cv2.resize(screenshot_cv, (screenshot_width, screenshot_height))

# Padding helper
def pad_width(img, target_width):
    h, w = img.shape[:2]
    if w < target_width:
        pad = target_width - w
        return cv2.copyMakeBorder(img, 0, 0, 0, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    return img

# Webcam setup
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Optional: lower resolution
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Get user input
choice, duration, num_photos, random_captures = get_user_input()

frames = []
delay_between = duration / num_photos if choice == 'gif' else 0  # Calculate delay for GIF

for _ in range(num_photos):
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Resize selfie to 30% of width
    selfie_width = int(combined_width * 0.3)
    selfie_height = int(frame.shape[0] * selfie_width / frame.shape[1])
    selfie_resized = cv2.resize(frame, (selfie_width, selfie_height))
    selfie_padded = pad_width(selfie_resized, combined_width)

    screenshot_padded = pad_width(screenshot_resized, combined_width)

    # Combine vertically
    combined = np.vstack((selfie_padded, screenshot_padded))

    # Show live
    cv2.imshow("Burst Preview", combined)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Add to frame list for GIF
    combined_rgb = cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)
    frames.append(Image.fromarray(combined_rgb))

    time.sleep(delay_between)

cap.release()
cv2.destroyAllWindows()

# Save with timestamped filename
file_base = get_timestamp_filename()

if choice == 'gif':
    frames[0].save(f"{file_base}.gif", save_all=True, append_images=frames[1:], duration=100, loop=0)
    print(f"GIF saved as {file_base}.gif")
else:
    frames[-1].save(f"{file_base}.png")
    print(f"Single photo saved as {file_base}.png")
