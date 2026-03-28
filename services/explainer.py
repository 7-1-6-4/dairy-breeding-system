class ExplainerService:
    """Generate human-readable explanations for recommendations"""
    
    def __init__(self):
     self.reason_templates = {
        'heat': "🌡️ <strong>Heat tolerance</strong>: Thrives in THI ranges of {thi_range}",
        'disease': "🛡️ <strong>Disease resistance</strong>: Strong resistance to {diseases}",
        'milk': "🥛 <strong>Milk production</strong>: Expected yield {yield_range} L/day",
        'feed': "🌿 <strong>Feed efficiency</strong>: Excellent conversion of {feed_type}",
        'crossbreed': "<strong>Crossbreed advantage</strong>: Combines {trait1} and {trait2}",
        'indigenous': "🏞️ <strong>Adaptation</strong>: Well-adapted to {region} conditions"
    }
    
    def generate_explanation(self, breed, county, score):
        """Generate explanation for a breed recommendation"""
        reasons = []
        
        # Heat tolerance explanation
        thi_range = f"{county.get('min_thi', '?')}-{county.get('max_thi', '?')}"
        if breed.get('heat_tolerance_score', 0) >= 7:
            reasons.append(self.reason_templates['heat'].format(thi_range=thi_range))
        elif breed.get('heat_tolerance_score', 0) <= 3:
            reasons.append(f"🌡️ **Heat management**: Requires cooling during peak THI months")
        
        # Disease resistance
        if breed.get('disease_resistance_score', 0) >= 7 and county.get('disease_index', 0) >= 6:
            reasons.append(self.reason_templates['disease'].format(diseases="tick-borne diseases"))
        
        # Milk yield
        milk_min = breed.get('milk_yield_potential_min', 0)
        milk_max = breed.get('milk_yield_potential_max', 0)
        adjusted_yield = int((milk_min + milk_max) / 2 * (score / 100))
        reasons.append(self.reason_templates['milk'].format(
            yield_range=f"{adjusted_yield-2}-{adjusted_yield+2}"
        ))
        
        # Breed type specific
        if breed.get('breed_type') == 'Crossbreed':
            reasons.append(self.reason_templates['crossbreed'].format(
                trait1="productivity", 
                trait2="adaptability"
            ))
        elif breed.get('breed_type') == 'Pure Indigenous':
            reasons.append(self.reason_templates['indigenous'].format(region=county.get('region', 'local')))
        
        return " ".join(reasons[:3])  # Limit to 3 reasons
    
    def generate_comparison(self, breed1, breed2, county):
        """Generate comparison between two breeds"""
        if not breed1 or not breed2:
            return ""
        
        comparison = []
        comparison.append(f"<strong>{breed1['breed_name']}</strong> vs <strong>{breed2['breed_name']}</strong> in {county['county_name']}:")
        
        # Compare heat tolerance
        ht1 = breed1.get('heat_tolerance_score', 0)
        ht2 = breed2.get('heat_tolerance_score', 0)
        if ht1 > ht2:
            comparison.append(f"• 🔥 {breed1['breed_name']} handles heat better (+{ht1-ht2} points)")
        elif ht2 > ht1:
            comparison.append(f"• 🔥 {breed2['breed_name']} handles heat better (+{ht2-ht1} points)")
        
        # Compare milk yield
        my1 = breed1.get('milk_yield_potential_max', 0)
        my2 = breed2.get('milk_yield_potential_max', 0)
        if my1 > my2:
            comparison.append(f"• 🥛 {breed1['breed_name']} produces more milk (+{my1-my2} L/day)")
        elif my2 > my1:
            comparison.append(f"• 🥛 {breed2['breed_name']} produces more milk (+{my2-my1} L/day)")
        
        return "\n".join(comparison)