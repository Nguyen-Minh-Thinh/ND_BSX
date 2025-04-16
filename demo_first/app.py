from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import cv2
import base64
import os
import tempfile
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process_license_plate")
async def process_license_plate(file: UploadFile = File(...)):
    logger.info("Nhận request /process_license_plate")
    
    output_dir = "processed_images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = int(time.time())
    output_filename = f"processed_{timestamp}.jpg"
    output_filepath = os.path.join(output_dir, output_filename)
    logger.info(f"Output path: {output_filepath}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_input, \
         tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_output:
        contents = await file.read()
        logger.info(f"Đọc file: {file.filename}, kích thước: {len(contents)} bytes")
        temp_input.write(contents)
        temp_input_path = temp_input.name
        temp_output_path = temp_output.name
        logger.info(f"Temp input: {temp_input_path}, Temp output: {temp_output_path}")

    try:
        logger.info("Gọi some_cars.py")
        result = subprocess.run(
            ["python", "demo_first/some_cars.py", temp_input_path, temp_output_path],
            capture_output=True, text=True
        )
        logger.info(f"some_cars.py stdout: {result.stdout}")
        logger.info(f"some_cars.py stderr: {result.stderr}")

        output_lines = result.stdout.strip().split("\n")
        license_plate = ""
        vehicle_type = "unknown"
        for line in output_lines:
            if line.startswith("Bien so xe:"):
                license_plate = line.split(":")[1].strip()
            elif line.startswith("Loai xe:"):
                vehicle_type = line.split(":")[1].strip()
        logger.info(f"License plate: {license_plate}, Vehicle type: {vehicle_type}")

        processed_img = cv2.imread(temp_output_path)
        if processed_img is None:
            logger.error(f"Không đọc được ảnh từ {temp_output_path}")
            return JSONResponse(content={"error": "Không tạo được ảnh kết quả"}, status_code=500)

        cv2.imwrite(output_filepath, processed_img)
        logger.info(f"Đã lưu ảnh vào {output_filepath}")

        _, buffer = cv2.imencode('.jpg', processed_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        logger.info(f"Base64 length: {len(img_base64)}")

        response = {
            "license_plate": license_plate if license_plate else "Không xác định",
            "vehicle_type": vehicle_type if vehicle_type else "Không xác định",
            "processed_image": f"/processed_images/{output_filename}"
        }
        logger.info(f"Response: {response}")
        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"Lỗi: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        if os.path.exists(temp_input_path):
            os.unlink(temp_input_path)
        if os.path.exists(temp_output_path):
            os.unlink(temp_output_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)