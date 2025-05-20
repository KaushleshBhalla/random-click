import cv2
import pyautogui
import numpy as np
from PIL import Image
import time

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

frames = []
num_photos = 10
delay_between = 0.3  # seconds

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

# Save to GIF
frames[0].save("burst_combined1.gif", save_all=True, append_images=frames[1:], duration=100, loop=0)
print("GIF saved as burst_combined1.gif")
