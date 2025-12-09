from .auth import execute_query
from typing import List, Dict

def get_user_purchase_history(user_id: int) -> List[Dict]:
    """
    Lấy danh sách các game đã mua của user từ bảng user_games, kèm thông tin game.
    """
    try:
        query = """
            SELECT
                ug.user_id,
                ug.game_id,
                g.title as game_title,
                g.price as game_price,
                g.description as game_description,
                COALESCE(g.image_url_vertical, 'https://via.placeholder.com/150') as game_image,
                1 as `order`
            FROM user_games ug
            LEFT JOIN games g ON ug.game_id = g.id
            WHERE ug.user_id = %s
            ORDER BY ug.game_id DESC
        """
        result = execute_query(query, (user_id,), fetch=True)
        # Kiểm tra chi tiết từng record
        # Kiểm tra xem có game nào bị thiếu thông tin không
        missing_info = []
        for record in result:
            if not record.get('game_title') or not record.get('game_price'):
                missing_info.append(record.get('game_id'))
        # Thử query riêng để lấy thông tin game nếu thiếu
        for game_id in missing_info:
            game_query = "SELECT title, price, description, image_url_vertical FROM games WHERE id = %s"
            game_info = execute_query(game_query, (game_id,), fetch=True)
        return result if result else []
    except Exception as e:
        return []

# Hàm tiện ích để import trực tiếp

def get_history(user_id: int) -> List[Dict]:
    return get_user_purchase_history(user_id) 