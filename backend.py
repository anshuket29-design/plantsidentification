from groq import Groq
import base64
import os
import time
from googlesearch import search
from transformers import pipeline

# ================== CONFIG ==================
client = Groq(api_key="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")

VISION_MODEL = "llama-3.2-11b-vision-preview"
TEXT_MODEL = "llama3-8b-8192"


# ================== STEP 1 ==================
# Image Analysis (Vision)
def analyze_image(image_bytes: bytes) -> str:
    try:
        # Encode image bytes to base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{base64_image}"

        # Step 1: Verify it is a plant/crop image
        verify_completion = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Check if this image is of a plant, crop, or farm field. Reply only 'Yes' or 'No'."},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ],
            temperature=0.0,
            max_completion_tokens=10
        )

        verify_response = verify_completion.choices[0].message.content
        if isinstance(verify_response, list):
            verify_response = verify_response[0].get("text", "")

        if verify_response.strip().lower() != "yes":
            return "This is not a plant or crop image. Skipping analysis."

        # Step 2: Actual crop analysis
        completion = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert agricultural analyst."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this farm or crop image and describe crop type, health, soil condition, and visible issues."},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ],
            temperature=0.3,
            max_completion_tokens=400
        )

        message = completion.choices[0].message
        if isinstance(message.content, list):
            return message.content[0].get("text", "No description generated")
        else:
            return message.content or "No description generated"

    except Exception as e:
        return f"Image analysis failed: {e}"



# ================== STEP 2 ==================
# Farming Intelligence
def analyze_farming_data(image_description: str) -> dict:
    try:
        prompt = f"""
Based on the following farm image analysis:

{image_description}

Provide structured farming advice in this exact format:

Crop Prediction:
Smart Irrigation:
Pest Detection:
Yield Optimization:
"""

        completion = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "You are a smart farming advisor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_completion_tokens=500
        )

        return parse_farming_response(completion.choices[0].message.content)

    except Exception as e:
        return {"error": True, "message": str(e)}


# ================== PARSER ==================
def parse_farming_response(text: str) -> dict:
    def extract(section):
        for line in text.splitlines():
            if line.lower().startswith(section.lower()):
                return line.split(":", 1)[1].strip()
        return "Not available"

    return {
        "error": False,
        "crop_prediction": extract("Crop Prediction"),
        "smart_irrigation": extract("Smart Irrigation"),
        "pest_detection": extract("Pest Detection"),
        "yield_optimization": extract("Yield Optimization")
    }


# ================== STEP 3 ==================
# Google Search
def search_google(query: str, num_results: int = 5) -> list:
    results = []
    try:
        for url in search(query):
            results.append(url)
            time.sleep(1)
            if len(results) >= num_results:
                break
    except Exception as e:
        return [f"Search failed: {e}"]
    return results


# ================== RUN TEST ==================
if __name__ == "__main__":
    test_image = "https://upload.wikimedia.org/wikipedia/commons/6/6f/Wheat_field.jpg"

    print("Analyzing image...")
    desc = analyze_image(test_image)
    print(desc)

    print("\nGenerating farming advice...")
    advice = analyze_farming_data(desc)
    print(advice)

    print("\nBackend loaded successfully ✅")
