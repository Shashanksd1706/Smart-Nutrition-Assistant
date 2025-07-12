import pandas as pd
import os

# Check if CSV file exists and handle gracefully
csv_path = "data/food_nutrition.csv"
nutrition_df = None

if os.path.exists(csv_path):
    try:
        nutrition_df = pd.read_csv(csv_path)
        print(f"CSV loaded successfully. Shape: {nutrition_df.shape}")
        print(f"Columns: {nutrition_df.columns.tolist()}")
        print(f"First few rows:\n{nutrition_df.head()}")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        nutrition_df = None

# Create fallback data if CSV doesn't exist or failed to load
if nutrition_df is None or nutrition_df.empty:
    print("Using fallback nutrition data")
    nutrition_df = pd.DataFrame({
        'Food': ['Eggs', 'Chicken Breast', 'Salmon', 'Broccoli', 'Rice', 'Banana', 'Almonds', 'Apple', 'Spinach', 'Oats'],
        'Calories': [155, 165, 208, 55, 130, 105, 579, 95, 23, 389],
        'Protein': [13, 31, 22, 3, 2.7, 1.3, 21, 0.5, 2.9, 16.9],
        'Carbs': [1.1, 0, 0, 11, 28, 27, 22, 25, 3.6, 66],
        'Fat': [11, 3.6, 12, 0.6, 0.3, 0.4, 50, 0.3, 0.4, 6.9],
        'Fiber': [0, 0, 0, 5, 0.4, 3.1, 12, 4.4, 2.2, 10.6]
    })

def get_nutrition_facts(query):
    try:
        print(f"Searching for: '{query}'")
        print(f"Available foods: {nutrition_df['Food'].tolist()}")
        
        if nutrition_df.empty:
            print("DataFrame is empty")
            return []
        
        # Search for the food item (case-insensitive)
        results = nutrition_df[nutrition_df["Food"].str.contains(query, case=False, na=False)]
        print(f"Found {len(results)} results")
        
        if len(results) > 0:
            print(f"Results:\n{results}")
        
        return results.head(3).to_dict(orient="records")
    except Exception as e:
        print(f"Error in nutrition lookup: {e}")
        import traceback
        traceback.print_exc()
        return []

# Test the function
if __name__ == "__main__":
    test_result = get_nutrition_facts("Salmon")
    print(f"Test result: {test_result}")