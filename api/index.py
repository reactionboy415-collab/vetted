import requests
import uuid
from flask import Flask, request, Response, stream_with_context

app = Flask(__name__)

@app.route("/api/vetted")
def vetted():

    product = request.args.get("product", "iphone")

    session_id = f"anonymous:{uuid.uuid4()}"

    headers = {
        "Content-Type": "application/json",
        "x-session-id": session_id,
        "User-Agent": "Mozilla/5.0 (Linux; Android 12)",
        "Origin": "https://vetted.ai",
        "Referer": "https://vetted.ai/",
        "Accept": "application/x-ndjson, application/json"
    }

    query_id = uuid.uuid4().hex[:16]

    payload = {
        "queries": {
            "researchProductComparison": {
                query_id: {
                    "localization": "IN",
                    "context": f"I want to know if I should buy {product}. Analyze reviews, pros, cons and value for money."
                }
            }
        }
    }

    def generate():
        try:
            r = requests.post(
                "https://api.vetted.ai/queries",
                json=payload,
                headers=headers,
                stream=True,
                timeout=120
            )

            for chunk in r.iter_lines():
                if chunk:
                    yield chunk.decode() + "\n"

        except Exception as e:
            yield f"ERROR: {str(e)}"

    return Response(stream_with_context(generate()), mimetype="text/plain")

# Vercel handler
def handler(request):
    return app(request.environ, lambda status, headers: None)
