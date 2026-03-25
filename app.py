from flask import Flask, render_template_string, request, Response, stream_with_context
import requests
import uuid
import json

app = Flask(__name__)

# --- NEW ERA SAAS UI (Premium Glassmorphism) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopSense AI | Intelligent Product Research</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #030712; color: #f9fafb; font-family: 'Inter', sans-serif; overflow-x: hidden; }
        .glass { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .neon-text { text-shadow: 0 0 10px #3b82f6, 0 0 20px #2563eb; }
        .neon-border { border: 1px solid #3b82f6; box-shadow: 0 0 15px rgba(59, 130, 246, 0.3); }
        .loader-dot { animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
        #terminal::-webkit-scrollbar { width: 4px; }
        #terminal::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 10px; }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-4xl w-full">
        <div class="text-center mb-10">
            <h1 class="text-5xl font-extrabold tracking-tighter mb-2 italic">ShopSense<span class="text-blue-500 neon-text">AI</span></h1>
            <p class="text-gray-400 font-medium">Next-Gen Shopping Intelligence. No Limits, Just Data.</p>
        </div>

        <div class="glass p-6 rounded-2xl mb-6 neon-border">
            <div class="flex flex-col md:flex-row gap-4">
                <input type="text" id="query" placeholder="Ask anything: 'Is PS5 Pro worth it?' or 'Best organic soap'..." 
                       class="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500 transition-all text-white">
                <button onclick="launchAnalysis()" id="fireBtn" class="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-8 rounded-xl transition-all flex items-center justify-center gap-2">
                    <span>LAUNCH SCAN</span>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
                </button>
            </div>
        </div>

        <div id="terminal" class="glass rounded-2xl p-6 h-[450px] overflow-y-auto font-mono text-sm border border-gray-800">
            <div class="text-gray-500 mb-4">// System initialized. Awaiting user input...</div>
            <div id="output-stream" class="space-y-3"></div>
        </div>
        
        <div class="mt-4 text-center text-xs text-gray-600">
            &copy; 2026 ShopSense AI • Powered by Ghost-Identity Logic
        </div>
    </div>

    <script>
        function launchAnalysis() {
            const query = document.getElementById('query').value;
            const output = document.getElementById('output-stream');
            const btn = document.getElementById('fireBtn');
            
            if(!query) return;

            // Reset UI
            output.innerHTML = '<div class="text-blue-400 font-bold tracking-widest">[CRITICAL] INITIALIZING PROXY SESSION...</div>';
            btn.disabled = true;
            btn.classList.add('opacity-50', 'cursor-not-allowed');

            const eventSource = new EventSource(`/api/v1/analyze?q=${encodeURIComponent(query)}`);
            
            eventSource.onmessage = function(e) {
                try {
                    const rawData = JSON.parse(e.data);
                    const responses = rawData.responses?.researchProductComparison;
                    
                    if (responses) {
                        const dataObj = Object.values(responses)[0];
                        
                        // 1. Process Logs (The "Updating" feeling)
                        if (dataObj.statusLog) {
                            dataObj.statusLog.forEach(log => {
                                const logElement = document.createElement('div');
                                logElement.className = 'flex items-center gap-2 text-gray-300 animate-pulse';
                                logElement.innerHTML = `<span class="text-blue-500">▹</span> ${log.statusMessage}...`;
                                output.appendChild(logElement);
                            });
                        }

                        // 2. The Final "Okay" (Rich Data)
                        if (dataObj.data) {
                            const dataBox = document.createElement('div');
                            dataBox.className = 'bg-blue-900/20 border border-blue-500/30 p-4 rounded-lg mt-4 text-blue-100 whitespace-pre-wrap';
                            dataBox.innerHTML = `<strong>🔥 ANALYSIS COMPLETE:</strong><br>${JSON.stringify(dataObj.data, null, 2)}`;
                            output.appendChild(dataBox);
                            eventSource.close();
                            finalizeUI();
                        }
                    }
                } catch(err) {}
                document.getElementById('terminal').scrollTop = document.getElementById('terminal').scrollHeight;
            };

            eventSource.onerror = function() {
                eventSource.close();
                finalizeUI();
            };
        }

        function finalizeUI() {
            const btn = document.getElementById('fireBtn');
            btn.disabled = false;
            btn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    </script>
</body>
</html>
"""

def server_side_stream(q):
    # 🛡️ Ghost-Identity Logic (Unlimited)
    session_id = f"anonymous:{uuid.uuid4()}"
    query_id = uuid.uuid4().hex[:16]
    
    url = "https://api.vetted.ai/queries"
    
    # 🛠️ All Headers Hidden on Server Side
    headers = {
        "Content-Type": "application/json",
        "x-session-id": session_id,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://vetted.ai",
        "Referer": "https://vetted.ai/",
        "Accept": "application/x-ndjson"
    }
    
    payload = {
        "queries": {
            "researchProductComparison": {
                query_id: {
                    "localization": "IN",
                    "context": f"Perform a deep web research and consumer sentiment analysis for: {q}. Provide pros, cons, and verdict."
                }
            }
        }
    }

    try:
        with requests.post(url, json=payload, headers=headers, stream=True, timeout=90) as r:
            for line in r.iter_lines():
                if line:
                    yield f"data: {line.decode('utf-8')}\\n\\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\\n\\n"

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/v1/analyze')
def api_analyze():
    q = request.args.get('q', '')
    if not q: return Response("Missing query", status=400)
    return Response(stream_with_context(server_side_stream(q)), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
