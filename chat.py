import ollama
import re

# สร้างตัวแปรเพื่อเก็บประวัติการสนทนา
conversation_history = []
current_order = []

# ฟังก์ชันเริ่มต้นการสนทนา
def init_chat():
    global conversation_history, current_order
    system_prompt = """
    คุณเป็นผู้ช่วยสั่งอาหารคอยรับรายการอาหาร
    - เมื่อผู้ใช้สั่งอาหาร ให้บันทึกรายการสั่งเรียงเป็นรายการ
    - เมื่อผู้ใช้ถามสรุปเมนู ให้แสดงรายการที่สั่งทั้งหมด
    """
    conversation_history = [{'role': 'system', 'content': system_prompt}]
    current_order = []

# ฟังก์ชันสรุปเมนูที่สั่ง
def summarize_order(menu_items):
    if not menu_items:
        return "ยังไม่มีเมนูที่ถูกสั่ง"
    return "📝 สรุปเมนูที่สั่ง:\n" + "\n".join(f"{i+1}. {item['name']} - {item.get('note', 'ไม่มีหมายเหตุ')}" for i, item in enumerate(menu_items))

# ฟังก์ชันแยกเมนูจากข้อความ
def parse_menu_items(text):
    items = []
    lines = text.strip().split('\n')
    for line in lines:
        match = re.match(r'-\s*(.+?)\s*(\d+)\s*จาน(?:\s*\((.+?)\))?', line)
        if match:
            name = match.group(1).strip()
            quantity = int(match.group(2))
            note = match.group(3) if match.group(3) else ''
            for _ in range(quantity):
                items.append({'name': name, 'note': note})
    return items

# ฟังก์ชันหลักสำหรับการสนทนากับผู้ใช้
def chat_with_text(user_input):
    global conversation_history, current_order
    model_name = 'qwen3:4b'

    # รีเซ็ตการสนทนา
    if user_input.lower() == 'reset':
        init_chat()
        return "รีเซ็ตการสนทนาเรียบร้อยแล้ว"

    # ถามสรุปเมนู
    if user_input.lower() == 'สรุปเมนู':
        return summarize_order(current_order)

    # สั่งอาหาร
    if 'สั่ง' in user_input.lower():
        parts = user_input.split()
        if len(parts) >= 2:
            item_name = parts[1]
            note = " ".join(parts[2:]) if len(parts) > 2 else ""
            current_order.append({'name': item_name, 'note': note})
            return summarize_order(current_order)

    # รับรายการสั่งอาหารในรูปแบบเฉพาะ
    if 'รายการสั่งอาหาร' in user_input:
        items = parse_menu_items(user_input)
        if items:
            current_order.extend(items)
            return summarize_order(current_order)

    # ส่งข้อความไปที่ Ollama สำหรับตอบกลับ
    conversation_history.append({'role': 'user', 'content': user_input})
    try:
        response = ollama.chat(
            model=model_name,
            messages=conversation_history,
            options={
                'temperature': 1.0,
                'num_ctx': 4096
            }
        )
        bot_response = response['message']['content']
        
        # เพิ่มส่วนลบแท็ก <think>
        bot_response = re.sub(r'<think>.*?</think>', '', bot_response, flags=re.DOTALL).strip()
        
        conversation_history.append({'role': 'assistant', 'content': bot_response})
        return bot_response
    except Exception as e:
        conversation_history.pop()
        return f"เกิดข้อผิดพลาด: {str(e)}"