import requests
import uuid
import json

def handler(request):

    try:
        product = request.args.get("product") or "wifi extender"

        session_id = f"anonymous:{uuid.uuid4()}"

        headers = {
            "Content-Type": "application/json",
            "x-session-id": session_id,
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://vetted.ai",
            "Referer": "https://vetted.ai/",
            "Accept": "application/json"
        }

        query_id = uuid.uuid4().hex[:16]

        payload = {
            "queries": {
                "researchProductComparison": {
                    query_id: {
                        "localization": "IN",
                        "context": f"I want to know if I should buy {product}. Analyze reviews pros cons and value."
                    }
                }
            }
        }

        r = requests.post(
            "https://api.vetted.ai/queries",
            json=payload,
            headers=headers,
            timeout=25
        )

        return {
            "statusCode": 200,
            "headers": {"content-type": "application/json"},
            "body": r.text
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }
