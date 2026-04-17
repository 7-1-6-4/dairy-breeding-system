from flask import Blueprint, request, jsonify
import uuid
from services.database import DatabaseService
from services.explainer import ExplainerService

# Create blueprint
recommendations_bp = Blueprint('recommendations', __name__)

# Initialize services
db = DatabaseService()
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
    
    # Get all suitability scores for this county
    all_scores = db.get_suitability_scores(county_id)
    
    # Get current breed info if provided
    current_breed_info = None
    has_current_breed = False
    if current_breed and current_breed != "":
        current_breed_info = db.get_breed_by_id(current_breed)
        has_current_breed = True
    
    # ========== BREED-AWARE RECOMMENDATION LOGIC ==========
    recommendations = []
    
    if not has_current_breed:
        # SCENARIO 1: Farmer has no cow
        # Recommend top pure breed and top crossbreed
        pure_breeds = [s for s in all_scores if s['breed_id'] in ['B001', 'B002', 'B003', 'B004', 'B005']]
        cross_breeds = [s for s in all_scores if s['breed_id'] in ['B006', 'B007', 'B008', 'B009', 'B010']]
        
        # Sort by suitability score
        pure_breeds.sort(key=lambda x: x['suitability_score'], reverse=True)
        cross_breeds.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        # Take top pure breed and top crossbreed
        if pure_breeds:
            recommendations.append(pure_breeds[0])
        if cross_breeds and len(recommendations) < 2:
            recommendations.append(cross_breeds[0])
        
        # If we don't have 2 yet, fill with more
        if len(recommendations) < 2:
            for score in all_scores:
                if score not in recommendations:
                    recommendations.append(score)
                    if len(recommendations) >= 2:
                        break
        
    else:
        # SCENARIO 2: Farmer has a cow - recommend crossbreeds
        current_type = current_breed_info.get('breed_type', '')
        current_name = current_breed_info.get('breed_name', '')
        
        # Crossbreed mapping based on current breed
        cross_mapping = {
            'B001': ['B006', 'B009'],  # Friesian → Friesian × Sahiwal, Friesian × Boran
            'B002': ['B007', 'B010'],  # Ayrshire → Ayrshire × Sahiwal, Ayrshire × Boran
            'B003': ['B008', 'B006'],  # Jersey → Jersey × Sahiwal, Friesian × Sahiwal
            'B004': ['B006', 'B008'],  # Sahiwal → Friesian × Sahiwal, Jersey × Sahiwal
            'B005': ['B009', 'B010'],  # Boran → Friesian × Boran, Ayrshire × Boran
            'B006': ['B006', 'B001'],  # Friesian × Sahiwal → continue or upgrade
            'B007': ['B007', 'B002'],  # Ayrshire × Sahiwal → continue or upgrade
            'B008': ['B008', 'B003'],  # Jersey × Sahiwal → continue or upgrade
            'B009': ['B009', 'B001'],  # Friesian × Boran → continue or upgrade
            'B010': ['B010', 'B002'],  # Ayrshire × Boran → continue or upgrade
        }
        
        # Get recommended crossbreeds
        target_ids = cross_mapping.get(current_breed, ['B006', 'B007'])
        
        for target_id in target_ids:
            for score in all_scores:
                if score['breed_id'] == target_id and score not in recommendations:
                    recommendations.append(score)
                    break
        
        # If we don't have 2 yet, add top crossbreed
        if len(recommendations) < 2:
            cross_breeds = [s for s in all_scores if s['breed_id'] in ['B006', 'B007', 'B008', 'B009', 'B010']]
            cross_breeds.sort(key=lambda x: x['suitability_score'], reverse=True)
            for score in cross_breeds:
                if score not in recommendations:
                    recommendations.append(score)
                    if len(recommendations) >= 2:
                        break
        
        # If still not enough, add top pure breed
        if len(recommendations) < 2:
            pure_breeds = [s for s in all_scores if s['breed_id'] in ['B001', 'B002', 'B003', 'B004', 'B005']]
            pure_breeds.sort(key=lambda x: x['suitability_score'], reverse=True)
            for score in pure_breeds:
                if score not in recommendations:
                    recommendations.append(score)
                    if len(recommendations) >= 2:
                        break
    
    # Limit to 2 recommendations
    recommendations = recommendations[:2]
    
    # Enrich with breed details and explanations
    enriched = []
    for idx, rec in enumerate(recommendations, 1):
        breed = db.get_breed_by_id(rec['breed_id'])
        if not breed:
            continue
        
        # Generate explanation with context about current breed
        explanation = explainer.generate_explanation(
            breed, county, rec['suitability_score'], 
            has_current_breed=has_current_breed, 
            current_breed_info=current_breed_info
        )
        
        enriched.append({
            'rank': idx,
            'breed_id': rec['breed_id'],
            'breed_name': breed.get('breed_name', 'Unknown'),
            'breed_type': breed.get('breed_type', 'Unknown'),
            'suitability_score': rec['suitability_score'],
            'milk_score': rec.get('milk_score', 0),
            'health_score': rec.get('health_score', 0),
            'adaptation_score': rec.get('adaptation_score', 0),
            'heat_tolerance_score': breed.get('heat_tolerance_score', 5),
            'disease_resistance_score': breed.get('disease_resistance_score', 5),
            'feed_efficiency_score': breed.get('feed_efficiency_score', 5),
            'description': breed.get('description', ''),
            'explanation': explanation
        })
    
    # Calculate improvement if current breed provided
    improvement = None
    if has_current_breed and enriched:
        current_score = None
        for score in all_scores:
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
        if breed1 and breed2:
            comparison = explainer.generate_comparison(breed1, breed2, county)
    
    response = {
        'success': True,
        'session_id': session_id,
        'county': {
            'id': county['county_id'],
            'name': county['county_name'],
            'region': county['region'],
            'altitude': county['altitude_m'],
            'avg_thi': county['avg_thi'],
            'disease_index': county['disease_index']
        },
        'recommendations': enriched,
        'improvement_potential': round(improvement, 2) if improvement is not None else None,
        'comparison': comparison,
        'has_current_breed': has_current_breed
    }
    
    return jsonify(response)

@recommendations_bp.route('/predict', methods=['POST'])
def predict_custom():
    """Use ML model for custom prediction"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    return jsonify({'message': 'ML prediction endpoint - model not loaded on Railway'}), 501