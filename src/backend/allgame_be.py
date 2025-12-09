from .auth import get_db_connection
from mysql.connector import Error

def get_all_games_by_release_date(page=1, per_page=12, filters=None, search=None):
    """
    Lấy tất cả game từ database theo ngày ra mắt mới nhất
    """
    try:
        conn = get_db_connection()
        if conn is None:
            print("Connection failed in get_all_games_by_release_date")  # Debug
            return {"success": False, "error": "Can't connect database!"}

        cursor = conn.cursor(dictionary=True)
        
        # Base query với filter cơ bản
        base_query = """
            SELECT 
                g.id,
                g.title,
                g.description,
                g.price,
                g.image_url_horizontal,
                g.image_url_vertical,
                g.release_date,
                g.link_download,
                g.isDeleted,
                gd.recommend_cpu,
                gd.recommend_gpu,
                gd.recommend_ram,
                gd.recommend_storage,
                GROUP_CONCAT(c.name) as genre,
                0 as views,
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
            LEFT JOIN game_category gc ON g.id = gc.game_id
            LEFT JOIN categories c ON gc.category_id = c.id
            WHERE 
                g.isDeleted = FALSE
        """
        
        # Thêm filter nếu có
        where_conditions = []
        params = []
        
        if filters:
            if filters.get('genre') and filters['genre'] != '- Tất cả -':
                where_conditions.append("c.name LIKE %s")
                params.append(f"%{filters['genre']}%")
            
            if filters.get('ram') and filters['ram'] != '- Tất cả -':
                where_conditions.append("gd.recommend_ram LIKE %s")
                params.append(f"%{filters['ram']}%")
            
            if filters.get('storage') and filters['storage'] != '- Tất cả -':
                where_conditions.append("gd.recommend_storage LIKE %s")
                params.append(f"%{filters['storage']}%")
            
            if filters.get('cpu') and filters['cpu'] != '- Tất cả -':
                where_conditions.append("gd.recommend_cpu LIKE %s")
                params.append(f"%{filters['cpu']}%")
            
            if filters.get('gpu') and filters['gpu'] != '- Tất cả -':
                where_conditions.append("gd.recommend_gpu LIKE %s")
                params.append(f"%{filters['gpu']}%")
        
        # Thêm điều kiện tìm kiếm
        if search and search.strip():
            where_conditions.append("(g.title LIKE %s OR g.description LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        if where_conditions:
            base_query += " AND " + " AND ".join(where_conditions)
        
        # Thêm ORDER BY và LIMIT
        base_query += """
            GROUP BY g.id
            ORDER BY g.release_date DESC, g.id DESC
            LIMIT %s OFFSET %s
        """
        
        offset = (page - 1) * per_page
        params.extend([per_page, offset])
        
        print(f"Executing query: {base_query}")  # Debug
        print(f"Parameters: {params}")  # Debug
        
        cursor.execute(base_query, params)
        games = cursor.fetchall()
        
        # Lấy tổng số game để tính pagination
        count_query = """
            SELECT COUNT(DISTINCT g.id) as total
            FROM games g
            LEFT JOIN game_details gd ON g.id = gd.game_id
            LEFT JOIN game_category gc ON g.id = gc.game_id
            LEFT JOIN categories c ON gc.category_id = c.id
            WHERE g.isDeleted = FALSE
        """
        
        if where_conditions:
            count_query += " AND " + " AND ".join(where_conditions)
        
        print(f"Executing count query: {count_query}")  # Debug
        print(f"Count parameters: {params[:-2]}")  # Debug (loại bỏ LIMIT và OFFSET)
        
        cursor.execute(count_query, params[:-2])  # Không cần LIMIT và OFFSET cho count
        total_result = cursor.fetchone()
        total_games = total_result['total'] if total_result else 0
        
        cursor.close()
        conn.close()

        print(f"Games fetched: {len(games)}")  # Debug
        return {
            "success": True, 
            "games": games, 
            "total": total_games,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_games + per_page - 1) // per_page
        }

    except Error as e:
        print(f"Query execution error in get_all_games_by_release_date: {e}")  # Debug
        return {"success": False, "error": f"Error query: {e}"}

def get_filter_options():
    """
    Lấy các option cho filter dropdown
    """
    try:
        conn = get_db_connection()
        if conn is None:
            print("Connection failed in get_filter_options")  # Debug
            return {"success": False, "error": "Can't connect database!"}

        cursor = conn.cursor(dictionary=True)
        
        # Lấy các giá trị unique cho từng filter
        filters = {}
        
        # Genre (từ bảng categories)
        cursor.execute("SELECT DISTINCT c.name FROM categories c JOIN game_category gc ON c.id = gc.category_id JOIN games g ON gc.game_id = g.id WHERE g.isDeleted = FALSE AND c.name IS NOT NULL AND c.name != ''")
        filters['genre'] = [row['name'] for row in cursor.fetchall()]
        
        # RAM (từ recommend_ram trong game_details)
        cursor.execute("SELECT DISTINCT gd.recommend_ram FROM games g LEFT JOIN game_details gd ON g.id = gd.game_id WHERE g.isDeleted = FALSE AND gd.recommend_ram IS NOT NULL AND gd.recommend_ram != ''")
        filters['ram'] = [row['recommend_ram'] for row in cursor.fetchall()]
        
        # Storage (từ recommend_storage trong game_details)
        cursor.execute("SELECT DISTINCT gd.recommend_storage FROM games g LEFT JOIN game_details gd ON g.id = gd.game_id WHERE g.isDeleted = FALSE AND gd.recommend_storage IS NOT NULL AND gd.recommend_storage != ''")
        filters['storage'] = [row['recommend_storage'] for row in cursor.fetchall()]
        
        # CPU (từ recommend_cpu trong game_details)
        cursor.execute("SELECT DISTINCT gd.recommend_cpu FROM games g LEFT JOIN game_details gd ON g.id = gd.game_id WHERE g.isDeleted = FALSE AND gd.recommend_cpu IS NOT NULL AND gd.recommend_cpu != ''")
        filters['cpu'] = [row['recommend_cpu'] for row in cursor.fetchall()]
        
        # GPU (từ recommend_gpu trong game_details)
        cursor.execute("SELECT DISTINCT gd.recommend_gpu FROM games g LEFT JOIN game_details gd ON g.id = gd.game_id WHERE g.isDeleted = FALSE AND gd.recommend_gpu IS NOT NULL AND gd.recommend_gpu != ''")
        filters['gpu'] = [row['recommend_gpu'] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()

        print(f"Filter options fetched: {filters}")  # Debug
        return {"success": True, "filters": filters}

    except Error as e:
        print(f"Error in get_filter_options: {e}")  # Debug
        return {"success": False, "error": f"Error query: {e}"}