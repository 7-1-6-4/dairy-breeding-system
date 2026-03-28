from flask import Blueprint, jsonify
from services.database import DatabaseService

counties_bp = Blueprint('counties', __name__)
db = DatabaseService()

@counties_bp.route('/counties', methods=['GET'])
def get_counties():
    """Get all counties for dropdown"""
    counties = db.get_all_counties()
    return jsonify(counties)

@counties_bp.route('/counties/<int:county_id>', methods=['GET'])
def get_county(county_id):
    """Get detailed county information"""
    county = db.get_county_by_id(county_id)
    if not county:
        return jsonify({'error': 'County not found'}), 404
    return jsonify(county)

@counties_bp.route('/counties/<int:county_id>/environment', methods=['GET'])
def get_county_environment(county_id):
    """Get environmental summary for a county"""
    county = db.get_county_by_id(county_id)
    if not county:
        return jsonify({'error': 'County not found'}), 404
    
    # Calculate stress level
    thi = county.get('avg_thi', 0)
    if thi < 68:
        stress = 'Comfortable'
    elif thi < 74:
        stress = 'Mild Stress'
    elif thi < 80:
        stress = 'Moderate Stress'
    else:
        stress = 'Severe Stress'
    
    return jsonify({
        'county_name': county['county_name'],
        'region': county['region'],
        'altitude': county['altitude_m'],
        'temperature': {
            'avg': county['avg_temp_c'],
            'min': county['min_temp_c'],
            'max': county['max_temp_c']
        },
        'humidity': county['avg_humidity_pct'],
        'rainfall': county['annual_rainfall_mm'],
        'thi': {
            'avg': county['avg_thi'],
            'min': county['min_thi'],
            'max': county['max_thi'],
            'stress_level': stress
        },
        'disease_index': county['disease_index']
    })