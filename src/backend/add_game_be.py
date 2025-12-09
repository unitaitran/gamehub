import mysql.connector
from mysql.connector import Error
from .auth import get_db_connection
from datetime import datetime

def get_database_connection():
    """Tạo kết nối đến database"""
    return get_db_connection()

def get_all_categories_from_db():
    """Lấy tất cả categories từ database"""
    connection = get_database_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT id, name
        FROM categories 
        WHERE isDeleted = 0
        ORDER BY name
        """
        cursor.execute(query)
        categories = cursor.fetchall()
        return categories
        
    except Error as e:
        print(f"Error getting categories from database: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_next_game_id():
    """Lấy ID tiếp theo cho game (bắt đầu từ 2277011)"""
    connection = get_database_connection()
    if not connection:
        return 2277011
    
    try:
        cursor = connection.cursor()
        query = "SELECT MAX(id) as max_id FROM games"
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result and result[0]:
            next_id = max(2277011, result[0] + 1)
        else:
            next_id = 2277011
        
        return next_id
        
    except Error as e:
        print(f"Error getting next game ID: {e}")
        return 2277011
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_game_to_db(game_data):
    """Thêm game mới vào database"""
    connection = get_database_connection()
    if not connection:
        print("Database connection failed")
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Lấy ID tiếp theo cho game
        game_id = get_next_game_id()
        print(f"Thêm game với ID: {game_id}")
        
        # Thêm game vào bảng games
        current_date = datetime.now().strftime('%Y-%m-%d')
        insert_game_query = """
        INSERT INTO games (id, title, description, price, image_url_vertical, image_url_horizontal, release_date, isDeleted)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 0)
        """
        cursor.execute(insert_game_query, (
            game_id,
            game_data["name"],
            game_data["description"],
            game_data["price"],
            game_data["vertical_image"],
            game_data["horizontal_image"],
            current_date
        ))
        
        # Thêm game details vào bảng game_details
        insert_details_query = """
        INSERT INTO game_details (game_id, recommend_cpu, recommend_gpu, recommend_ram, recommend_storage, price_original)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            recommend_cpu = VALUES(recommend_cpu),
            recommend_gpu = VALUES(recommend_gpu),
            recommend_ram = VALUES(recommend_ram),
            recommend_storage = VALUES(recommend_storage),
            price_original = VALUES(price_original)
        """
        cursor.execute(insert_details_query, (
            game_id,
            game_data["cpu"],
            game_data["gpu"],
            game_data["ram"],
            game_data["storage"],
            game_data["price_original"]
        ))
        
        # Thêm genres vào bảng game_category
        if game_data.get("genres"):
            print(f"Thêm genres: {game_data['genres']}")
            for genre_name in game_data["genres"]:
                # Tìm category_id
                get_category_query = "SELECT id FROM categories WHERE name = %s AND isDeleted = 0"
                cursor.execute(get_category_query, (genre_name,))
                category_result = cursor.fetchone()
                
                if category_result:
                    category_id = category_result["id"]
                    # Thêm liên kết game-category
                    insert_genre_query = "INSERT INTO game_category (game_id, category_id) VALUES (%s, %s)"
                    cursor.execute(insert_genre_query, (game_id, category_id))
                    print(f"Thêm genre '{genre_name}' (category_id: {category_id}) cho game {game_id}")
                else:
                    print(f"Thể loại '{genre_name}' không tồn tại trong database")
        
        connection.commit()
        print(f"Game ID {game_id} added successfully")
        return True
        
    except Exception as e:
        print(f"Error adding game: {e}")
        if connection.is_connected():
            connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def validate_game_data(game_data):
    """Kiểm tra dữ liệu game trước khi thêm"""
    errors = []
    
    if not game_data.get("name", "").strip():
        errors.append("Tên game không được để trống")
    
    if not game_data.get("description", "").strip():
        errors.append("Mô tả game không được để trống")
    
    if not game_data.get("genres"):
        errors.append("Phải chọn ít nhất một thể loại")
    
    try:
        price = float(game_data.get("price", 0))
        if price < 0:
            errors.append("Game price must be greater than 0")
    except:
        errors.append("Giá game không hợp lệ")
    
    if not game_data.get("horizontal_image", "").strip():
        errors.append("Link ảnh ngang không được để trống")
    
    if not game_data.get("vertical_image", "").strip():
        errors.append("Link ảnh dọc không được để trống")
    
    if not game_data.get("cpu", "").strip():
        errors.append("CPU không được để trống")
    
    if not game_data.get("gpu", "").strip():
        errors.append("GPU không được để trống")
    
    if not game_data.get("ram", "").strip():
        errors.append("RAM không được để trống")
    
    if not game_data.get("storage", "").strip():
        errors.append("Storage không được để trống")
    
    try:
        price_original = float(game_data.get("price_original", 0))
        if price_original < 0:
            errors.append("Giá gốc không được âm")
    except:
        errors.append("Giá gốc không hợp lệ")
    
    return errors 