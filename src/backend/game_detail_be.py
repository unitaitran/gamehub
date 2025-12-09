import mysql.connector
from mysql.connector import Error
from .auth import get_db_connection

def get_database_connection():
    return get_db_connection()

def check_game_in_cart(user_id, game_id):
    """Kiểm tra xem game đã có trong cart chưa"""
    connection = get_database_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query kiểm tra cart - chỉ SELECT user_id và game_id
        query = "SELECT user_id, game_id FROM cart_items WHERE user_id = %s AND game_id = %s"
        cursor.execute(query, (user_id, game_id))
        result = cursor.fetchone()
        in_cart = result is not None
        return in_cart
    except Error as e:
        print(f"Error checking game in cart: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def check_game_purchased(user_id, game_id):
    """Kiểm tra xem user đã mua game này chưa"""
    connection = get_database_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query kiểm tra purchase - chỉ SELECT user_id và game_id
        query = "SELECT user_id, game_id FROM user_games WHERE user_id = %s AND game_id = %s"
        cursor.execute(query, (user_id, game_id))
        result = cursor.fetchone()
        is_purchased = result is not None
        return is_purchased
    except Error as e:
        print(f"Error checking game purchase: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_game_detail_by_id(game_id, user_id=None):
    connection = get_database_connection()
    if not connection:
        return None
    try:
        cursor = connection.cursor(dictionary=True)
        query = '''
        SELECT g.id, g.title, g.description, g.price, g.image_url_vertical, g.image_url_horizontal,
               g.release_date, g.link_download, g.isDeleted,
               GROUP_CONCAT(c.name SEPARATOR ', ') as genres
        FROM games g
        LEFT JOIN game_category gc ON g.id = gc.game_id
        LEFT JOIN categories c ON gc.category_id = c.id AND c.isDeleted = 0
        WHERE g.id = %s AND g.isDeleted = 0
        GROUP BY g.id
        '''
        cursor.execute(query, (game_id,))
        game = cursor.fetchone()
        cursor.close()
        
        if game:
            # Lấy cấu hình recommend từ bảng game_details
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT recommend_cpu, recommend_gpu, recommend_ram, recommend_storage, rating
                FROM game_details 
                WHERE game_id = %s
            """, (game_id,))
            config = cursor.fetchone()
            cursor.close()
            
            min_config = {}
            if config:
                min_config = {
                    "cpu": config["recommend_cpu"] if config["recommend_cpu"] else "",
                    "gpu": config["recommend_gpu"] if config["recommend_gpu"] else "",
                    "ram": config["recommend_ram"] if config["recommend_ram"] else "",
                    "storage": config["recommend_storage"] if config["recommend_storage"] else ""
                }
                # Lấy rating từ game_details thay vì reviews
                avg_rating = round(config["rating"], 1) if config["rating"] is not None else 0
            else:
                min_config = {
                    "cpu": "",
                    "gpu": "",
                    "ram": "",
                    "storage": ""
                }
                avg_rating = 0
            
            # Kiểm tra game đã được mua chưa
            is_purchased = False
            in_cart = False
            if user_id:
                is_purchased = check_game_purchased(user_id, game_id)
                in_cart = check_game_in_cart(user_id, game_id)
            
            return {
                "id": game["id"],
                "name": game["title"],
                "title": game["title"],  # Thêm title để đồng nhất với frontend
                "description": game["description"] or "Game description not available",
                "price": float(game["price"]) if game["price"] else 0.0,
                "image": game["image_url_horizontal"] or game["image_url_vertical"] or "",
                "genres": game["genres"],
                "min_config": min_config,
                "rating": avg_rating,
                "is_purchased": is_purchased,
                "in_cart": in_cart
            }
        return None
    except Error as e:
        print(f"Error fetching game detail: {e}")
        return None
    finally:
        if connection.is_connected():
            connection.close()

def get_top_rated_games(limit=4):
    connection = get_database_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor(dictionary=True)
        query = '''
        SELECT 
            g.id, g.title, g.price, g.image_url_horizontal, g.image_url_vertical,
            COALESCE(gd.rating, 0) as rating,
            COALESCE(gd.price_original, 0) as price_original,
            CASE 
                WHEN COALESCE(gd.price_original, 0) > COALESCE(g.price, 0) AND COALESCE(gd.price_original, 0) > 0 
                THEN ROUND(((COALESCE(gd.price_original, 0) - COALESCE(g.price, 0)) / COALESCE(gd.price_original, 0)) * 100)
                ELSE 0
            END as discount_percentage
        FROM games g
        LEFT JOIN game_details gd ON g.id = gd.game_id
        WHERE g.isDeleted = 0
            AND COALESCE(gd.rating, 0) > 0
        GROUP BY g.id, g.title, g.price, g.image_url_horizontal, g.image_url_vertical, gd.rating, gd.price_original
        ORDER BY gd.rating DESC, g.id DESC
        LIMIT %s
        '''
        cursor.execute(query, (limit,))
        games = cursor.fetchall()
        
        result = []
        for game in games:
            result.append({
                "id": game["id"],
                "name": game["title"],
                "title": game["title"],
                "price": float(game["price"]) if game["price"] else 0.0,
                "image": game["image_url_horizontal"] or game["image_url_vertical"] or "",
                "image_url_horizontal": game["image_url_horizontal"],
                "image_url_vertical": game["image_url_vertical"],
                "price_original": float(game["price_original"]) if game["price_original"] else 0.0,
                "rating": round(game["rating"], 1) if game["rating"] is not None else 0,
                "discount_percentage": game["discount_percentage"]
            })
        return result
    except Error as e:
        print(f"Error fetching top rated games: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
