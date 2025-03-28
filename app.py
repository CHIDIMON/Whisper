import sys
import io
import os
import whisper
import traceback
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
from database import FoodMenuDB
import torch

# ตั้งค่า encoding เป็น UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

app = Flask(__name__)
CORS(app, resources={
    r"/.*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
db = FoodMenuDB()

# โหลดโมเดล Whisper
print("กำลังโหลดโมเดล Whisper...")
model = whisper.load_model("large-v3", device="cpu")
print("โหลดโมเดล Whisper เสร็จสิ้น")

@app.route('/image/<menu_name>', methods=['GET'])
def get_image(menu_name):
    """ให้บริการรูปภาพเมนูอาหาร"""
    try:
        image_data = db.get_menu_image(menu_name)
        if image_data:
            return send_file(BytesIO(image_data), mimetype='image/jpeg')
        return jsonify({"error": "ไม่พบรูปภาพ"}), 404
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {str(e)}")
        return jsonify({"error": "เกิดข้อผิดพลาดในการดึงรูปภาพ"}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """รับไฟล์เสียงและประมวลผล"""
    if 'file' not in request.files:
        return jsonify({"error": "ไม่มีไฟล์ที่อัปโหลด"}), 400
    
    file = request.files['file']
    language = request.form.get('language', 'th')
    
    if file.filename == '':
        return jsonify({"error": "ไม่ได้เลือกไฟล์"}), 400

    try:
        # บันทึกไฟล์ชั่วคราว
        temp_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(temp_path)
        
        # ถอดเสียง
        result = model.transcribe(temp_path, language=language)
        text = result["text"].strip()
        print(f"Transcribed text: {text}")
        
        # ค้นหาเมนูอาหาร
        menu_result = db.search_menu(text)
        response_data = {"text": text}
        
        if menu_result:
            menu_name, _ = menu_result
            response_data["menu"] = menu_name
        
        return jsonify(response_data)
    
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "เกิดข้อผิดพลาดในการประมวลผล"}), 500
    finally:
        # ลบไฟล์ชั่วคราวถ้ามี
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/debug/menus', methods=['GET'])
def debug_menus():
    """Endpoint for debugging - list all menus"""
    try:
        menus = db.list_all_menus()
        return jsonify({"menus": [{"id": m[0], "name": m[1], "keywords": m[2]} for m in menus]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # For debugging - print all menus when starting
    print("Current menus in database:")
    print(db.list_all_menus())
    
    app.run(debug=True, port=5000, host='0.0.0.0')