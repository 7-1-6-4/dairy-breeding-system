from flask import Blueprint, request, jsonify
import uuid
from services.database import DatabaseService
#from services.predictor import PredictorService
from services.explainer import ExplainerService

# Create blueprint
recommendations_bp = Blueprint('recommendations', __name__)

# Initialize services
db = DatabaseService()
#predictor = PredictorService()
explainer = ExplainerService()

@recommendations_bp.route('/recommend', methods=['POST'])
def get_recommendations():
    """
    Get breed recommendations for a county
    
    Request body:
    {
        "county_id": 1,
        "current_breed": "B001" (optional)
    }
    """
    data = request.get_json()
    
    if not data or 'county_id' not in data:
        return jsonify({'error': 'county_id is required'}), 400
    
    county_id = data['county_id']
    current_breed = data.get('current_breed')
    
    # Generate session ID for tracking
    session_id = str(uuid.uuid4())
    
    # Get county information
    county = db.get_county_by_id(county_id)
    if not county:
        return jsonify({'error': 'County not found'}), 404
    
    # Get top recommendations from database
    recommendations = db.get_top_recommendations(county_id, limit=2)
    
    if not recommendations:
        return jsonify({'error': 'No recommendations found'}), 404
    
    # Enrich with breed details and explanations
    enriched = []
    for idx, rec in enumerate(recommendations, 1):
        breed_data = rec.get('breeds', {})
        
        # Get full breed details
        breed = db.get_breed_by_id(rec['breed_id'])
        
        # Generate explanation
        explanation = explainer.generate_explanation(breed, county, rec['suitability_score'])
        
        enriched.append({
            'rank': idx,
            'breed_id': rec['breed_id'],
            'breed_name': breed_data.get('breed_name', 'Unknown'),
            'breed_type': breed_data.get('breed_type', 'Unknown'),
            'suitability_score': rec['suitability_score'],
            'milk_score': rec['milk_score'],
            'health_score': rec['health_score'],
            'adaptation_score': rec['adaptation_score'],
            'heat_tolerance_score': breed.get('heat_tolerance_score', 5),
            'description': breed_data.get('description', ''),
            'explanation': explanation
        })
    
    # Calculate improvement if current breed provided
    improvement = None
    if current_breed and enriched:
        current_score = None
        for score in db.get_suitability_scores(county_id):
            if score['breed_id'] == current_breed:
                current_score = score['suitability_score']
                break
        
        if current_score:
            improvement = enriched[0]['suitability_score'] - current_score
    
    # Log the recommendation
    db.log_recommendation(
        session_id=session_id,
        county_id=county_id,
        user_breed_id=current_breed,
        rec1_id=enriched[0]['breed_id'] if enriched else None,
        rec2_id=enriched[1]['breed_id'] if len(enriched) > 1 else None,
        score1=enriched[0]['suitability_score'] if enriched else None,
        score2=enriched[1]['suitability_score'] if len(enriched) > 1 else None
    )
    
    # Generate comparison if two breeds
    comparison = None
    if len(enriched) >= 2:
        breed1 = db.get_breed_by_id(enriched[0]['breed_id'])
        breed2 = db.get_breed_by_id(enriched[1]['breed_id'])
        comparison = explainer.generate_comparison(breed1, breed2, county)
    
    response = {
        'success': True,
        'session_id': session_id,
        'county': {
            'id': county['county_id'],
            'name': county['county_name'],
            'region': county['region'],
            'altitude': county['altitude_m'],
            'avg_thi': county['avg_thi']
        },
        'recommendations': enriched,
        'improvement_potential': round(improvement, 2) if improvement is not None else None,
        'comparison': comparison
    }
    
    return jsonify(response)

@recommendations_bp.route('/predict', methods=['POST'])
def predict_custom():
    """Use ML model for custom prediction"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        score = predictor.predict_suitability(data)
        return jsonify({'predicted_suitability': round(score, 2)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400