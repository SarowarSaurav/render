from flask import Flask, request, jsonify
import requests
import base64
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/analyze_leaf', methods=['POST'])
def analyze_leaf_disease():
    # Get the image and API key from the request
    image_base64 = request.json.get('image')
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        return jsonify({"error": "API Key not configured"}), 400

    headers = {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
        "X-API-Key": api_key
    }

    payload = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": """Analyze this leaf image in detail. 
                        Identify:
                        1. Plant species (if possible)
                        2. Specific disease or health condition
                        3. Detailed symptoms
                        4. Potential causes
                        5. Recommended treatment or management strategies
                        
                        Provide a comprehensive and clear explanation."""
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages", 
            headers=headers, 
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        return jsonify({"analysis": result['content'][0]['text']})
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
