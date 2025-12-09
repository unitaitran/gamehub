from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
import google.generativeai as genai
import re
import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-pro')

# FastAPI app
app = FastAPI()

class QueryRequest(BaseModel):
    prompt: str

# Thông tin DB
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "game_shop")
}

# Mô tả schema đầy đủ cho Gemini
schema_description = """
Bạn đang truy vấn một CSDL MySQL với các bảng sau:

1. Bảng `games`:
   - id (INT PRIMARY KEY)
   - title (VARCHAR) - tên game
   - description (TEXT) - mô tả game
   - price (DECIMAL) - giá tiền
   - image_url_vertical (VARCHAR) - URL ảnh dọc
   - release_date (DATE) - ngày phát hành
   - link_download (VARCHAR) - link tải
   - isDeleted (TINYINT) - trạng thái xóa
   - image_url_horizontal (VARCHAR) - URL ảnh ngang

2. Bảng `game_details`:
   - id (INT PRIMARY KEY)
   - game_id (INT) - ID tham chiếu đến games
   - win (TINYINT) - hỗ trợ Windows (0/1)
   - mac (TINYINT) - hỗ trợ Mac (0/1)
   - linux (TINYINT) - hỗ trợ Linux (0/1)
   - rating (DECIMAL) - đánh giá
   - positive_ratio (INT) - tỷ lệ đánh giá tích cực
   - user_reviews (INT) - số lượng review
   - price_original (DECIMAL) - giá gốc
   - steam_deck (TINYINT) - hỗ trợ Steam Deck (0/1)
   - recommend_cpu (VARCHAR) - CPU khuyến nghị
   - recommend_ram (VARCHAR) - RAM khuyến nghị
   - recommend_storage (VARCHAR) - dung lượng khuyến nghị
   - recommend_gpu (VARCHAR) - GPU khuyến nghị
   - isDeleted (TINYINT) - trạng thái xóa

3. Bảng `categories`:
   - id (INT PRIMARY KEY)
   - name (VARCHAR) - tên thể loại
   - isDeleted (TINYINT) - trạng thái xóa

4. Bảng `game_category` (bảng liên kết):
   - game_id (INT) - ID game
   - category_id (INT) - ID thể loại

Dựa vào yêu cầu người dùng về giá tiền, tên, thể loại hoặc cấu hình khuyến nghị, hãy sinh câu lệnh SQL phù hợp.
Nếu không cần truy vấn, chỉ trả về "NO_SQL".

Trả về kết quả dưới dạng JSON với key là `sql`. Ví dụ:
{
  "sql": "SELECT g.title, g.price, c.name as category FROM games g JOIN game_category gc ON g.id = gc.game_id JOIN categories c ON gc.category_id = c.id WHERE g.price < 10;"
}
Hoặc nếu không cần SQL, trả về:
{
  "sql": "NO_SQL"
}
"""

# Hàm trích xuất JSON từ markdown code block
def extract_json_from_markdown(text: str):
    """Trích xuất JSON từ markdown code block"""
    import re
    
    # Tìm pattern ```json ... ``` hoặc ``` ... ```
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    match = re.search(json_pattern, text, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # Nếu không tìm thấy markdown, thử parse trực tiếp
    return text.strip()

# Truy vấn MySQL
def run_sql_query(sql: str):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# Endpoint chính
@app.post("/chat")
async def chat(request: QueryRequest):
    user_prompt = request.prompt

    # Bước 1: yêu cầu Gemini tạo SQL nếu cần
    sql_prompt = f"""
Người dùng hỏi: "{user_prompt}"

{schema_description}

QUAN TRỌNG: Chỉ trả về JSON thuần túy, KHÔNG sử dụng markdown code block. Ví dụ:

{{
  "sql": "SELECT g.title, g.price FROM games g WHERE g.price < 10"
}}

Hoặc nếu không cần SQL:
{{
  "sql": "NO_SQL"
}}

Trả về JSON:
"""
    try:
        sql_response_obj = model.generate_content(sql_prompt)
        if sql_response_obj.text:
            raw_response = sql_response_obj.text.strip()
            # Trích xuất JSON từ markdown nếu cần
            sql_response = extract_json_from_markdown(raw_response)
        else:
            # Nếu không có text, thử lấy response khác
            sql_response = "{\"sql\": \"NO_SQL\"}"
        print("[GeminiAI] User prompt:", user_prompt)
        print("[GeminiAI] Raw Gemini response:", raw_response if 'raw_response' in locals() else "No response")
        print("[GeminiAI] Extracted SQL response:", sql_response)
    except Exception as e:
        print(f"Lỗi khi gọi Gemini API: {e}")
        sql_response = "{\"sql\": \"NO_SQL\"}"

    try:
        sql_json = json.loads(sql_response)
        sql_query = sql_json.get("sql", "NO_SQL")
        print("[GeminiAI] Final SQL query:", sql_query)
    except Exception as e:
        print(f"Lỗi parse JSON: {e}")
        print(f"SQL Response to parse: {sql_response}")
        return {"response": f"Gemini trả về kết quả không hợp lệ: {str(e)}", "raw": sql_response}

    # Bước 2: Nếu có SQL thì chạy, rồi đưa kết quả vào prompt trả lời
    if sql_query != "NO_SQL":
        try:
            results = run_sql_query(sql_query)
            print("SQL Results:", results)
        except Exception as e:
            return {"response": f"Lỗi khi chạy SQL: {str(e)}", "sql": sql_query}

        # Bước 3: Đưa kết quả vào prompt để Gemini trả lời cuối
        if results:
            # Giới hạn số lượng kết quả để tránh prompt quá dài
            limited_results = results[:10]  # Chỉ lấy 10 kết quả đầu
            result_str = "\n".join([json.dumps(row, ensure_ascii=False, default=str) for row in limited_results])
            
            final_prompt = f"""
Người dùng hỏi: "{user_prompt}"

Tôi đã tìm thấy {len(results)} kết quả trong database. Dưới đây là {len(limited_results)} kết quả đầu tiên:

{result_str}

Dựa vào thông tin trên, hãy trả lời cho người dùng bằng tiếng Việt một cách chi tiết và hữu ích. 
Nếu có nhiều kết quả, hãy tóm tắt và đưa ra gợi ý tốt nhất.
"""
        else:
            final_prompt = f"""
Người dùng hỏi: "{user_prompt}"

Không tìm thấy kết quả nào trong database với câu truy vấn: {sql_query}

Hãy trả lời cho người dùng bằng tiếng Việt rằng không tìm thấy thông tin phù hợp:
"""
        
        try:
            print(f"Final prompt length: {len(final_prompt)}")
            answer_obj = model.generate_content(final_prompt)
            if answer_obj.text:
                answer = answer_obj.text.strip()
                print(f"Generated answer: {answer[:100]}...")
            else:
                answer = "Xin lỗi, tôi không thể xử lý yêu cầu này. Vui lòng thử lại."
        except Exception as e:
            print(f"Lỗi khi tạo câu trả lời: {e}")
            # Tạo câu trả lời đơn giản dựa trên kết quả
            if results:
                game_names = [row.get('title', 'Unknown') for row in results[:5]]
                answer = f"Tôi đã tìm thấy {len(results)} games phù hợp với yêu cầu của bạn. Một số games tiêu biểu: {', '.join(game_names)}"
            else:
                answer = "Không tìm thấy games nào phù hợp với yêu cầu của bạn."
        
        return {"response": answer, "sql": sql_query, "results_count": len(results)}
    
    # Bước 4: Nếu không cần SQL → Gemini trả lời trực tiếp
    else:
        try:
            answer_obj = model.generate_content(user_prompt)
            if answer_obj.text:
                answer = answer_obj.text.strip()
            else:
                answer = "Xin lỗi, tôi không thể xử lý yêu cầu này. Vui lòng thử lại."
        except Exception as e:
            print(f"Lỗi khi tạo câu trả lời: {e}")
            answer = "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu của bạn."
        
        return {"response": answer, "sql": "NO_SQL"}

# Endpoint test
@app.get("/")
async def root():
    return {"message": "Game Shop AI API đang hoạt động"}

# Endpoint test database connection
@app.get("/test-db")
async def test_db():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total_games FROM games")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "success", "total_games": result[0]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Endpoint test Gemini API
@app.get("/test-gemini")
async def test_gemini():
    try:
        test_prompt = "Xin chào, đây là test"
        response_obj = model.generate_content(test_prompt)
        if response_obj.text:
            return {"status": "success", "response": response_obj.text}
        else:
            return {"status": "error", "message": "Gemini trả về response rỗng"}
    except Exception as e:
        logger.error(f"Lỗi Gemini API: {e}")
        return {"status": "error", "message": str(e)}

# Endpoint debug để test response generation
@app.post("/debug-response")
async def debug_response(request: QueryRequest):
    """Debug endpoint để test việc tạo response"""
    try:
        # Test với dữ liệu mẫu
        sample_data = [
            {"id": 1, "title": "Hitman 3", "price": 29.99, "category": "Stealth"},
            {"id": 2, "title": "Metal Gear Solid V", "price": 19.99, "category": "Stealth"}
        ]
        
        result_str = "\n".join([json.dumps(row, ensure_ascii=False, default=str) for row in sample_data])
        
        final_prompt = f"""
Người dùng hỏi: "{request.prompt}"

Tôi đã tìm thấy {len(sample_data)} kết quả trong database. Dưới đây là kết quả:

{result_str}

Dựa vào thông tin trên, hãy trả lời cho người dùng bằng tiếng Việt một cách chi tiết và hữu ích.
"""
        
        print(f"Debug prompt: {final_prompt}")
        answer_obj = model.generate_content(final_prompt)
        
        if answer_obj.text:
            answer = answer_obj.text.strip()
            return {"status": "success", "response": answer, "prompt_length": len(final_prompt)}
        else:
            return {"status": "error", "message": "Gemini trả về response rỗng"}
            
    except Exception as e:
        logger.error(f"Lỗi debug response: {e}")
        return {"status": "error", "message": str(e)}
