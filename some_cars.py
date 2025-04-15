import cv2
from matplotlib import pyplot as plt
import numpy as np
import imutils
import easyocr
import tkinter as tk
from tkinter import filedialog
import subprocess
import sys

# Nhận ảnh từ sys.argv nếu có, nếu không dùng mặc định
input_image = sys.argv[1] if len(sys.argv) > 1 else r"0404.jpg"
output_image = sys.argv[2] if len(sys.argv) > 2 else "output.jpg"

# Đọc ảnh
img = cv2.imread(input_image)
if img is None:
    print("Error: Không đọc được ảnh")
    sys.exit(1)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
plt.imshow(cv2.cvtColor(gray, cv2.COLOR_BGR2RGB))

bfilter = cv2.bilateralFilter(gray, 11, 17, 17) #Noise reduction
edged = cv2.Canny(bfilter, 30, 200) #Edge detection
plt.imshow(cv2.cvtColor(edged, cv2.COLOR_BGR2RGB))

keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = imutils.grab_contours(keypoints)
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

location = None
for contour in contours:
    approx = cv2.approxPolyDP(contour, 10, True)
    if len(approx) == 4:
        location = approx
        break

if location is None:
    print("Không tìm thấy biển số")
    subprocess.run([
        r"venv\Scripts\python.exe", 
        "./demo_first/TestImg_final.py", 
        input_image, output_image
    ])
    sys.exit(0)

mask = np.zeros(gray.shape, np.uint8)
new_image = cv2.drawContours(mask, [location], 0,255, -1)
new_image = cv2.bitwise_and(img, img, mask=mask)

(x,y) = np.where(mask==255)
(x1, y1) = (np.min(x), np.min(y))
(x2, y2) = (np.max(x), np.max(y))
cropped_image = gray[x1:x2+1, y1:y2+1]

# Phân loại xe
himg, wimg = cropped_image.shape
vehicle_type = "car" if wimg/himg > 2 else "motorcycle"

reader = easyocr.Reader(['en'])
result = reader.readtext(cropped_image)

def is_valid_license_plate(text):
    return len(text.replace(" ", "")) >= 6
text = result[0][-2] if result else ""
if is_valid_license_plate(text):
    # Nếu đúng => Vẽ text lên ảnh + in kết quả
    font = cv2.FONT_HERSHEY_SIMPLEX
    res = cv2.putText(img, text=text, org=(approx[0][0][0], approx[1][0][1] + 60),
                      fontFace=font, fontScale=1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
    res = cv2.rectangle(img, tuple(approx[0][0]), tuple(approx[2][0]), (0, 255, 0), 3)
    result = str()
    for char in text:
        if char.isalnum():
            result += char
    print('Bien so xe:', result)
    print('Loai xe:', vehicle_type)
    cv2.imwrite(output_image, res)  # Lưu ảnh cho API
    # Chỉ hiển thị khi chạy thủ công
    if len(sys.argv) <= 1:
        cv2.imshow('result', res)
        cv2.waitKey()
        cv2.destroyAllWindows()
    # plt.imshow(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))
    # plt.show()
else:
    # Nếu sai => Gọi file TestImg_final.py
    subprocess.run([
        r"venv\Scripts\python.exe", 
        "./demo_first/TestImg_final.py", 
        input_image, output_image
    ])