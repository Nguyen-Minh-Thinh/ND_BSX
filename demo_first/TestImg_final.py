import cv2
import numpy as np
import sys

# Khởi tạo kích thước của kí tự trên biển số
digit_w = 30
digit_h = 60

# Load model SVM(Support Vector Machine) đã huấn luyện để nhận diện ký tự (chữ/số)
model_svm = cv2.ml.SVM_load('svm.xml')

# Nhận ảnh từ some_cars.py truyền qua
if len(sys.argv) > 1:
    img_path = sys.argv[1]
else:
    print("Error: Cần đường dẫn ảnh")
    sys.exit(1)
output_image = sys.argv[2] if len(sys.argv) > 2 else "output.jpg"
OriImg = cv2.imread(img_path, 1)

if OriImg is None:
    print("Error: Không đọc được ảnh")
    sys.exit(1)

# Dùng mô hình cascade(Cascade Classifier) đã train để nhận diện vùng có biển số
plate_cascade = cv2.CascadeClassifier("./cascade.xml")
plates = plate_cascade.detectMultiScale(OriImg, 1.1, 3)

img = OriImg

# Cắt vùng biển số ra để xử lý tiếp
for (x,y,w,h) in plates:
    cv2.rectangle(OriImg,(x,y),(x+w,y+h),(255,0,0),1)
    img = OriImg[y:y+h, x:x+w]

(himg,wimg,chanel)=img.shape
# Phân loại xe
vehicle_type = "car" if wimg/himg >= 2 else "motorcycle"

if(wimg/himg >=2):
    img=cv2.resize(img,dsize=(1000,200))
else:
    img=cv2.resize(img,dsize=(800,500))

# Tiền xử lí ảnh
grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
noise_removal = cv2.bilateralFilter(grayImg,9,75,75)
ret, binImg = cv2.threshold(grayImg, 100, 255, cv2.THRESH_BINARY_INV+ cv2.THRESH_OTSU)
kerel3 = cv2.getStructuringElement(cv2.MORPH_RECT,(4,4))
binImg = cv2.morphologyEx(binImg,cv2.MORPH_DILATE,kerel3)

# Tìm contour và vẽ lên ảnh
cnts, _ = cv2.findContours(binImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
imgtemp=img.copy()
cv2.drawContours(imgtemp,cnts,-1,(0,120,0),1)

plate_number=''
count=0
coorarr=[]

# Duyệt từng contour và nhận diện
for c in (cnts):
    x,y,w,h=cv2.boundingRect(c)
    cv2.rectangle(imgtemp, (x, y), (x + w, y + h), (0, 255, 0), 1)
    if h/w >1.5 and h/w <4 and cv2.contourArea(c)>4500:
        # Đóng khung cho kí tự
        cv2.rectangle(imgtemp, (x, y), (x + w, y + h), (0, 0, 255),2)
        # Crop thành những số riêng lẻ
        crop=img[y:y+h, x:x+w]
        count+=1
        cv2.imwrite('./number/number%d.jpg'% count,crop)
        coorarr.append((x,y))
        binImgtemp=binImg
        curr_num=binImgtemp[y:y+h, x:x+w]
        curr_num=cv2.resize(curr_num,dsize=(digit_w,digit_h))
        _, curr_num=cv2.threshold(curr_num,30,255,cv2.THRESH_BINARY)
        curr_num= np.array(curr_num,dtype=np.float32)
        curr_num=curr_num.reshape(-1,digit_w*digit_h)

        result=model_svm.predict(curr_num)[-1]
        result= int(result[0,0])
        if result<=9: 
            result= str(result)
        else:
            result=chr(result)
        plate_number +=result+' '
        cv2.putText(imgtemp,result,(x-50,y+50),cv2.FONT_HERSHEY_COMPLEX,3,(0, 255, 0), 2, cv2.LINE_AA)


stringarr=plate_number.strip()
stringarr=stringarr.split(" ")

# Dựa vào tọa độ (x, y) để sắp xếp lại thứ tự các ký tự trái → phải, trên → dưới
for i in range(len(coorarr)):
    # So sánh tọa độ y
    for j in range(i+1,len(coorarr)):
        # Nếu y của i > y của j 
        if coorarr[i][1]- coorarr[j][1] >15:
            temp=stringarr[i]
            stringarr[i]=stringarr[j]
            stringarr[j]=temp
            tempp=coorarr[i]
            coorarr[i]=coorarr[j]
            coorarr[j]=tempp
        elif coorarr[i][0]- coorarr[j][0] >0:
            temp=stringarr[i]
            stringarr[i]=stringarr[j]
            stringarr[j]=temp
            tempp=coorarr[i]
            coorarr[i]=coorarr[j]
            coorarr[j]=tempp

# Cho về lại string
plate_number=''.join(stringarr)
print('Bien so xe:', plate_number)
print('Loai xe:', vehicle_type)

# Lưu ảnh cho API
cv2.imwrite(output_image, imgtemp)

# Chỉ hiển thị khi chạy thủ công
if len(sys.argv) <= 1:
    cv2.imshow('result',imgtemp)
    #mở thư mục number để xe,
    # os.startfile('number')
    cv2.waitKey()
    cv2.destroyAllWindows()