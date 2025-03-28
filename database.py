import sqlite3
from io import BytesIO

class FoodMenuDB:
    def __init__(self, db_path="food_menu.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Initialize database and create tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    image BLOB,
                    search_keywords TEXT
                )
            ''')
            conn.commit()

    def insert_menu(self, name, image_path, search_keywords=None):
        """Insert a new menu item into database"""
        try:
            with open(image_path, "rb") as file:
                image_data = file.read()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if search_keywords:
                    cursor.execute(
                        "INSERT INTO menu (name, image, search_keywords) VALUES (?, ?, ?)", 
                        (name, image_data, search_keywords)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO menu (name, image) VALUES (?, ?)", 
                        (name, image_data)
                    )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting {name}: {str(e)}")
            return False

    def search_menu(self, text):
        """Search for menu items by name or keywords"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                search_term = f"%{text}%"
                
                query = """
                SELECT name, image FROM menu 
                WHERE name LIKE ? COLLATE NOCASE
                OR search_keywords LIKE ? COLLATE NOCASE
                ORDER BY CASE
                    WHEN name LIKE ? COLLATE NOCASE THEN 1
                    WHEN search_keywords LIKE ? COLLATE NOCASE THEN 2
                    ELSE 3
                END
                LIMIT 1
                """
                
                cursor.execute(query, (search_term, search_term, search_term, search_term))
                return cursor.fetchone()
        except Exception as e:
            print(f"Database search error: {str(e)}")
            return None

    def get_menu_image(self, menu_name):
        """Get image data for a menu item"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT image FROM menu WHERE name = ? COLLATE NOCASE", 
                    (menu_name,)
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error getting image: {str(e)}")
            return None

    def list_all_menus(self):
        """List all menu items for debugging"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, search_keywords FROM menu")
                return cursor.fetchall()
        except Exception as e:
            print(f"Error listing menus: {str(e)}")
            return []