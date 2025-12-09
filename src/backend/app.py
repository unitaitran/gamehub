from flask import Flask, request, jsonify
from flask_cors import CORS
from .home_page import search_games_by_title
from .allgame_be import get_all_games_by_release_date, get_filter_options

app = Flask(__name__)
CORS(app)

@app.route("/api/search", methods=["GET"])
def search_games():
    keyword = request.args.get("q", "")
    print(f"API /api/search called with keyword={keyword}")  # Debug
    result = search_games_by_title(keyword)
    print(f"API /api/search result: {result}")  # Debug
    return jsonify(result)

@app.route("/api/allgames", methods=["GET"])
def get_all_games():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 12))
    
    # Lấy filters từ query parameters
    filters = {}
    filter_fields = ['genre', 'ram', 'storage', 'cpu', 'gpu']
    for field in filter_fields:
        value = request.args.get(field)
        if value:
            filters[field] = value
    
    search = request.args.get("search")  # Lấy tham số search
    print(f"API /api/allgames called with page={page}, per_page={per_page}, filters={filters}, search={search}")  # Debug
    
    result = get_all_games_by_release_date(page, per_page, filters, search)
    print(f"API /api/allgames result: {result}")  # Debug
    return jsonify(result)

@app.route("/api/filter-options", methods=["GET"])
def get_filter_options_api():
    result = get_filter_options()
    print(f"API /api/filter-options result: {result}")  # Debug
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)