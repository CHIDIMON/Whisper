import ollama

def summarize_order(menu_items):
    """ฟังก์ชันสำหรับสรุปเมนูที่ถูกสั่ง"""
    if not menu_items:
        return "ยังไม่มีเมนูที่ถูกสั่ง"
    
    summary = "📝 สรุปเมนูที่สั่ง:\n"
    for i, item in enumerate(menu_items, 1):
        summary += f"{i}. {item['name']} - {item.get('note', 'ไม่มีหมายเหตุ')}\n"
    
    return summary

def chat_with_ollama():
    print("เริ่มการสนทนา (พิมพ์ 'exit' เพื่อออก, 'reset' เพื่อรีเซ็ตการสนทนา, 'สรุปเมนู' เพื่อดูรายการสั่ง)")
    
    # ระบุชื่อโมเดล
    model_name = 'qwen3:8b'
    print(f"กำลังใช้โมเดล: {model_name}")
    
    # ระบบ prompt สำหรับเมนูอาหาร
    system_prompt = """
    คุณเป็นผู้ช่วยสั่งอาหารและให้คำแนะนำเมนูอาหาร
    - เมื่อผู้ใช้สั่งอาหาร ให้บันทึกรายการสั่ง
    - เมื่อผู้ใช้ถามสรุปเมนู ให้แสดงรายการที่สั่งทั้งหมด
    """
    
    conversation_history = [{'role': 'system', 'content': system_prompt}]
    current_order = []
    
    while True:
        user_input = input("คุณ: ")
        
        if user_input.lower() == 'exit':
            print("จบการสนทนา...")
            break
            
        if user_input.lower() == 'reset':
            conversation_history = [{'role': 'system', 'content': system_prompt}]
            current_order = []
            print("บอท: ความจำถูกลบแล้ว เริ่มการสนทนาใหม่!")
            continue
            
        # ตรวจสอบคำสั่งสั่งอาหาร
        if 'สั่ง' in user_input.lower():
            parts = user_input.split()
            if len(parts) >= 2:
                item_name = parts[1]
                note = " ".join(parts[2:]) if len(parts) > 2 else ""
                current_order.append({'name': item_name, 'note': note})
                print(f"บอท: เพิ่ม {item_name} ในรายการสั่งแล้ว {f'(หมายเหตุ: {note})' if note else ''}")
                continue
        
        # ตรวจสอบคำขอสรุปเมนู
        if user_input.lower() == 'สรุปเมนู':
            print("บอท:", summarize_order(current_order))
            continue
            
        # ถ้าไม่ใช่คำสั่งพิเศษ ส่งไปยังโมเดลแชท
        conversation_history.append({'role': 'user', 'content': user_input})
        
        try:
            response = ollama.chat(
                model=model_name,
                messages=conversation_history,
                options={
                    'temperature': 1.0,
                    'num_ctx': 8192
                }
            )
            
            bot_response = response['message']['content']
            conversation_history.append({'role': 'assistant', 'content': bot_response})
            
            print("บอท:", bot_response)
            
        except Exception as e:
            print(f"บอท: เกิดข้อผิดพลาด: {str(e)}")
            conversation_history.pop()  # ลบข้อความล่าสุดที่ทำให้เกิดข้อผิดพลาด

if __name__ == "__main__":
    chat_with_ollama()