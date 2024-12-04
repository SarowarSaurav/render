from flask import Flask, request, jsonify
import requests
import base64
import os
from flask_cors import CORS
import traceback
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/analyze_leaf', methods=['POST'])
def analyze_leaf_disease():
    try:
        # Log the entire incoming request for debugging
        logger.debug(f"Received request: {request.json}")
        
        # Validate request data
        if not request.json:
            logger.error("No JSON data received")
            return jsonify({"error": "No data provided"}), 400
        
        # Extract image data
        image_base64 = request.json.get('image')
        if not image_base64:
            logger.error("No image data in request")
            return jsonify({"error": "No image data provided"}), 400

        # Retrieve API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            logger.error("Anthropic API key not configured")
            return jsonify({"error": "API Key not configured"}), 400

        # Prepare headers for Anthropic API
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "X-API-Key": api_key
        }

        # Prepare payload for Anthropic API
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

        # Make request to Anthropic API
        response = requests.post(
            "https://api.anthropic.com/v1/messages", 
            headers=headers, 
            json=payload
        )

        # Log the response status and content for debugging
        logger.debug(f"Anthropic API Response Status: {response.status_code}")
        logger.debug(f"Anthropic API Response Content: {response.text}")

        # Raise an exception for bad responses
        response.raise_for_status()

        # Parse the response
        result = response.json()
        
        # Return the analysis
        return jsonify({
            "analysis": result['content'][0]['text']
        })
    
    except requests.exceptions.RequestException as e:
        # Log detailed error information
        logger.error(f"API Request Error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"API Request Error: {str(e)}",
            "details": traceback.format_exc()
        }), 500
    
    except Exception as e:
        # Catch and log any other unexpected errors
        logger.error(f"Unexpected Error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Unexpected Error: {str(e)}",
            "details": traceback.format_exc()
        }), 500

@app.route('/', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True)
