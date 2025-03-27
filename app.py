import sys
import io
import os
import whisper
import json
import sqlite3
from flask import Flask, request, Response, send_file
from flask_cors import CORS
from googletrans import Translator
from io import BytesIO
import requests  # สำหรับใช้ในการเชื่อมต่อ API
from pythaispell import spell
# บังคับให้ Python ใช้ UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "*"}}, supports_credentials=True)

UPLOAD_FOLDER = "small"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# โหลดโมเดล Whisper
print("Loading Whisper model...")
model = whisper.load_model("large-v3", device="cuda")
print("Whisper model loaded successfully.")

def search_menu(text):
    conn = sqlite3.connect("food_menu.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, image FROM menu WHERE name LIKE ?", (f"%{text}%",))
    result = cursor.fetchone()
    conn.close()
    return result


# ฟังก์ชันสำหรับแก้ไขการสะกดคำผิดในภาษาไทย
def correct_spelling_thai(word):
    # ใช้ ThaiSpell ในการแก้ไขคำสะกดผิด
    corrected_word = spell(word)
    return corrected_word

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Received upload request.")
    file = request.files.get('file')
    language = request.form.get('language', 'en')  # รับภาษาที่เลือกจากฟอร์ม
    
    if not file or file.filename == '':
        return Response(json.dumps({"error": "No file uploaded or selected"}, ensure_ascii=False),
                        status=400, content_type='application/json; charset=utf-8')
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    try:
        file.save(file_path)
        print(f"File saved: {file_path}")
        
        result = model.transcribe(file_path, language=language)  # ใช้ภาษาที่เลือก
        text = result["text"].strip()
        print(f"Transcribed text: {text}")
        
        # แก้ไขคำสะกดผิดในภาษาไทย (ถ้าเป็นภาษาไทย)
        if language == 'th':
            text = correct_spelling_thai(text)
        
        # แปลเป็นอังกฤษทับศัพท์หากไม่ใช่ภาษาอังกฤษ
        if language != 'en':
            translated_text = text  # ไม่แปลถ้าเป็นภาษาอื่น
        else:
            translated_text = text
        
        menu_result = search_menu(translated_text)
        if menu_result:
            menu_name, image_data = menu_result
            image_base64 = image_data.hex()  # แปลง binary image เป็น hex string
        else:
            menu_name, image_base64 = None, None
        
        return Response(json.dumps({"text": translated_text, "menu": menu_name, "image": image_base64},
                                   ensure_ascii=False), status=200,
                        content_type='application/json; charset=utf-8')
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return Response(json.dumps({"error": str(e)}, ensure_ascii=False),
                        status=500, content_type='application/json; charset=utf-8')

@app.route('/image/<menu_name>', methods=['GET'])
def get_image(menu_name):
    conn = sqlite3.connect("food_menu.db")
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM menu WHERE name = ?", (menu_name,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        image_data = result[0]
        return send_file(BytesIO(image_data), mimetype='image/jpeg')
    return Response(json.dumps({"error": "Image not found"}, ensure_ascii=False),
                    status=404, content_type='application/json; charset=utf-8')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
