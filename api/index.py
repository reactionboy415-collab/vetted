from flask import Flask, request, Response, stream_with_context
import requests
import uuid
import json

app = Flask(__name__)

def generate_vetted_stream(topic):
    session_id = f"anonymous:{uuid.uuid4()}"
    query_id = uuid.uuid4().hex[:16]
    
    url = "https://api.vetted.ai/queries"
    headers = {
        "Content-Type": "application/json",
        "x-session-id": session_id,
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; LAVA Blaze)",
        "Origin": "https://vetted.ai",
        "Referer": "https://vetted.ai/",
        "Accept": "application/x-ndjson, application/json"
    }
    
    payload = {
        "queries": {
            "researchProductComparison": {
                query_id: {
                    "localization": "IN",
                    "context": f"I want to know if I should buy {topic}. Analyze reviews, pros, cons, and value for money."
                }
            }
        }
    }

    try:
        # Stream=True zaroori hai bade responses ke liye
        with requests.post(url, json=payload, headers=headers, stream=True, timeout=60) as r:
            for line in r.iter_lines():
                if line:
                    # Har chunk ko frontend ke liye yield kar rahe hain
                    yield line.decode('utf-8') + "\\n"
    except Exception as e:
        yield json.dumps({"error": str(e)})

@app.route('/api/analyze', methods=['GET'])
def analyze():
    topic = request.args.get('topic')
    if not topic:
        return {"error": "Bhai, topic toh daal!"}, 400
        
    return Response(
        stream_with_context(generate_vetted_stream(topic)),
        mimetype='application/x-ndjson'
    )

# Vercel handling
def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    app.run(debug=True)
