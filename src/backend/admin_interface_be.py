import mysql.connector
from mysql.connector import Error
from .auth import get_db_connection

def get_database_connection():
    """Tạo kết nối đến database"""
    return get_db_connection()

def get_all_games_from_db():
    """Lấy tất cả game từ bảng games"""
    connection = get_database_connection()
    if not connection:
        print("Database connection failed, returning empty list")
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            g.id,
            g.title,
            g.description,
            g.price,
            g.image_url_vertical,
            g.image_url_horizontal,
            g.release_date,
            g.link_download,
            g.isDeleted,
            GROUP_CONCAT(c.name SEPARATOR ', ') as genres
        FROM games g
        LEFT JOIN game_category gc ON g.id = gc.game_id
        LEFT JOIN categories c ON gc.category_id = c.id AND c.isDeleted = 0
        WHERE g.isDeleted = 0
        GROUP BY g.id
        ORDER BY g.id DESC
        """
        cursor.execute(query)
        games = cursor.fetchall()
        
        formatted_games = []
        for game in games:
            print(f"Game ID: {game['id']}, Title: {game['title']}, Genres: {game['genres']}")
            price_value = float(game["price"]) if game["price"] else 0.0
            price_display = "Free" if price_value == 0.0 else f"${price_value:.2f}"
            image_url = game["image_url_vertical"] or game["image_url_horizontal"] or ""
            release_date = game["release_date"].strftime("%Y-%m-%d") if game["release_date"] else ""
            
            # Xử lý category: nếu genres là None hoặc rỗng, đặt là "Database Games"
            category = game["genres"] if game["genres"] else "Database Games"
            
            formatted_game = {
                "id": game["id"],
                "name": game["title"],
                "description": game["description"] or "Game description not available",
                "price": price_value,
                "price_display": price_display,
                "image": image_url,
                "image_vertical": game["image_url_vertical"] or "",
                "image_horizontal": game["image_url_horizontal"] or "",
                "release_date": release_date,
                "download_link": game["link_download"] or "",
                "category": category,
                "source_list": "database",
                "isDeleted": game["isDeleted"]
            }
            formatted_games.append(formatted_game)
        
        return formatted_games
        
    except Error as e:
        print(f"Error fetching games from database: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_all_users_from_db():
    """Lấy tất cả user từ bảng users"""
    connection = get_database_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            id,
            username,
            password,
            email,
            fullname,
            age,
            gender,
            coin,
            role_id,
            isDeleted,
            phone
        FROM users 
        WHERE isDeleted = 0
        ORDER BY id DESC
        """
        cursor.execute(query)
        users = cursor.fetchall()
        
        # Chuyển đổi dữ liệu để phù hợp với format hiện tại
        formatted_users = []
        for user in users:
            # Xác định role
            role = "admin" if user["role_id"] == 1 else "user"
            
            # Xử lý fullname - tách thành first_name và last_name
            fullname = user["fullname"] or ""
            name_parts = fullname.split(" ", 1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            formatted_user = {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "first_name": first_name,
                "last_name": last_name,
                "fullname": user["fullname"] or "",
                "age": user["age"] or 0,
                "gender": user["gender"] or "",
                "phone": user["phone"] or "",
                "balance": float(user["coin"]) if user["coin"] else 0.0,
                "role": role,
                "role_id": user["role_id"],
                "isDeleted": user["isDeleted"]
            }
            formatted_users.append(formatted_user)
        
        return formatted_users
        
    except Error as e:
        print(f"Error fetching users from database: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def search_games_from_db(search_term, category_filter="all"):
    """Tìm kiếm game trong database"""
    connection = get_database_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Xây dựng query với điều kiện tìm kiếm
        query = """
        SELECT 
            g.id, g.title, g.description, g.price, g.image_url_vertical, g.image_url_horizontal, 
            g.release_date, g.link_download, g.isDeleted,
            GROUP_CONCAT(c.name SEPARATOR ', ') as genres
        FROM games g
        LEFT JOIN game_category gc ON g.id = gc.game_id
        LEFT JOIN categories c ON gc.category_id = c.id
        WHERE g.isDeleted = 0
        """
        
        params = []
        
        # Thêm điều kiện tìm kiếm
        if search_term:
            query += " AND (g.title LIKE %s OR g.description LIKE %s)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern])
        
        # Thêm điều kiện category (nếu cần)
        if category_filter != "all":
            # Vì database không có category, ta có thể bỏ qua hoặc thêm logic khác
            pass
        
        query += " GROUP BY g.id ORDER BY g.id DESC"
        
        cursor.execute(query, params)
        games = cursor.fetchall()
        
        # Chuyển đổi dữ liệu
        formatted_games = []
        for game in games:
            # Xử lý price - có thể là 0.00 cho free games
            price_value = float(game["price"]) if game["price"] else 0.0
            price_display = "Free" if price_value == 0.0 else f"${price_value:.2f}"
            
            # Sử dụng image_url_vertical làm ảnh chính, fallback sang image_url_horizontal
            image_url = game["image_url_vertical"] or game["image_url_horizontal"] or ""
            
            # Xử lý release_date
            release_date = game["release_date"].strftime("%Y-%m-%d") if game["release_date"] else ""
            
            formatted_game = {
                "id": game["id"],
                "name": game["title"],
                "description": game["description"] or "Game description not available",
                "price": price_value,
                "price_display": price_display,
                "image": image_url,
                "image_vertical": game["image_url_vertical"] or "",
                "image_horizontal": game["image_url_horizontal"] or "",
                "release_date": release_date,
                "download_link": game["link_download"] or "",
                "category": game["genres"] or "Database Games",  # Sử dụng genres từ database
                "source_list": "database",
                "isDeleted": game["isDeleted"]
            }
            formatted_games.append(formatted_game)
        
        return formatted_games
        
    except Error as e:
        print(f"Error searching games in database: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def search_users_from_db(search_term):
    """Tìm kiếm user trong database"""
    connection = get_database_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            id, username, password, email, fullname, age, gender, 
            coin, role_id, isDeleted, phone
        FROM users 
        WHERE isDeleted = 0
        """
        
        params = []
        
        if search_term:
            query += " AND (username LIKE %s OR email LIKE %s OR fullname LIKE %s)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        query += " ORDER BY id DESC"
        
        cursor.execute(query, params)
        users = cursor.fetchall()
        
        # Chuyển đổi dữ liệu
        formatted_users = []
        for user in users:
            role = "admin" if user["role_id"] == 1 else "user"
            
            # Xử lý fullname - tách thành first_name và last_name
            fullname = user["fullname"] or ""
            name_parts = fullname.split(" ", 1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            formatted_user = {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "first_name": first_name,
                "last_name": last_name,
                "fullname": user["fullname"] or "",
                "age": user["age"] or 0,
                "gender": user["gender"] or "",
                "phone": user["phone"] or "",
                "balance": float(user["coin"]) if user["coin"] else 0.0,
                "role": role,
                "role_id": user["role_id"],
                "isDeleted": user["isDeleted"]
            }
            formatted_users.append(formatted_user)
        
        return formatted_users
        
    except Error as e:
        print(f"Error searching users in database: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_game_by_id(game_id):
    """Lấy thông tin game theo ID"""
    connection = get_database_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            g.id, g.title, g.description, g.price, g.image_url_vertical, g.image_url_horizontal, 
            g.release_date, g.link_download, g.isDeleted,
            GROUP_CONCAT(c.name SEPARATOR ', ') as genres
        FROM games g
        LEFT JOIN game_category gc ON g.id = gc.game_id
        LEFT JOIN categories c ON gc.category_id = c.id
        WHERE g.id = %s AND g.isDeleted = 0
        GROUP BY g.id
        """
        cursor.execute(query, (game_id,))
        game = cursor.fetchone()
        
        if game:
            # Xử lý price - có thể là 0.00 cho free games
            price_value = float(game["price"]) if game["price"] else 0.0
            price_display = "Free" if price_value == 0.0 else f"${price_value:.2f}"
            
            # Sử dụng image_url_vertical làm ảnh chính, fallback sang image_url_horizontal
            image_url = game["image_url_vertical"] or game["image_url_horizontal"] or ""
            
            # Xử lý release_date
            release_date = game["release_date"].strftime("%Y-%m-%d") if game["release_date"] else ""
            
            return {
                "id": game["id"],
                "name": game["title"],
                "description": game["description"] or "Game description not available",
                "price": price_value,
                "price_display": price_display,
                "image": image_url,
                "image_vertical": game["image_url_vertical"] or "",
                "image_horizontal": game["image_url_horizontal"] or "",
                "release_date": release_date,
                "download_link": game["link_download"] or "",
                "category": game["genres"] or "Database Games",  # Sử dụng genres từ database
                "source_list": "database",
                "isDeleted": game["isDeleted"]
            }
        
        return None
        
    except Error as e:
        print(f"Error fetching game by ID: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_user_by_id(user_id):
    """Lấy thông tin user theo ID"""
    connection = get_database_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            id, username, password, email, fullname, age, gender, 
            coin, role_id, isDeleted, phone
        FROM users 
        WHERE id = %s AND isDeleted = 0
        """
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        if user:
            role = "admin" if user["role_id"] == 1 else "user"
            
            # Xử lý fullname - tách thành first_name và last_name
            fullname = user["fullname"] or ""
            name_parts = fullname.split(" ", 1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "first_name": first_name,
                "last_name": last_name,
                "fullname": user["fullname"] or "",
                "age": user["age"] or 0,
                "gender": user["gender"] or "",
                "phone": user["phone"] or "",
                "balance": float(user["coin"]) if user["coin"] else 0.0,
                "role": role,
                "role_id": user["role_id"],
                "isDeleted": user["isDeleted"]
            }
        
        return None
        
    except Error as e:
        print(f"Error fetching user by ID: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete_game(game_id):
    """Đánh dấu game là đã xoá (isDeleted=1) trong database"""
    connection = get_database_connection()
    if not connection:
        print("Database connection failed")
        return False
    try:
        cursor = connection.cursor()
        query = "UPDATE games SET isDeleted = 1 WHERE id = %s"
        cursor.execute(query, (game_id,))
        if cursor.rowcount == 0:
            print(f"No game found with ID: {game_id}")
            connection.rollback()
            return False
        connection.commit()
        print(f"Game with ID {game_id} marked as deleted")
        return True
    except Exception as e:
        print(f"Error deleting game: {e}")
        if connection.is_connected():
            connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete_user(user_id):
    """Đánh dấu user là đã xoá (isDeleted=1) trong database"""
    connection = get_database_connection()
    if not connection:
        print("Database connection failed")
        return False
    try:
        cursor = connection.cursor()
        query = "UPDATE users SET isDeleted = 1 WHERE id = %s"
        cursor.execute(query, (user_id,))
        if cursor.rowcount == 0:
            print(f"No user found with ID: {user_id}")
            connection.rollback()
            return False
        connection.commit()
        print(f"User with ID {user_id} marked as deleted")
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        if connection.is_connected():
            connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


            from .auth import get_db_connection

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