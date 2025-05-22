# -*- coding: utf-8 -*-
import sys
import io

# บังคับ stdout และ stderr เป็น utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, request, render_template_string
from markupsafe import Markup
from openai import OpenAI

client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)

app = Flask(__name__)
conversation = [{"role": "system", "content": "คุณคือผู้ช่วยรับออเดอร์อาหาร ฉลาดและพูดไทยได้ดี"}]

@app.route("/", methods=["GET", "POST"])
def chat():
    global conversation
    user_input = ""
    reply = ""

    if request.method == "POST":
        user_input = request.form["user_input"]
        if user_input.lower().strip() == "reset":
            conversation = [{"role": "system", "content": "คุณคือผู้ช่วยรับออเดอร์อาหาร ฉลาดและพูดไทยได้ดี"}]
            reply = "เริ่มต้นการสนทนาใหม่แล้ว"
        else:
            conversation.append({"role": "user", "content": user_input})
            try:
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=conversation,
                    temperature=0.3
                )
                ai_message = response.choices[0].message.content
                conversation.append({"role": "assistant", "content": ai_message})
                reply = Markup(ai_message)  # ⬅️ ป้องกัน Jinja encode ผิด
            except Exception as e:
                import traceback
                try:
                    traceback.print_exc()
                    print(f"[DEBUG] Raw error: {e}")
                except Exception:
                    print("[DEBUG] ไม่สามารถ print error ได้ (ascii codec issue)")

                # ตัดปัญหา: อย่าแสดง str(e) ที่มีปัญหา
                reply = "❌ เกิดข้อผิดพลาดในการเชื่อมต่อกับ AI (ดู log ใน console)"




    html = """
    <!DOCTYPE html>
    <html lang="th">
    <head>
      <meta charset="UTF-8">
      <title>Groq Chat (Food Order)</title>
    </head>
    <body style="font-family: sans-serif; padding: 20px;">
      <h2>🍜 Groq Chat – ระบบผู้ช่วยสั่งอาหาร</h2>
      <form method="POST">
        <input name="user_input" style="width: 300px;" placeholder="พิมพ์ข้อความ..." autofocus required>
        <button type="submit">ส่ง</button>
      </form>
      <br>
      {% if user_input %}
        <p><b>คุณ:</b> {{ user_input }}</p>
        <p><b>AI:</b> {{ reply }}</p>
      {% endif %}
    </body>
    </html>
    """
    return render_template_string(html, user_input=user_input, reply=reply)

if __name__ == "__main__":
    app.run(debug=False)
