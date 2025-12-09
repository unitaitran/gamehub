from .auth import get_db_connection
from mysql.connector import Error


def get_top_rated_games():
    try:
        conn = get_db_connection()
        if conn is None:
            return {"success": False, "error": "Can't connect database!"}

        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                g.id,
                g.title,
                g.title as name,
                g.image_url_horizontal,
                g.image_url_vertical,
                COALESCE(g.price, 0) as price,
                COALESCE(gd.price_original, 0) as price_original,
                COALESCE(gd.rating, 0) as rating,
                CASE 
                    WHEN COALESCE(gd.price_original, 0) > COALESCE(g.price, 0) AND COALESCE(gd.price_original, 0) > 0 
                    THEN ROUND(((COALESCE(gd.price_original, 0) - COALESCE(g.price, 0)) / COALESCE(gd.price_original, 0)) * 100)
                    ELSE 0
                END as discount_percentage
            FROM 
                games g
            LEFT JOIN game_details gd ON g.id = gd.game_id
            WHERE 
                g.isDeleted = FALSE
                AND COALESCE(gd.rating, 0) > 0
            GROUP BY g.id, g.title, g.image_url_horizontal, g.image_url_vertical, g.price, gd.price_original, gd.rating
            ORDER BY 
                gd.rating DESC, g.id DESC
            LIMIT 20;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return {"success": True, "games": rows}

    except Error as e:
        return {"success": False, "error": f"Error query {e}"}


def get_top_paid_games():
    try:
        conn = get_db_connection()
        if conn is None:
            return {"success": False, "error": "Can't connect database!"}

        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                g.id,
                g.title,
                g.title as name,
                g.price,
                g.image_url_horizontal,
                g.image_url_vertical,
                COALESCE(gd.price_original, 0) as price_original,
                COALESCE(gd.rating, 0) as rating,
                CASE 
                    WHEN COALESCE(gd.price_original, 0) > COALESCE(g.price, 0) AND COALESCE(gd.price_original, 0) > 0 
                    THEN ROUND(((COALESCE(gd.price_original, 0) - COALESCE(g.price, 0)) / COALESCE(gd.price_original, 0)) * 100)
                    ELSE 0
                END as discount_percentage
            FROM games g
            LEFT JOIN game_details gd ON g.id = gd.game_id
            WHERE 
                g.price > 0
                AND g.isDeleted = FALSE
                AND COALESCE(gd.rating, 0) > 0
            GROUP BY g.id, g.title, g.price, g.image_url_horizontal, g.image_url_vertical, gd.price_original, gd.rating
            ORDER BY gd.rating DESC, g.price DESC
            LIMIT 20;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return {"success": True, "games": rows}

    except Error as e:
        return {"success": False, "error": f"Error query {e}"}


def get_top_free_games():
    try:
        conn = get_db_connection()
        if conn is None:
            return {"success": False, "error": "Can't connect database!"}

        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                g.id,
                g.title,
                g.title as name,
                g.price,
                g.image_url_horizontal,
                g.image_url_vertical,
                COALESCE(gd.price_original, 0) as price_original,
                COALESCE(gd.rating, 0) as rating,
                CASE 
                    WHEN COALESCE(gd.price_original, 0) > COALESCE(g.price, 0) AND COALESCE(gd.price_original, 0) > 0 
                    THEN ROUND(((COALESCE(gd.price_original, 0) - COALESCE(g.price, 0)) / COALESCE(gd.price_original, 0)) * 100)
                    ELSE 0
                END as discount_percentage
            FROM games g
            LEFT JOIN game_details gd ON g.id = gd.game_id
            WHERE 
                g.price = 0
                AND g.isDeleted = FALSE
                AND COALESCE(gd.rating, 0) > 0
            GROUP BY g.id, g.title, g.price, g.image_url_horizontal, g.image_url_vertical, gd.price_original, gd.rating
            ORDER BY gd.rating DESC, g.id DESC
            LIMIT 20;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return {"success": True, "games": rows}

    except Error as e:
        return {"success": False, "error": f"Error query {e}"}


def search_games_by_title(keyword):
    try:
        conn = get_db_connection()
        if conn is None:
            return {"success": False, "error": "Can't connect database!"}
        
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT id, title, image_url_horizontal, image_url_vertical, price
            FROM games
            WHERE title LIKE %s AND isDeleted = FALSE
            ORDER BY title
            LIMIT 10;
        """
        like_pattern = f"%{keyword}%"
        cursor.execute(query, (like_pattern,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        return {"success": True, "games": results}

    except Error as e:
        return {"success": False, "error": str(e)}


def get_banner_games():
    """Lấy 4 game cho banner từ database"""
    try:
        conn = get_db_connection()
        if conn is None:
            return {"success": False, "error": "Can't connect database!"}

        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                g.id,
                g.title,
                g.description,
                g.price,
                g.image_url_horizontal,
                g.image_url_vertical
            FROM 
                games g
            WHERE 
                g.isDeleted = FALSE
            ORDER BY 
                g.id DESC
            LIMIT 4;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return {"success": True, "games": rows}

    except Error as e:
        return {"success": False, "error": f"Error query {e}"}


def get_custom_banner_games(game_ids):
    """Lấy game cho banner theo danh sách ID cụ thể"""
    try:
        conn = get_db_connection()
        if conn is None:
            return {"success": False, "error": "Can't connect database!"}

        cursor = conn.cursor(dictionary=True)
        # Tạo placeholders cho IN clause
        placeholders = ','.join(['%s'] * len(game_ids))
        query = f"""
            SELECT 
                g.id,
                g.title,
                g.description,
                g.price,
                g.image_url_horizontal,
                g.image_url_vertical
            FROM 
                games g
            WHERE 
                g.id IN ({placeholders})
                AND g.isDeleted = FALSE
            ORDER BY 
                FIELD(g.id, {placeholders})
        """
        # Duplicate game_ids để sử dụng cho cả IN và FIELD
        params = game_ids + game_ids
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return {"success": True, "games": rows}

    except Error as e:
        return {"success": False, "error": f"Error query {e}"}
