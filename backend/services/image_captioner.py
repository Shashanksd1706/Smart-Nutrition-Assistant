# Replace your entire services/image_captioner.py file with this:

import google.generativeai as genai
from PIL import Image
import io
import os

def generate_caption_with_gemini(image_data):
    """
    Analyze food image using Gemini Vision API and return food items
    """
    try:
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return ["Error: GEMINI_API_KEY not configured"]
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Convert bytes to PIL Image
        try:
            image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            return [f"Error: Invalid image format - {str(e)}"]
        
        # Create prompt for food identification
        prompt = """
        Analyze this food image and identify all the food items you can see. 
        Return only a comma-separated list of food items, nothing else.
        For example: "rice, chicken curry, vegetables, bread"
        If no food is visible, return "no food items detected"
        """
        
        # Generate content with image
        response = model.generate_content([prompt, image])
        
        # Parse the response into a list
        if response.text:
            food_items = [item.strip() for item in response.text.split(',')]
            return food_items
        else:
            return ["No food items detected"]
            
    except Exception as e:
        return [f"Error analyzing image: {str(e)}"]