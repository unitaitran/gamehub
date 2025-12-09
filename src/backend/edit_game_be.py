import mysql.connector
from mysql.connector import Error
from .auth import get_db_connection

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

def get_game_genres_from_db(game_id):
    """Lấy genres của game từ database"""
    connection = get_database_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT c.name
        FROM game_category gc
        JOIN categories c ON gc.category_id = c.id
        WHERE gc.game_id = %s AND c.isDeleted = 0
        ORDER BY c.name
        """
        cursor.execute(query, (game_id,))
        genres = cursor.fetchall()
        return [genre["name"] for genre in genres]
        
    except Error as e:
        print(f"Error getting game genres from database: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_game_in_db(game_id, game_data):
    connection = get_db_connection()
    if not connection:
        print("Database connection failed")
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)  # Sử dụng dictionary cursor
        
        # Kiểm tra game tồn tại
        cursor.execute(
            "SELECT id FROM games WHERE id = %s AND isDeleted = 0",
            (game_id,)
        )
        if not cursor.fetchone():
            print(f"Game with ID not found: {game_id}")
            return False
        
        # Cập nhật thông tin game
        query = """
        UPDATE games 
        SET title = %s, description = %s, price = %s 
        WHERE id = %s AND isDeleted = 0
        """
        cursor.execute(query, (
            game_data["name"],
            game_data["description"],
            game_data["price"],
            game_id
        ))
        
        # Cập nhật game_details - chỉ cập nhật price_original nếu có
        if "price_original" in game_data:
            update_details_query = """
            UPDATE game_details 
            SET price_original = %s
            WHERE game_id = %s
            """
            cursor.execute(update_details_query, (
                game_data["price_original"],
                game_id
            ))
        
        # Xóa genres cũ
        cursor.execute("DELETE FROM game_category WHERE game_id = %s", (game_id,))
        
        # Thêm genres mới
        for genre in game_data["genres"]:
            cursor.execute(
                "SELECT id FROM categories WHERE name = %s AND isDeleted = 0",
                (genre,)
            )
            result = cursor.fetchone()
            if not result:
                print(f"Thể loại '{genre}' không tồn tại trong bảng categories")
                connection.rollback()
                return False
            cursor.execute(
                "INSERT INTO game_category (game_id, category_id) VALUES (%s, %s)",
                (game_id, result["id"])
            )
        
        connection.commit()
        print(f"Game ID {game_id} updated successfully")
        return True
    
    except Exception as e:
        print(f"Error updating game ID {game_id}: {e}")
        connection.rollback()
        return False
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_game_by_id_for_edit(game_id):
    """Lấy thông tin game để edit (bao gồm genres)"""
    connection = get_database_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            g.id, g.title, g.description, g.price, g.image_url_vertical, g.image_url_horizontal, 
            g.release_date, g.link_download, g.isDeleted, COALESCE(gd.price_original, 0) as price_original
        FROM games g
        LEFT JOIN game_details gd ON g.id = gd.game_id
        WHERE g.id = %s AND g.isDeleted = 0
        """
        cursor.execute(query, (game_id,))
        game = cursor.fetchone()
        
        if game:
            genres = get_game_genres_from_db(game_id)
            price_value = float(game["price"]) if game["price"] else 0.0
            price_display = "Free" if price_value == 0.0 else f"${price_value:.2f}"
            image_url = game["image_url_vertical"] or game["image_url_horizontal"] or ""
            release_date = game["release_date"].strftime("%Y-%m-%d") if game["release_date"] else ""
            
            return {
                "id": game["id"],
                "name": game["title"],
                "description": game["description"] or "Game description not available",
                "price": price_value,
                "price_original": float(game["price_original"]) if game["price_original"] else 0.0,
                "price_display": price_display,
                "image": image_url,
                "image_vertical": game["image_url_vertical"] or "",
                "image_horizontal": game["image_url_horizontal"] or "",
                "release_date": release_date,
                "download_link": game["link_download"] or "",
                "genres": genres,
                "source_list": "database",
                "isDeleted": game["isDeleted"]
            }
        
        return None
        
    except Error as e:
        print(f"Error getting game ID {game_id} for editing: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()