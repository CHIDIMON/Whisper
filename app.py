import sys
import io
import os
import traceback
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import sqlite3
from chatapi import init_chat, chat_with_text
from faster_whisper import WhisperModel

# ตั้งค่า encoding เป็น UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "*"}, r"/image/*": {"origins": "*"}, r"/chat": {"origins": "*"}})

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
def get_db_connection():
    conn = sqlite3.connect('food_menu.db')
    conn.row_factory = sqlite3.Row
    return conn

# โหลดโมเดล faster-whisper
print("กำลังโหลดโมเดล Faster-Whisper...")
model = WhisperModel("large-v3", compute_type="int8")
print("โหลดโมเดลเสร็จสิ้น")

@app.route('/image/<menu_name>', methods=['GET'])
def get_image(menu_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT image FROM menu WHERE name=?", (menu_name,))
        image_data = cursor.fetchone()
        conn.close()
        
        if image_data:
            return send_file(BytesIO(image_data['image']), mimetype='image/jpeg')
        return jsonify({"error": "ไม่พบรูปภาพ"}), 404
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {str(e)}")
        return jsonify({"error": "เกิดข้อผิดพลาดในการดึงรูปภาพ"}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "ไม่มีไฟล์ที่อัปโหลด"}), 400
    
    file = request.files['file']
    language = request.form.get('language', 'th')
    
    if file.filename == '':
        return jsonify({"error": "ไม่ได้เลือกไฟล์"}), 400

    try:
        temp_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(temp_path)

        # ใช้ faster-whisper ถอดเสียง
        segments, info = model.transcribe(temp_path, language=language, temperature=0, beam_size=5, best_of=5)
        text = " ".join([seg.text for seg in segments]).strip()
        print(f"Transcribed text: {text}")

        chat_response = chat_with_text(text, lang_code=language)

        # ดึงรายการเมนูทั้งหมดจาก DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM menu")
        all_menus = [row['name'] for row in cursor.fetchall()]
        conn.close()

        # ค้นหาคำที่ตรงบางส่วน
        matched_menu = None
        for menu_name in all_menus:
            if menu_name.lower() in text.lower():
                matched_menu = menu_name
                break

        response_data = {
            "text": text,
            "chat_response": chat_response
        }

        if matched_menu:
            response_data["menu"] = matched_menu
        
        return jsonify(response_data)

    except Exception:
        print("🔥 ERROR:", traceback.format_exc())
        return jsonify({"error": "เกิดข้อผิดพลาดในการประมวลผล"}), 500
    finally:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)

init_chat()

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    try:
        data = request.get_json()
        user_input = data.get('text', '')
        lang_code = data.get('language', 'th')

        if not user_input:
            return jsonify({'error': 'ไม่มีข้อความ'}), 400

        response = chat_with_text(user_input, lang_code=lang_code)
        return jsonify({'response': response})

    except Exception as e:
        print(f"เกิดข้อผิดพลาดใน chat: {str(e)}")
        return jsonify({'error': 'เกิดข้อผิดพลาดในการสนทนา'}), 500

@app.route('/debug/menus', methods=['GET'])
def debug_menus():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM menu")
        menus = cursor.fetchall()
        conn.close()
        return jsonify({"menus": [{"id": m['id'], "name": m['name']} for m in menus]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def initialize_database():
    conn = sqlite3.connect('food_menu.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image BLOB
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM menu")
    if cursor.fetchone()[0] == 0:
        with open("image/Pizza.webp", "rb") as f:
            pizza_img = f.read()
        cursor.execute("INSERT INTO menu (name, image) VALUES (?, ?)", ("Pizza", pizza_img))
        with open("image/Tomyum.jpg", "rb") as f:
            tomyum_img = f.read()
        cursor.execute("INSERT INTO menu (name, image) VALUES (?, ?)", ("ต้มยำ", tomyum_img))
        cursor.execute("INSERT INTO menu (name, image) VALUES (?, ?)", ("Tom Yum", tomyum_img))
        cursor.execute("INSERT INTO menu (name, image) VALUES (?, ?)", ("Tom Yam", tomyum_img))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()
    print("Current menus in database:")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM menu")
    print(cursor.fetchall())
    conn.close()
    app.run(debug=False, port=5000, host='0.0.0.0')
