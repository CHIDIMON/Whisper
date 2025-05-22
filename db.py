import sqlite3

def create_database():
    conn = sqlite3.connect("food_menu.db")  # สร้างหรือเชื่อมต่อฐานข้อมูล
    cursor = conn.cursor()
    
    # สร้างตารางเมนูอาหาร (เก็บข้อมูลรูปภาพเป็น BLOB)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image BLOB
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database and table created successfully.")

def insert_menu(name, image_path):
    try:
        with open(image_path, "rb") as file:
            image_data = file.read()  # อ่านไฟล์รูปภาพเป็น binary data
    
        conn = sqlite3.connect("food_menu.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO menu (name, image) VALUES (?, ?)", (name, image_data))
        
        conn.commit()
        print(f"Inserted: {name}")
    except Exception as e:
        print(f"Error inserting {name}: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    # สร้างฐานข้อมูลและตาราง
    create_database()
    
    # ตัวอย่างการเพิ่มเมนูอาหาร (แก้ไข path ให้ถูกต้อง)
    insert_menu("Pizza", "/Users/chidimon/Projectcode/Whisper/image/Pizza.webp")
    insert_menu("ต้มยำ", "/Users/chidimon/Projectcode/Whisper/image/Tomyum.jpg")
    insert_menu("Tom Yum", "/Users/chidimon/Projectcode/Whisper/image/Tomyum.jpg")
    insert_menu("Tom Yam", "/Users/chidimon/Projectcode/Whisper/image/Tomyum.jpg")
