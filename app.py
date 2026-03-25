from flask import Flask, render_template_string, request, Response, stream_with_context
import requests
import uuid
import json
import time

app = Flask(__name__)

# --- HTML FRONTEND (Embedded) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💀 VETTED AI UNLIMITED 💀</title>
    <style>
        body { background: #000; color: #0f0; font-family: 'Segoe UI', monospace; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .terminal { width: 100%; max-width: 900px; border: 1px solid #0f0; background: #050505; padding: 20px; box-shadow: 0 0 20px rgba(0, 255, 0, 0.2); }
        h1 { text-align: center; color: #fff; text-shadow: 0 0 10px #0f0; margin-top: 0; }
        .input-group { display: flex; gap: 10px; margin-bottom: 20px; }
        input { flex: 1; padding: 12px; background: #111; border: 1px solid #0f0; color: #0f0; outline: none; }
        button { padding: 12px 25px; background: #0f0; color: #000; border: none; cursor: pointer; font-weight: bold; transition: 0.3s; }
        button:hover { background: #fff; box-shadow: 0 0 15px #fff; }
        #output { height: 500px; overflow-y: auto; border-top: 1px solid #333; padding: 15px; font-size: 13px; line-height: 1.6; color: #ccc; }
        .log-entry { margin-bottom: 8px; border-left: 2px solid #0f0; padding-left: 10px; }
        .status-msg { color: #ff0; font-weight: bold; }
        .data-msg { color: #0fa; background: #001a00; padding: 10px; border-radius: 4px; margin-top: 5px; }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #0f0; }
    </style>
</head>
<body>
    <div class="terminal">
        <h1>💀 VETTED.AI UNLIMITED BYPASS 💀</h1>
        <div class="input-group">
            <input type="text" id="query" placeholder="Enter Product (e.g. PS5 vs Xbox, Best Soap for skin...)">
            <button onclick="fireResearch()">ANALYSIS</button>
        </div>
        <div id="output">System Ready. Awaiting Command...</div>
    </div>

    <script>
        function fireResearch() {
            const query = document.getElementById('query').value;
            const output = document.getElementById('output');
            if(!query) return alert("Pehle product name toh daal bhai!");

            output.innerHTML = "📡 [SYSTEM] Initializing Ghost Session...<br>";
            
            const eventSource = new EventSource(`/api/research?q=${encodeURIComponent(query)}`);
            
            eventSource.onmessage = function(e) {
                try {
                    const rawData = JSON.parse(e.data);
                    const responses = rawData.responses?.researchProductComparison;
                    
                    if (responses) {
                        const dataObj = Object.values(responses)[0];
                        
                        // Status Updates Display
                        if (dataObj.statusLog) {
                            dataObj.statusLog.forEach(log => {
                                output.innerHTML += `<div class='log-entry'><span class='status-msg'>⚡ ${log.statusMessage}</span></div>`;
                            });
                        }

                        // Final Data Display
                        if (dataObj.data) {
                            output.innerHTML += `<div class='data-msg'>📦 DATA RECEIVED:<br>${JSON.stringify(dataObj.data, null, 2)}</div>`;
                        }
                    }
                } catch(err) {
                    // console.log("Stream Chunk:", e.data);
                }
                output.scrollTop = output.scrollHeight;
            };

            eventSource.onerror = function() {
                output.innerHTML += "<br>✅ [SYSTEM] Research Deep-Scan Completed.";
                eventSource.close();
            };
        }
    </script>
</body>
</html>
"""

def stream_vetted(product):
    session_id = f"anonymous:{uuid.uuid4()}"
    query_id = uuid.uuid4().hex[:16]
    
    url = "https://api.vetted.ai/queries"
    headers = {
        "Content-Type": "application/json",
        "x-session-id": session_id,
        "User-Agent": "Mozilla/5.0 (Linux; Android 12)",
        "Origin": "https://vetted.ai",
        "Accept": "application/x-ndjson"
    }
    
    payload = {
        "queries": {
            "researchProductComparison": {
                query_id: {
                    "localization": "IN",
                    "context": f"Detailed analysis for {product}"
                }
            }
        }
    }

    try:
        # 100% Unlimited logic: Direct stream fetching
        with requests.post(url, json=payload, headers=headers, stream=True, timeout=60) as r:
            for line in r.iter_lines():
                if line:
                    yield f"data: {line.decode('utf-8')}\\n\\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\\n\\n"

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/research')
def research_api():
    q = request.args.get('q', 'gadgets')
    return Response(stream_with_context(stream_vetted(q)), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
