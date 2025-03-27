import sqlite3

def create_database():
    conn = sqlite3.connect("food_menu.db")  # สร้างหรือเชื่อมต่อฐานข้อมูล
    cursor = conn.cursor()
    
    # สร้างตารางเมนูอาหาร
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
    with open(image_path, "rb") as file:
        image_data = file.read()  # อ่านไฟล์รูปภาพเป็น binary data
    
    conn = sqlite3.connect("food_menu.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO menu (name, image) VALUES (?, ?)", (name, image_data))
    
    conn.commit()
    conn.close()
    print(f"Inserted: {name}")

# สร้างฐานข้อมูลและตาราง
create_database()

# ตัวอย่างการเพิ่มเมนูอาหาร (เปลี่ยน path เป็นรูปภาพที่มีอยู่ในเครื่อง)
# insert_menu("ผัดไทย", "padthai.jpg")
# insert_menu("ต้มยำกุ้ง", "tomyum.jpg")

# เพิ่มเมนู Pizza
insert_menu("Pizza", "D:\\Whisper\\pizza.webp")
insert_menu("พิซซ่า", "D:\\Whisper\\pizza.webp")
insert_menu("Tom Yum", "D:\\Whisper\\TomYum.jpg")
