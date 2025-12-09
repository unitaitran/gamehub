import pandas as pd
import pickle
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings

# Suppress InconsistentVersionWarning
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Định nghĩa hàm tokenizer thay cho lambda (giống như trong training)
def custom_tokenizer(x):
    return x.split(',')

# Hàm lấy dữ liệu từ MySQL
def fetch_data_from_db():
    """Lấy dữ liệu từ database cho recommendation system"""
    try:
        from .auth import get_db_connection
        connection = get_db_connection()
        if not connection:
            return None, None
        
        cursor = connection.cursor(dictionary=True)
        
        # Lấy dữ liệu từ bảng user_games
        query_train = "SELECT user_id, game_id FROM user_games"
        cursor.execute(query_train)
        train_data = cursor.fetchall()
        cursor.close()
        
        # Tạo cursor mới cho query thứ 2
        cursor = connection.cursor(dictionary=True)
        
        # Lấy dữ liệu từ bảng games, join với game_category và categories để lấy categories, và game_details cho rating
        query_games = """
            SELECT g.id, g.title, GROUP_CONCAT(ca.name SEPARATOR ',') AS categories, gd.rating
            FROM games g
            LEFT JOIN game_category gc ON g.id = gc.game_id
            LEFT JOIN categories ca ON gc.category_id = ca.id
            LEFT JOIN game_details gd ON g.id = gd.game_id
            GROUP BY g.id, g.title, gd.rating
        """
        cursor.execute(query_games)
        games_data = cursor.fetchall()
        cursor.close()
        
        train_df = pd.DataFrame(train_data)
        games_df = pd.DataFrame(games_data)
        
        return train_df, games_df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None
    finally:
        if connection:
            connection.close()

# Khởi tạo dữ liệu mẫu cho recommendation (fallback)
def initialize_recommendation_data():
    """Khởi tạo dữ liệu mẫu cho recommendation system"""
    sample_games = pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'title': [
            'Assassin\'s Creed Mirage', 'Cyberpunk 2077', 'Red Dead Redemption 2',
            'Grand Theft Auto V', 'ELDEN RING', 'Rainbow Six Siege',
            'Assassin\'s Creed Odyssey', 'Assassin\'s Creed Origins',
            'Far Cry 5', 'Fallout 4'
        ],
        'categories': [
            'action,adventure', 'rpg,action', 'action,adventure',
            'action,adventure', 'rpg,action', 'fps,action',
            'action,adventure', 'action,adventure',
            'fps,action', 'rpg,action'
        ],
        'rating': [4.5, 4.0, 4.8, 4.2, 4.7, 4.1, 4.3, 4.4, 4.0, 4.6]
    })
    
    sample_train = pd.DataFrame({
        'user_id': [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4],
        'game_id': [1, 3, 5, 2, 4, 6, 1, 7, 9, 2, 8, 10]
    })
    
    return sample_train, sample_games

# Load mô hình từ file .pkl với xử lý lỗi tốt hơn
def load_trained_models():
    """Load trained models từ file .pkl với xử lý lỗi"""
    try:
        import os
        # Lấy đường dẫn tuyệt đối của file hiện tại
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Đi lên 1 cấp để đến thư mục src, rồi vào model
        model_path = os.path.join(current_dir, '..', 'model', 'trained_models.pkl')
        
        if not os.path.exists(model_path):
            print(f"Model file not found at: {model_path}")
            return None, None
            
        # Thử load với các cách khác nhau
        try:
            # Cách 1: Load với custom unpickler ngay từ đầu để tránh lỗi
            class CustomUnpickler(pickle.Unpickler):
                def find_class(self, module, name):
                    # Luôn trả về custom_tokenizer từ recommendation.py nếu tìm thấy
                    if name == 'custom_tokenizer':
                        return custom_tokenizer
                    # Xử lý trường hợp module là 'src.app' hoặc bất kỳ module nào khác
                    if module in ['src.app', '__main__', 'app'] and name == 'custom_tokenizer':
                        return custom_tokenizer
                    return super().find_class(module, name)
            
            with open(model_path, 'rb') as f:
                unpickler = CustomUnpickler(f)
                trained_models = unpickler.load()
                tfidf_df = trained_models.get('tfidf_df')
                item_sim_df = trained_models.get('item_sim_df')
                print("Loaded trained models successfully")
                return tfidf_df, item_sim_df
        except Exception as e1:
            print(f"First attempt failed: {e1}")
            
            # Cách 2: Load với custom unpickler để bỏ qua custom_tokenizer
            try:
                import pickle5 as pickle_alt
                with open(model_path, 'rb') as f:
                    trained_models = pickle_alt.load(f)
                    tfidf_df = trained_models.get('tfidf_df')
                    item_sim_df = trained_models.get('item_sim_df')
                    print("Loaded trained models with pickle5")
                    return tfidf_df, item_sim_df
            except:
                pass
                
            # Cách 3: Load với dill
            try:
                import dill
                with open(model_path, 'rb') as f:
                    trained_models = dill.load(f)
                    tfidf_df = trained_models.get('tfidf_df')
                    item_sim_df = trained_models.get('item_sim_df')
                    print("Loaded trained models with dill")
                    return tfidf_df, item_sim_df
            except:
                pass
                

                
            print("All loading methods failed, using fallback data")
            return None, None
            
    except Exception as e:
        print(f"Error loading trained models: {e}")
        return None, None

# Khởi tạo hệ thống recommendation
print("Initializing recommendation system...")

# Thử load trained models
tfidf_df, item_sim_df = load_trained_models()

if tfidf_df is None or item_sim_df is None:
    print("Using fallback data...")
    # Fallback: tạo dữ liệu mẫu nếu không load được
    train_df, games_df = initialize_recommendation_data()
    games_df['categories'] = games_df['categories'].apply(lambda x: str(x).lower().strip() if pd.notna(x) else '')
    scaler = MinMaxScaler()
    games_df['rating'] = scaler.fit_transform(games_df[['rating']])
    
    tfidf = TfidfVectorizer(tokenizer=custom_tokenizer, token_pattern=None)
    tfidf_matrix = tfidf.fit_transform(games_df['categories'])
    tfidf_df = pd.DataFrame.sparse.from_spmatrix(tfidf_matrix, columns=tfidf.get_feature_names_out(), index=games_df['id'])
    tfidf_df = pd.concat([tfidf_df, games_df.set_index('id')[['rating']]], axis=1)
    
    item_sim_matrix = cosine_similarity(tfidf_df)
    item_sim_df = pd.DataFrame(item_sim_matrix, index=games_df['id'], columns=games_df['id'])

print("Recommendation system initialized successfully")

# Hàm để lấy tfidf_df và item_sim_df
def get_trained_models():
    return tfidf_df, item_sim_df

# Hàm lấy thông tin chi tiết game từ database
def get_game_details_by_ids(game_ids):
    """Lấy thông tin chi tiết game từ database dựa trên list game_ids"""
    try:
        from .auth import get_db_connection
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        # Tạo placeholders cho IN clause
        placeholders = ','.join(['%s'] * len(game_ids))
        
        # Query để lấy thông tin chi tiết game bao gồm categories
        query = f"""
            SELECT 
                g.id,
                g.title,
                g.price,
                g.image_url_vertical,
                gd.price_original,
                gd.rating,
                GROUP_CONCAT(ca.name SEPARATOR ', ') AS categories
            FROM games g
            LEFT JOIN game_details gd ON g.id = gd.game_id
            LEFT JOIN game_category gc ON g.id = gc.game_id
            LEFT JOIN categories ca ON gc.category_id = ca.id
            WHERE g.id IN ({placeholders})
            GROUP BY g.id, g.title, g.price, g.image_url_vertical, gd.price_original, gd.rating
        """
        
        cursor.execute(query, game_ids)
        games_data = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Tính discount percentage
        for game in games_data:
            if game['price_original'] and game['price_original'] > game['price']:
                discount = ((game['price_original'] - game['price']) / game['price_original']) * 100
                game['discount_percentage'] = round(discount)
            else:
                game['discount_percentage'] = 0
        
        return games_data
        
    except Exception as e:
        print(f"Error fetching game details: {e}")
        return []

# Định nghĩa các hàm khuyến nghị
def get_content_based(user_id, train_df, tfidf_df, games_df, k=10):
    # Kiểm tra xem user_id có trong train_df không
    user_data = train_df[train_df['user_id'] == user_id]
    if user_data.empty:
        # Nếu user không có dữ liệu mua hàng, tạo dữ liệu mẫu cho user này
        # Sử dụng user_id làm seed để đảm bảo cùng user luôn nhận cùng recommendations
        import random
        random.seed(user_id)  # Set seed dựa trên user_id
        sample_size = min(3, len(games_df))  # Lấy 3 games hoặc ít hơn nếu không đủ
        if sample_size > 0:
            sample_games = games_df.sample(n=sample_size, random_state=user_id)
            bought_ids = sample_games['id'].tolist()
        else:
            # Nếu không có games nào, trả về top games
            return games_df.head(k)[['id', 'title']].assign(score=0.5)
    else:
        bought_ids = user_data['game_id'].tolist()
    
    if not bought_ids:
        return pd.DataFrame(columns=['id', 'title', 'score'])
    
    # Lọc ra các ID có trong tfidf_df
    valid_bought_ids = [gid for gid in bought_ids if gid in tfidf_df.index]
    if not valid_bought_ids:
        # Nếu không có valid bought_ids, trả về top games từ games_df
        return games_df.head(k)[['id', 'title']].assign(score=0.5)
    
    mean_vector = tfidf_df.loc[valid_bought_ids].mean(axis=0).to_numpy().reshape(1, -1)
    sim_scores = cosine_similarity(mean_vector, tfidf_df)[0]
    scores_df = pd.DataFrame({'id': tfidf_df.index, 'score': sim_scores})
    scores_df = scores_df[~scores_df['id'].isin(valid_bought_ids)].sort_values(by='score', ascending=False)
    
    # Chỉ lấy các games có trong games_df (MySQL hiện tại)
    available_games = set(games_df['id'].tolist())
    scores_df = scores_df[scores_df['id'].isin(available_games)].head(k)
    
    # Chỉ trả về id và score, không cần merge với games_df
    return scores_df[['id', 'score']]

def get_item_based_cf(user_id, train_df, item_sim_df, games_df, k=10):
    # Kiểm tra xem user_id có trong train_df không
    user_data = train_df[train_df['user_id'] == user_id]
    if user_data.empty:
        # Nếu user không có dữ liệu mua hàng, tạo dữ liệu mẫu cho user này
        # Sử dụng user_id làm seed để đảm bảo cùng user luôn nhận cùng recommendations
        import random
        random.seed(user_id)  # Set seed dựa trên user_id
        sample_size = min(3, len(games_df))  # Lấy 3 games hoặc ít hơn nếu không đủ
        if sample_size > 0:
            sample_games = games_df.sample(n=sample_size, random_state=user_id)
            bought_games = sample_games['id'].tolist()
        else:
            # Nếu không có games nào, trả về top games
            return games_df.head(k)[['id']].assign(score=0.5)
    else:
        bought_games = user_data['game_id'].tolist()
    
    bought_games = [g for g in bought_games if g in item_sim_df.index]
    if not bought_games:
        # Nếu không có valid bought_games, trả về top games từ games_df
        return games_df.head(k)[['id']].assign(score=0.5)
    
    sim_scores = item_sim_df[bought_games].mean(axis=1)
    sim_scores = sim_scores.drop(index=bought_games)
    scores_df = sim_scores.sort_values(ascending=False).reset_index()
    scores_df.columns = ['id', 'score']
    
    # Chỉ lấy các games có trong games_df (MySQL hiện tại)
    available_games = set(games_df['id'].tolist())
    scores_df = scores_df[scores_df['id'].isin(available_games)].head(k)
    
    # Chỉ trả về id và score, không cần merge với games_df
    return scores_df[['id', 'score']]

def get_hybrid(user_id, train_df, tfidf_df, item_sim_df, games_df, alpha=0.6, k=10):
    cb_scores = get_content_based(user_id, train_df, tfidf_df, games_df, k*2)
    cf_scores = get_item_based_cf(user_id, train_df, item_sim_df, games_df, k*2)
    hybrid_df = pd.merge(cb_scores[['id', 'score']], cf_scores[['id', 'score']], on='id', how='outer', suffixes=('_cb', '_cf')).fillna(0)
    hybrid_df['score'] = hybrid_df['score_cb'] * alpha + hybrid_df['score_cf'] * (1-alpha)
    hybrid_df = hybrid_df.sort_values(by='score', ascending=False).head(k)
    return hybrid_df[['id', 'score']]