
from .auth import get_db_connection, execute_query, select_data, insert_data, update_data, delete_data
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional, Tuple

class CartBackend:
    def __init__(self):
        self.table_name = 'cart_items'
    
    def get_user_cart(self, user_id: int) -> List[Dict]:
        """
        Lấy tất cả items trong cart của user từ database
        """
        try:
            # Query với JOIN để lấy thông tin game và price
            query = """
                SELECT 
                    ci.id, ci.user_id, ci.game_id, 
                    g.title as game_title, g.price as game_price, 
                    g.description as game_description, 
                    COALESCE(g.image_url_vertical, 'https://via.placeholder.com/150') as game_image
                FROM cart_items ci 
                LEFT JOIN games g ON ci.game_id = g.id 
                WHERE ci.user_id = %s 
                ORDER BY ci.id DESC 
            """
            result = execute_query(query, (user_id,), fetch=True)
            # Convert Decimal to float for frontend compatibility
            if result:
                for item in result:
                    if 'game_price' in item and hasattr(item['game_price'], '__float__'):
                        item['game_price'] = float(item['game_price'])
                    if 'price' in item and hasattr(item['price'], '__float__'):
                        item['price'] = float(item['price'])
            return result if result else []
        except Exception as e:
            return []
    
    def add_to_cart(self, user_id: int, game_id: int, quantity: int = 1) -> bool:
        """
        Thêm game vào cart
        """
        try:
            # Kiểm tra xem game đã có trong cart chưa
            existing_item = self.get_cart_item(user_id, game_id)
            
            if existing_item:
                # Nếu đã có, thêm một item mới (vì không có quantity column)
                cart_data = {
                    'user_id': user_id,
                    'game_id': game_id
                }
                result = insert_data('cart_items', cart_data)
                return result is not None
            else:
                # Nếu chưa có, thêm mới
                cart_data = {
                    'user_id': user_id,
                    'game_id': game_id
                }
                result = insert_data('cart_items', cart_data)
                return result is not None
                
        except Exception as e:
            print(f"Error adding to cart: {e}")
            return False
    
    def remove_from_cart(self, cart_item_id: int) -> bool:
        """
        Xóa item khỏi cart
        """
        try:
            result = delete_data('cart_items', 'id = %s', (cart_item_id,))
            return result is not None
        except Exception as e:
            print(f"Error removing from cart: {e}")
            return False
    
    def update_cart_quantity(self, cart_item_id: int, quantity: int) -> bool:
        """
        Cập nhật quantity của item trong cart
        Vì không có quantity column, sẽ xóa item cũ và thêm item mới
        """
        try:
            # Lấy thông tin item hiện tại
            item = self.get_cart_item_by_id(cart_item_id)
            if not item:
                return False
            
            # Xóa item cũ
            self.remove_from_cart(cart_item_id)
            
            # Thêm item mới với số lượng mong muốn
            for _ in range(quantity):
                cart_data = {
                    'user_id': item['user_id'],
                    'game_id': item['game_id']
                }
                insert_data('cart_items', cart_data)
            
            return True
        except Exception as e:
            print(f"Error updating cart quantity: {e}")
            return False
    
    def get_cart_item_by_id(self, cart_item_id: int) -> Optional[Dict]:
        """
        Lấy thông tin item theo cart_item_id
        """
        try:
            query = """
                SELECT ci.*, g.title as game_title, g.price as game_price
                FROM cart_items ci
                LEFT JOIN games g ON ci.game_id = g.id
                WHERE ci.id = %s
            """
            result = execute_query(query, (cart_item_id,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting cart item by id: {e}")
            return None
    
    def get_cart_item(self, user_id: int, game_id: int) -> Optional[Dict]:
        """
        Lấy thông tin item cụ thể trong cart
        """
        try:
            query = """
                SELECT ci.*, g.title as game_title, g.price as game_price
                FROM cart_items ci
                LEFT JOIN games g ON ci.game_id = g.id
                WHERE ci.user_id = %s AND ci.game_id = %s
            """
            result = execute_query(query, (user_id, game_id), fetch=True)
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting cart item: {e}")
            return None
    
    def get_cart_total(self, user_id: int) -> float:
        """
        Tính tổng giá trị cart
        """
        try:
            cart_items = self.get_user_cart(user_id)
            total = 0.0
            for item in cart_items:
                price = float(item.get('game_price', 0))
                total += price
            return total
        except Exception as e:
            print(f"Error calculating cart total: {e}")
            return 0.0
    
    def clear_user_cart(self, user_id: int) -> bool:
        """
        Xóa tất cả items trong cart của user
        """
        try:
            result = delete_data('cart_items', 'user_id = %s', (user_id,))
            return result is not None
        except Exception as e:
            print(f"Error clearing user cart: {e}")
            return False
    
    def get_cart_count(self, user_id: int) -> int:
        """
        Đếm số lượng items trong cart
        """
        try:
            cart_items = self.get_user_cart(user_id)
            return len(cart_items)
        except Exception as e:
            print(f"Error getting cart count: {e}")
            return 0
    
    def checkout_cart(self, user_id: int) -> Tuple[bool, List[Dict]]:
        """
        Checkout cart - chuyển items từ cart sang purchase_history
        """
        try:
            cart_items = self.get_user_cart(user_id)
            if not cart_items:
                return False, []
            
            # Thêm vào purchase_history
            for item in cart_items:
                purchase_data = {
                    'user_id': user_id,
                    'game_id': item['game_id'],
                    'quantity': item.get('quantity', 1),
                    'price': item.get('game_price', 0)
                }
                insert_data('purchase_history', purchase_data)
            
            # Xóa cart
            self.clear_user_cart(user_id)
            
            return True, cart_items
            
        except Exception as e:
            print(f"Error during checkout: {e}")
            return False, []
    
    def get_cart_summary(self, user_id: int) -> Dict:
        """
        Lấy summary của cart (count, total)
        """
        try:
            count = self.get_cart_count(user_id)
            total = self.get_cart_total(user_id)
            return {
                'count': count,
                'total': total
            }
        except Exception as e:
            print(f"Error getting cart summary: {e}")
            return {'count': 0, 'total': 0.0}

# Tạo instance mặc định
cart_backend = CartBackend()

# Utility functions để import trực tiếp
def get_user_cart(user_id: int) -> List[Dict]:
    return cart_backend.get_user_cart(user_id)

def add_to_cart(user_id: int, game_id: int, quantity: int = 1) -> bool:
    return cart_backend.add_to_cart(user_id, game_id, quantity)

def remove_from_cart(cart_item_id: int) -> bool:
    return cart_backend.remove_from_cart(cart_item_id)

def update_cart_quantity(cart_item_id: int, quantity: int) -> bool:
    return cart_backend.update_cart_quantity(cart_item_id, quantity)

def get_cart_total(user_id: int) -> float:
    return cart_backend.get_cart_total(user_id)

def get_cart_count(user_id: int) -> int:
    return cart_backend.get_cart_count(user_id)

def checkout_selected_cart_items(user_id: int, cart_item_ids: list) -> bool:
    """
    Chuyển các game được chọn từ cart sang user_games (lịch sử mua), trừ balance từ coin của user
    """
    try:
        if not cart_item_ids:
            return False
        
        # 1. Lấy thông tin games và tính tổng tiền
        format_strings = ','.join(['%s'] * len(cart_item_ids))
        query = f"""
            SELECT ci.game_id, g.title, g.price 
            FROM cart_items ci 
            LEFT JOIN games g ON ci.game_id = g.id 
            WHERE ci.id IN ({format_strings}) AND ci.user_id = %s
        """
        params = cart_item_ids + [user_id]
        games = execute_query(query, params, fetch=True)
        
        if not games:
            return False
        
        # 2. Tính tổng tiền
        total_cost = sum(float(game['price']) for game in games)
        
        # 3. Kiểm tra balance của user
        user_query = "SELECT coin FROM users WHERE id = %s"
        user_data = execute_query(user_query, (user_id,), fetch=True)
        if not user_data:
            return False
        
        current_balance = float(user_data[0]['coin']) if user_data[0]['coin'] else 0
        
        # Cho phép mua game free (total_cost = 0)
        if total_cost > 0 and current_balance < total_cost:
            return False
        
        # 4. Trừ tiền từ balance (chỉ khi có chi phí)
        if total_cost > 0:
            new_balance = current_balance - total_cost
            update_balance_query = "UPDATE users SET coin = %s WHERE id = %s"
            balance_result = execute_query(update_balance_query, (new_balance, user_id))
        else:
            new_balance = current_balance
        
        # 5. Thêm games vào user_games
        for game in games:
            # Kiểm tra đã mua chưa
            check_query = "SELECT * FROM user_games WHERE user_id = %s AND game_id = %s"
            exists = execute_query(check_query, (user_id, game['game_id']), fetch=True)
            
            if not exists:
                result = insert_data('user_games', {'user_id': user_id, 'game_id': game['game_id']})
            else:
                pass # Game already in user_games
        
        # 6. Xóa games khỏi cart
        del_query = f"DELETE FROM cart_items WHERE id IN ({format_strings}) AND user_id = %s"
        del_result = execute_query(del_query, params)
        
        return True
        
    except Exception as e:
        return False

def checkout_selected(user_id: int, cart_item_ids: list) -> bool:
    return checkout_selected_cart_items(user_id, cart_item_ids) 