# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from database.types.postgresql_news_database import PostgresqlNewsDatabase
from datetime import datetime
from common.new_class import News

app = Flask(__name__)
CORS(app)
db_manager = PostgresqlNewsDatabase.from_url(db_url='postgresql://db_admin:PbZNxUyKRnScK8ckTUkxmUXjoDaf2a01@dpg-cult6kqj1k6c73803jeg-a.oregon-postgres.render.com/newsdbrender')

@app.route('/news', methods=['GET'])
def get_news():
    """Get all news articles"""
    try:
        news_items = db_manager.get_all()
        news_items_dicts = [news_item.to_dict() for news_item in news_items]
        return jsonify(news_items_dicts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/news', methods=['POST'])
def add_news():
    """Add new news article"""
    data = request.get_json()
    
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Missing required fields (title and content)'}), 400
    
    news_data = News.from_dict(data)
    print("news data converted : ",news_data)
    try:    
        result = db_manager.save_new(news_data)
        return jsonify({
            'news' : news_data.to_dict(),
            'message': 'News article created successfully',
        }), 201
    except Exception as e:
        if 'unique' in str(e).lower():
            return jsonify({'error': 'Article with this title already exists'}), 409
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)