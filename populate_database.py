"""
Database Population Script for AI Dairy Breeding System
Populates Supabase tables with data from CSV files
"""

import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin access

if not url or not key:
    print("❌ ERROR: Missing SUPABASE_URL or SUPABASE_KEY in .env file")
    exit(1)

supabase = create_client(url, key)
print("✅ Connected to Supabase successfully!")

# ============================================
# HELPER FUNCTIONS
# ============================================

def clear_table(table_name):
    """Clear all data from a table (use with caution!)"""
    try:
        supabase.table(table_name).delete().neq('county_id', 0).execute()
        print(f"  Cleared table: {table_name}")
    except Exception as e:
        print(f"  Note: Could not clear {table_name} (may be empty)")

def insert_batch(table, records, batch_size=50, delay=0.5):
    """Insert records in batches to avoid rate limits"""
    total = len(records)
    for i in range(0, total, batch_size):
        batch = records[i:i+batch_size]
        try:
            supabase.table(table).insert(batch).execute()
            print(f"    Inserted {i+1} to {min(i+batch_size, total)}", end='\r')
            time.sleep(delay)
        except Exception as e:
            print(f"\n    ❌ Error inserting batch: {e}")
            return False
    print(f"    ✅ Inserted {total} records into {table}")
    return True

# ============================================
# POPULATE COUNTIES TABLE
# ============================================

def populate_counties():
    """Insert county data from CSV"""
    print("\n📊 POPULATING COUNTIES TABLE...")
    
    try:
        # Read CSV
        df = pd.read_csv('D:/Projects/dairy-breeding-project/dairy_breeding_dataset/county_environmental_profiles.csv')
        print(f"  Found {len(df)} counties in CSV")
        
        # Clean and prepare data
        records = []
        for _, row in df.iterrows():
            record = {
                'county_id': int(row['county_id']),
                'county_name': row['county_name'],
                'region': row['region'],
                'altitude_m': int(row['altitude_m']) if pd.notna(row['altitude_m']) else None,
                'avg_temp_c': float(row['avg_temp_c']) if pd.notna(row['avg_temp_c']) else None,
                'min_temp_c': float(row['min_temp_c']) if pd.notna(row['min_temp_c']) else None,
                'max_temp_c': float(row['max_temp_c']) if pd.notna(row['max_temp_c']) else None,
                'avg_humidity_pct': int(row['avg_humidity_pct']) if pd.notna(row['avg_humidity_pct']) else None,
                'annual_rainfall_mm': int(row['annual_rainfall_mm']) if pd.notna(row['annual_rainfall_mm']) else None,
                'avg_thi': float(row['avg_thi']) if pd.notna(row['avg_thi']) else None,
                'min_thi': float(row['min_thi']) if pd.notna(row['min_thi']) else None,
                'max_thi': float(row['max_thi']) if pd.notna(row['max_thi']) else None,
                'disease_index': float(row['disease_index']) if pd.notna(row['disease_index']) else None,
                'vegetation_zone': row['vegetation_zone'] if pd.notna(row['vegetation_zone']) else None,
                'soil_fertility': row['soil_fertility'] if pd.notna(row['soil_fertility']) else None
            }
            records.append(record)
        
        # Insert data
        success = insert_batch('counties', records, batch_size=10)
        if success:
            print(f"  ✅ Successfully inserted {len(records)} counties")
            return True
        return False
        
    except FileNotFoundError:
        print("  ❌ ERROR: county_environmental_profiles.csv not found!")
        print("    Make sure CSV files are in dairy_breeding_dataset/ folder")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

# ============================================
# POPULATE BREEDS TABLE
# ============================================

def populate_breeds():
    """Insert breed data from CSV"""
    print("\n🐄 POPULATING BREEDS TABLE...")
    
    try:
        # Read CSV
        df = pd.read_csv('D:/Projects/dairy-breeding-project/dairy_breeding_dataset/breed_trait_profiles.csv')
        print(f"  Found {len(df)} breeds in CSV")
        
        # Clean and prepare data
        records = []
        for _, row in df.iterrows():
            record = {
                'breed_id': row['breed_id'],
                'breed_name': row['breed_name'],
                'breed_type': row['breed_type'],
                'origin': row['origin'] if pd.notna(row['origin']) else None,
                'mature_weight_kg_min': int(row['mature_weight_kg_min']) if pd.notna(row['mature_weight_kg_min']) else None,
                'mature_weight_kg_max': int(row['mature_weight_kg_max']) if pd.notna(row['mature_weight_kg_max']) else None,
                'height_cm_min': int(row['height_cm_min']) if pd.notna(row['height_cm_min']) else None,
                'height_cm_max': int(row['height_cm_max']) if pd.notna(row['height_cm_max']) else None,
                'milk_yield_potential_min': int(row['milk_yield_potential_min']) if pd.notna(row['milk_yield_potential_min']) else None,
                'milk_yield_potential_max': int(row['milk_yield_potential_max']) if pd.notna(row['milk_yield_potential_max']) else None,
                'milk_yield_stress_min': int(row['milk_yield_stress_min']) if pd.notna(row['milk_yield_stress_min']) else None,
                'milk_yield_stress_max': int(row['milk_yield_stress_max']) if pd.notna(row['milk_yield_stress_max']) else None,
                'butterfat_pct': float(row['butterfat_pct']) if pd.notna(row['butterfat_pct']) else None,
                'protein_pct': float(row['protein_pct']) if pd.notna(row['protein_pct']) else None,
                'heat_tolerance_score': int(row['heat_tolerance_score']) if pd.notna(row['heat_tolerance_score']) else None,
                'cold_tolerance_score': int(row['cold_tolerance_score']) if pd.notna(row['cold_tolerance_score']) else None,
                'disease_resistance_score': int(row['disease_resistance_score']) if pd.notna(row['disease_resistance_score']) else None,
                'parasite_resistance': int(row['parasite_resistance']) if pd.notna(row['parasite_resistance']) else None,
                'feed_efficiency_score': int(row['feed_efficiency_score']) if pd.notna(row['feed_efficiency_score']) else None,
                'temperament_score': int(row['temperament_score']) if pd.notna(row['temperament_score']) else None,
                'calving_ease_score': int(row['calving_ease_score']) if pd.notna(row['calving_ease_score']) else None,
                'longevity_years_min': int(row['longevity_years_min']) if pd.notna(row['longevity_years_min']) else None,
                'longevity_years_max': int(row['longevity_years_max']) if pd.notna(row['longevity_years_max']) else None,
                'critical_thi_threshold': int(row['critical_thi_threshold']) if pd.notna(row['critical_thi_threshold']) else None,
                'description': f"{row['breed_name']} - {row['breed_type']} breed from {row['origin']}" if pd.notna(row['origin']) else None
            }
            records.append(record)
        
        # Insert data
        success = insert_batch('breeds', records, batch_size=10)
        if success:
            print(f"  ✅ Successfully inserted {len(records)} breeds")
            return True
        return False
        
    except FileNotFoundError:
        print("  ❌ ERROR: breed_trait_profiles.csv not found!")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

# ============================================
# POPULATE SUITABILITY SCORES TABLE
# ============================================

def populate_suitability_scores():
    """Insert suitability scores from training data"""
    print("\n📈 POPULATING SUITABILITY SCORES TABLE...")
    
    try:
        # Read training data
        df = pd.read_csv('D:/Projects/dairy-breeding-project/dairy_breeding_dataset/model_training_dataset.csv')
        print(f"  Found {len(df)} records in training dataset")
        
        # Group by county and breed to get average scores
        grouped = df.groupby(['county_id', 'breed_id']).agg({
            'overall_suitability': 'mean',
            'milk_yield_actual': 'mean',
            'heat_tolerance_score': 'first',
            'disease_resistance_score': 'first',
            'feed_efficiency_score': 'first',
            'confidence': 'mean'
        }).reset_index()
        
        print(f"  Creating {len(grouped)} county-breed combinations")
        
        # Create records
        records = []
        for _, row in grouped.iterrows():
            # Calculate component scores
            milk_score = (row['milk_yield_actual'] / 30) * 100
            health_score = row['disease_resistance_score'] * 10
            adaptation_score = (row['heat_tolerance_score'] + row['feed_efficiency_score']) * 5
            economic_score = (milk_score + adaptation_score) / 2
            
            record = {
                'county_id': int(row['county_id']),
                'breed_id': row['breed_id'],
                'suitability_score': round(float(row['overall_suitability']), 2),
                'milk_score': round(min(milk_score, 100), 2),
                'health_score': round(min(health_score, 100), 2),
                'adaptation_score': round(min(adaptation_score, 100), 2),
                'economic_score': round(min(economic_score, 100), 2),
                'confidence_level': round(float(row['confidence']), 1),
                'validation_status': 'Validated' if row['confidence'] > 8.5 else 'Pending'
            }
            records.append(record)
        
        # Insert data
        success = insert_batch('suitability_scores', records, batch_size=20)
        if success:
            print(f"  ✅ Successfully inserted {len(records)} suitability scores")
            return True
        return False
        
    except FileNotFoundError:
        print("  ❌ ERROR: model_training_dataset.csv not found!")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

# ============================================
# VERIFY DATA
# ============================================

def verify_data():
    """Check that data was inserted correctly"""
    print("\n🔍 VERIFYING DATA...")
    
    tables = [
        ('counties', 47),
        ('breeds', 10),
        ('suitability_scores', 470)
    ]
    
    all_good = True
    for table, expected in tables:
        try:
            result = supabase.table(table).select('*', count='exact').execute()
            count = result.count
            status = "✅" if count == expected else "⚠️"
            print(f"  {status} {table}: {count} records (expected {expected})")
            if count != expected:
                all_good = False
        except Exception as e:
            print(f"  ❌ Could not verify {table}: {e}")
            all_good = False
    
    # Show sample data
    if all_good:
        print("\n📋 Sample Data - Top 5 Breeds in Kiambu:")
        result = supabase.table('suitability_scores')\
            .select('breed_id, suitability_score')\
            .eq('county_id', 1)\
            .order('suitability_score', desc=True)\
            .limit(5)\
            .execute()
        
        for i, item in enumerate(result.data, 1):
            breed = supabase.table('breeds').select('breed_name').eq('breed_id', item['breed_id']).execute()
            breed_name = breed.data[0]['breed_name'] if breed.data else item['breed_id']
            print(f"    {i}. {breed_name}: {item['suitability_score']}%")
    
    return all_good

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    print("="*60)
    print("🐄 DAIRY BREEDING SYSTEM - DATABASE POPULATION")
    print("="*60)
    
    # Check if CSV directory exists
    if not os.path.exists('../dairy_breeding_dataset'):
        print("\n❌ ERROR: 'dairy_breeding_dataset' folder not found!")
        print("   Current directory:", os.getcwd())
        print("   Expected: ../dairy_breeding_dataset/")
        return
    
    # Optional: Clear existing data (uncomment if needed)
    # print("\n⚠️  Clearing existing data...")
    # clear_table('suitability_scores')
    # clear_table('breeds')
    # clear_table('counties')
    
    # Populate tables in correct order
    success = True
    
    if not populate_counties():
        success = False
        print("\n❌ Failed to populate counties. Stopping.")
        return
    
    if not populate_breeds():
        success = False
        print("\n❌ Failed to populate breeds. Stopping.")
        return
    
    if not populate_suitability_scores():
        success = False
        print("\n❌ Failed to populate suitability scores. Stopping.")
        return
    
    # Verify everything worked
    if success:
        print("\n" + "="*60)
        if verify_data():
            print("\n✅ DATABASE POPULATION COMPLETE! All data loaded successfully.")
        else:
            print("\n⚠️ Database populated but verification found issues.")
    else:
        print("\n❌ Database population failed. Check errors above.")
    
    print("="*60)

if __name__ == "__main__":
    main()