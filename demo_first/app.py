from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import cv2
import numpy as np
import imutils
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

# Khởi tạo kích thước ký tự
digit_w = 30
digit_h = 60

# Load mô hình SVM và cascade
model_svm = cv2.ml.SVM_load('svm.xml')
plate_cascade = cv2.CascadeClassifier('cascade2.xml')

# Thư mục lưu file tạm
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Hàm tiền xử lý ảnh
def Pretreatment(imgLP):
    grayImg = cv2.cvtColor(imgLP, cv2.COLOR_BGR2GRAY)
    noise_removal = cv2.bilateralFilter(grayImg, 9, 75, 75)
    ret, binImg = cv2.threshold(grayImg, 100, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kerel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 1))
    binImg = cv2.morphologyEx(binImg, cv2.MORPH_DILATE, kerel3)
    return binImg

# Hàm tìm contour
def contours_detect(binImg):
    cnts, _ = cv2.findContours(binImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    return cnts

# Hàm vẽ contour
def draw_rects_on_img(img, cnts):
    imgtemp = img.copy()
    cv2.drawContours(imgtemp, cnts, -1, (0, 120, 0), 1)
    return imgtemp

# Hàm nhận diện và sắp xếp ký tự
def find_number(cnts, binImg, imgtemp, vehicle_type):
    count = 0
    plate_number = ''
    coorarr = []
    firstrow = []
    lastrow = []

    # Duyệt contour
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if h/w > 1.5 and h/w < 4 and cv2.contourArea(c) > 4000:
            # Crop ký tự
            crop = imgtemp[y:y+h, x:x+w]
            count += 1
            cv2.imwrite(f'./number/number{count}.jpg', crop)
            coorarr.append((x, y, ''))

            # Xử lý ký tự
            binImgtemp = binImg
            curr_num = binImgtemp[y:y+h, x:x+w]
            curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
            _, curr_num = cv2.threshold(curr_num, 30, 255, cv2.THRESH_BINARY)
            curr_num = np.array(curr_num, dtype=np.float32)
            curr_num = curr_num.reshape(-1, digit_w * digit_h)

            # Dự đoán
            result = model_svm.predict(curr_num)[-1]
            result = int(result[0, 0])
            char = str(result) if result <= 9 else chr(result)
            coorarr[-1] = (x, y, char)

    # Sắp xếp theo y (hàng trên/dưới)
    coorarr.sort(key=lambda elem: elem[1])
    firstrow = coorarr[:4]  # Hàng trên
    lastrow = coorarr[4:]  # Hàng dưới
    firstrow.sort(key=lambda elem: elem[0])  # Sắp xếp trái -> phải
    lastrow.sort(key=lambda elem: elem[0])

    # Ghép ký tự
    for _, _, c in firstrow:
        plate_number += c
    for _, _, c in lastrow:
        plate_number += c

    # Giả lập confidence dựa trên số ký tự nhận diện
    confidence = min(95, 60 + len(plate_number) * 5) if plate_number else 0

    return {
        'plate': plate_number if plate_number else 'Unknown',
        'confidence': confidence,
        'vehicleType': vehicle_type.capitalize() if vehicle_type else 'Unknown'
    }

# Route API
@app.route('/api/recognize', methods=['POST'])
def recognize_plate():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    vehicle_type = request.form.get('vehicleType', '')

    # Kiểm tra định dạng file
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        return jsonify({'error': 'Unsupported file format'}), 400

    # Lưu file tạm
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        # Đọc và xử lý ảnh
        img = cv2.imread(file_path)
        if img is None:
            return jsonify({'error': 'Invalid image'}), 400

        # Resize ảnh
        himg, wimg, _ = img.shape
        if wimg/himg > 2:
            img = cv2.resize(img, dsize=(1000, 200))
        else:
            img = cv2.resize(img, dsize=(800, 500))

        # Tiền xử lý
        binImg = Pretreatment(img)
        cnts = contours_detect(binImg)
        imgtemp = draw_rects_on_img(img, cnts)

        # Nhận diện
        result = find_number(cnts, binImg, imgtemp, vehicle_type)

        return jsonify(result)

    except Exception as e:
        print(f"Error in API: {str(e)}")  # In lỗi ra console server
        return jsonify({'error': str(e)}), 500

    finally:
        # Xóa file tạm
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)