import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseService:
    """Service to handle all Supabase database interactions"""
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env")
        
        self.supabase = create_client(url, key)
        print("✅ Database service connected")
    
    # ========== COUNTY METHODS ==========
    def get_all_counties(self):
        """Get all counties for dropdown"""
        result = self.supabase.table('counties')\
            .select('county_id, county_name, region')\
            .order('county_name')\
            .execute()
        return result.data
    
    def get_county_by_id(self, county_id):
        """Get detailed county information"""
        result = self.supabase.table('counties')\
            .select('*')\
            .eq('county_id', county_id)\
            .execute()
        return result.data[0] if result.data else None
    
    # ========== BREED METHODS ==========
    def get_all_breeds(self):
        """Get all breeds for dropdown"""
        result = self.supabase.table('breeds')\
            .select('breed_id, breed_name, breed_type')\
            .order('breed_name')\
            .execute()
        return result.data
    
    def get_breed_by_id(self, breed_id):
        """Get detailed breed information"""
        result = self.supabase.table('breeds')\
            .select('*')\
            .eq('breed_id', breed_id)\
            .execute()
        return result.data[0] if result.data else None
    
    # ========== SUITABILITY SCORES ==========
    def get_suitability_scores(self, county_id):
        """Get all suitability scores for a county"""
        result = self.supabase.table('suitability_scores')\
            .select('*')\
            .eq('county_id', county_id)\
            .order('suitability_score', desc=True)\
            .execute()
        return result.data
    
    def get_top_recommendations(self, county_id, limit=2):
        """Get top N breed recommendations for a county"""
        result = self.supabase.table('suitability_scores')\
            .select('''
                breed_id,
                suitability_score,
                milk_score,
                health_score,
                adaptation_score,
                breeds!inner(breed_name, breed_type, description)
            ''')\
            .eq('county_id', county_id)\
            .order('suitability_score', desc=True)\
            .limit(limit)\
            .execute()
        return result.data
    
    # ========== RECOMMENDATIONS LOG ==========
    def log_recommendation(self, session_id, county_id, user_breed_id, rec1_id, rec2_id, score1, score2):
        """Log a recommendation for analytics"""
        data = {
            'session_id': session_id,
            'county_id': county_id,
            'user_breed_id': user_breed_id,
            'recommended_breed1_id': rec1_id,
            'recommended_breed2_id': rec2_id,
            'score1': score1,
            'score2': score2
        }
        result = self.supabase.table('recommendations_log')\
            .insert(data)\
            .execute()
        return result.data