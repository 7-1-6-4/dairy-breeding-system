from flask import Blueprint, jsonify
from services.database import DatabaseService

breeds_bp = Blueprint('breeds', __name__)
db = DatabaseService()

@breeds_bp.route('/breeds', methods=['GET'])
def get_breeds():
    """Get all breeds for dropdown"""
    breeds = db.get_all_breeds()
    return jsonify(breeds)

@breeds_bp.route('/breeds/<breed_id>', methods=['GET'])
def get_breed(breed_id):
    """Get detailed breed information"""
    breed = db.get_breed_by_id(breed_id)
    if not breed:
        return jsonify({'error': 'Breed not found'}), 404
    return jsonify(breed)

@breeds_bp.route('/breeds/type/<breed_type>', methods=['GET'])
def get_breeds_by_type(breed_type):
    """Get breeds filtered by type"""
    supabase = db.supabase
    result = supabase.table('breeds')\
        .select('breed_id, breed_name, breed_type')\
        .eq('breed_type', breed_type)\
        .order('breed_name')\
        .execute()
    return jsonify(result.data)