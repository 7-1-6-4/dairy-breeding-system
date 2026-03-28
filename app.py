from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import blueprints
from api.routes.recommendations import recommendations_bp
from api.routes.counties import counties_bp
from api.routes.breeds import breeds_bp

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Register blueprints
app.register_blueprint(recommendations_bp)
app.register_blueprint(counties_bp)
app.register_blueprint(breeds_bp)

@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        'name': 'AI Dairy Breeding Recommendation System API',
        'version': '1.0',
        'status': 'running',
        'endpoints': {
            'GET /': 'This help',
            'GET /counties': 'List all counties',
            'GET /counties/<id>': 'Get county details',
            'GET /counties/<id>/environment': 'Get county environmental data',
            'GET /breeds': 'List all breeds',
            'GET /breeds/<id>': 'Get breed details',
            'GET /breeds/type/<type>': 'Filter breeds by type',
            'POST /recommend': 'Get breed recommendations',
            'POST /predict': 'Custom ML prediction'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print("="*60)
    print("🚀 AI DAIRY BREEDING API")
    print("="*60)
    print(f"Starting server on port {port}...")
    print(f"Environment: {'Development' if debug else 'Production'}")
    print("="*60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)