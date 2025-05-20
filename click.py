import cv2
import pyautogui
import numpy as np

# Capture screenshot
screenshot = pyautogui.screenshot()
screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

# Capture selfie
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
ret, selfie = cap.read()
cap.release()

if not ret:
    print("Failed to capture selfie.")
    exit()

# Target combined width (use the screenshot's width)
combined_width = screenshot.shape[1]

# Resize selfie to 30% of combined width
selfie_width = int(combined_width * 0.3)
selfie_height = int(selfie.shape[0] * selfie_width / selfie.shape[1])
selfie_resized = cv2.resize(selfie, (selfie_width, selfie_height))

# Resize screenshot to 70% of combined width, keep aspect ratio
screenshot_width = combined_width - selfie_width
screenshot_height = int(screenshot.shape[0] * screenshot_width / screenshot.shape[1])
screenshot_resized = cv2.resize(screenshot, (screenshot_width, screenshot_height))

# To stack vertically, widths must match, so pad narrower image width-wise
target_width = max(selfie_width, screenshot_width)
def pad_width(img, target_width):
    h, w = img.shape[:2]
    if w < target_width:
        pad = target_width - w
        # pad right side with black pixels
        return cv2.copyMakeBorder(img, 0, 0, 0, pad, cv2.BORDER_CONSTANT, value=[0,0,0])
    return img

selfie_padded = pad_width(selfie_resized, target_width)
screenshot_padded = pad_width(screenshot_resized, target_width)

# Combine vertically (portrait)
combined = np.vstack((selfie_padded, screenshot_padded))

# Show result
filename = "combined_image1.jpg"
cv2.imwrite(filename, combined)
print(f"Image saved as {filename}")

# Show result
cv2.imshow("combined-image", combined)
cv2.waitKey(0)
cv2.destroyAllWindows()