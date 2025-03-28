import sqlite3
from PIL import Image
import io
import os

def get_all_menus():
    """ดึงข้อมูลเมนูทั้งหมดจากฐานข้อมูล"""
    try:
        conn = sqlite3.connect("food_menu.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name FROM menu")
        menus = cursor.fetchall()
        
        return menus
    except Exception as e:
        print(f"Error fetching menus: {str(e)}")
        return []
    finally:
        conn.close()

def get_menu_image(menu_id):
    """ดึงรูปภาพเมนูจากฐานข้อมูล"""
    try:
        conn = sqlite3.connect("food_menu.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT image FROM menu WHERE id=?", (menu_id,))
        image_data = cursor.fetchone()
        
        if image_data:
            # แปลง binary data เป็นรูปภาพ
            image = Image.open(io.BytesIO(image_data[0]))
            return image
        else:
            return None
    except Exception as e:
        print(f"Error fetching menu image: {str(e)}")
        return None
    finally:
        conn.close()

def display_menu(menu_id):
    """แสดงข้อมูลเมนูและรูปภาพ"""
    try:
        conn = sqlite3.connect("food_menu.db")
        cursor = conn.cursor()
        
        # ดึงข้อมูลเมนู
        cursor.execute("SELECT name, image FROM menu WHERE id=?", (menu_id,))
        menu = cursor.fetchone()
        
        if menu:
            name, image_data = menu
            print(f"\nMenu ID: {menu_id}")
            print(f"Menu Name: {name}")
            
            # แสดงรูปภาพถ้ามี
            if image_data:
                image = Image.open(io.BytesIO(image_data))
                image.show()
            else:
                print("No image available for this menu.")
        else:
            print(f"No menu found with ID: {menu_id}")
            
    except Exception as e:
        print(f"Error displaying menu: {str(e)}")
    finally:
        conn.close()

def check_menu_exists(menu_name):
    """ตรวจสอบว่ามีเมนูนี้ในฐานข้อมูลหรือไม่"""
    try:
        conn = sqlite3.connect("food_menu.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM menu WHERE name=?", (menu_name,))
        result = cursor.fetchone()
        
        return result is not None
    except Exception as e:
        print(f"Error checking menu existence: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    # ตัวอย่างการใช้งานฟังก์ชันตรวจสอบเมนู
    
    # 1. แสดงเมนูทั้งหมดที่มี
    print("Available Menus:")
    menus = get_all_menus()
    for menu in menus:
        print(f"{menu[0]}: {menu[1]}")
    
    # 2. ตรวจสอบว่ามีเมนูที่ต้องการหรือไม่
    search_menu = "Pizza"
    if check_menu_exists(search_menu):
        print(f"\n'{search_menu}' is available in the database.")
    else:
        print(f"\n'{search_menu}' is NOT available in the database.")
    
    # 3. แสดงข้อมูลเมนูเฉพาะ (เปลี่ยน menu_id ตามต้องการ)
    menu_id_to_display = 1
    display_menu(menu_id_to_display)