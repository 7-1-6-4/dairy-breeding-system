class ExplainerService:
    """Generate human-readable explanations for recommendations"""
    
    def __init__(self):
        self.reason_templates = {
            'heat': "🌡️ <strong>Heat tolerance</strong>: Thrives in THI ranges of {thi_range}",
            'disease': "🛡️ <strong>Disease resistance</strong>: Strong resistance to {diseases}",
            'milk': "🥛 <strong>Milk production</strong>: Expected yield {yield_range} L/day",
            'feed': "🌿 <strong>Feed efficiency</strong>: Excellent conversion of {feed_type}",
            'crossbreed': "🔄 <strong>Crossbreed advantage</strong>: Combines {trait1} and {trait2}",
            'indigenous': "🏞️ <strong>Adaptation</strong>: Well-adapted to {region} conditions"
        }
        
        # Crossbreed base recommendations
        self.crossbreed_base = {
            'B006': {'base_breed': 'Sahiwal', 'improving_breed': 'Friesian', 'base_id': 'B004', 'improving_id': 'B001'},
            'B007': {'base_breed': 'Sahiwal', 'improving_breed': 'Ayrshire', 'base_id': 'B004', 'improving_id': 'B002'},
            'B008': {'base_breed': 'Sahiwal', 'improving_breed': 'Jersey', 'base_id': 'B004', 'improving_id': 'B003'},
            'B009': {'base_breed': 'Boran', 'improving_breed': 'Friesian', 'base_id': 'B005', 'improving_id': 'B001'},
            'B010': {'base_breed': 'Boran', 'improving_breed': 'Ayrshire', 'base_id': 'B005', 'improving_id': 'B002'}
        }
    
    def generate_explanation(self, breed, county, score, has_current_breed=False, current_breed_info=None):
        """Generate explanation for a breed recommendation"""
        reasons = []
        
        # Heat tolerance explanation
        thi_range = f"{county.get('min_thi', '?')}-{county.get('max_thi', '?')}"
        if breed.get('heat_tolerance_score', 0) >= 7:
            reasons.append(self.reason_templates['heat'].format(thi_range=thi_range))
        elif breed.get('heat_tolerance_score', 0) <= 3:
            reasons.append(f"🌡️ <strong>Heat management</strong>: Requires cooling during peak THI months")
        
        # Disease resistance
        if breed.get('disease_resistance_score', 0) >= 7 and county.get('disease_index', 0) >= 6:
            reasons.append(self.reason_templates['disease'].format(diseases="tick-borne diseases"))
        
        # Milk yield calculation
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
        
        # ========== NEW: Starting point explanation for farmers with no cow ==========
        if not has_current_breed and breed.get('breed_type') == 'Crossbreed':
            base_info = self.crossbreed_base.get(breed.get('breed_id'))
            if base_info:
                starting_advice = f" 💡 <strong>How to start</strong>: Begin with a {base_info['base_breed']} cow. " \
                                 f"Once established, breed it with a {base_info['improving_breed']} bull to get this crossbreed. " \
                                 f"This approach ensures your foundation cow is well-adapted to your local conditions."
                reasons.append(starting_advice)
        
        # ========== NEW: Crossbreeding upgrade explanation for farmers with existing cow ==========
        if has_current_breed and current_breed_info and breed.get('breed_type') == 'Crossbreed':
            current_type = current_breed_info.get('breed_type', '')
            current_name = current_breed_info.get('breed_name', '')
            
            if current_type == 'Pure Exotic':
                # They have a pure exotic - recommend crossing with indigenous
                if 'Friesian' in current_name:
                    base_breed = 'Sahiwal'
                elif 'Ayrshire' in current_name:
                    base_breed = 'Sahiwal'
                elif 'Jersey' in current_name:
                    base_breed = 'Sahiwal'
                else:
                    base_breed = 'Sahiwal'
                
                upgrade_advice = f" 💡 <strong>Crossbreeding strategy</strong>: Since you already own a {current_name}, " \
                                f"breed it with a {base_breed} bull. This crossbreed calf will have better heat tolerance " \
                                f"and disease resistance while maintaining good milk production."
                reasons.append(upgrade_advice)
                
            elif current_type == 'Pure Indigenous':
                # They have a pure indigenous - recommend crossing with exotic
                if 'Sahiwal' in current_name:
                    improving_breed = 'Friesian or Jersey'
                elif 'Boran' in current_name:
                    improving_breed = 'Friesian or Ayrshire'
                else:
                    improving_breed = 'Friesian'
                
                upgrade_advice = f" 💡 <strong>Crossbreeding strategy</strong>: Your {current_name} is already well-adapted. " \
                                f"Breed it with a {improving_breed} bull. The crossbreed calf will inherit your cow's resilience " \
                                f"AND gain higher milk production potential."
                reasons.append(upgrade_advice)
                
            elif current_type == 'Crossbreed':
                # They already have a crossbreed - recommend continuing
                upgrade_advice = f" 💡 <strong>Continue the program</strong>: Your current {current_name} is already a crossbreed. " \
                                f"Continue this breeding program to maintain the optimal balance of productivity and adaptation."
                reasons.append(upgrade_advice)
        
        return " ".join(reasons[:4])  # Allow up to 4 reasons now
    
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
        
        # Compare disease resistance
        dr1 = breed1.get('disease_resistance_score', 0)
        dr2 = breed2.get('disease_resistance_score', 0)
        if dr1 > dr2:
            comparison.append(f"• 🛡️ {breed1['breed_name']} has better disease resistance (+{dr1-dr2} points)")
        elif dr2 > dr1:
            comparison.append(f"• 🛡️ {breed2['breed_name']} has better disease resistance (+{dr2-dr1} points)")
        
        return "\n".join(comparison)