from flask import Flask, render_template_string, request, Response, stream_with_context
import requests
import uuid
import json

app = Flask(__name__)

# --- HIGH-END EDITORIAL UI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopSense AI — Discern Better.</title>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,600&family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root { --bg: #0a0a0a; --accent: #d4af37; --text: #f4f4f4; }
        body { 
            background-color: var(--bg); 
            color: var(--text); 
            font-family: 'Outfit', sans-serif; 
            background-image: url("https://www.transparenttextures.com/patterns/carbon-fibre.png");
            overflow-x: hidden;
        }
        .serif { font-family: 'Cormorant Garamond', serif; }
        .glass-card { 
            background: rgba(20, 20, 20, 0.6); 
            backdrop-filter: blur(20px); 
            border: 1px solid rgba(212, 175, 55, 0.1); 
        }
        .search-input {
            background: transparent;
            border-bottom: 2px solid rgba(212, 175, 55, 0.3);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .search-input:focus {
            border-bottom: 2px solid var(--accent);
            padding-left: 15px;
        }
        .step-node {
            animation: slideIn 0.8s ease forwards;
            opacity: 0;
            transform: translateY(20px);
        }
        @keyframes slideIn {
            to { opacity: 1; transform: translateY(0); }
        }
        .dot-loader {
            width: 8px; height: 8px; background: var(--accent);
            border-radius: 50%; display: inline-block;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1.0); } }
    </style>
</head>
<body class="min-h-screen flex flex-col items-center py-20 px-6">
    
    <header class="text-center mb-16">
        <h1 class="text-6xl md:text-8xl serif italic mb-4">ShopSense</h1>
        <p class="uppercase tracking-[0.3em] text-[10px] text-gray-500 font-semibold">The Final Word in Product Intelligence</p>
    </header>

    <main class="w-full max-w-3xl">
        <div class="relative mb-20">
            <input type="text" id="query" autocomplete="off"
                   placeholder="Describe your requirement..." 
                   class="search-input w-full text-2xl md:text-3xl py-4 outline-none serif italic placeholder:opacity-30">
            <button onclick="ignite()" class="absolute right-0 bottom-4 text-xs tracking-widest uppercase hover:text-[#d4af37] transition-colors">
                Analyze &rarr;
            </button>
        </div>

        <div id="narrative-flow" class="space-y-12">
            </div>

        <div id="final-verdict" class="mt-20 opacity-0 transition-opacity duration-1000">
            <div class="glass-card p-10 rounded-sm border-l-4 border-l-[#d4af37]">
                <h3 class="serif text-3xl italic mb-6">The Collective Intelligence</h3>
                <div id="verdict-content" class="text-gray-400 leading-relaxed text-lg"></div>
            </div>
        </div>
    </main>

    <script>
        let currentStepId = '';

        function ignite() {
            const q = document.getElementById('query').value;
            if(!q) return;

            const flow = document.getElementById('narrative-flow');
            const verdict = document.getElementById('final-verdict');
            flow.innerHTML = '';
            verdict.style.opacity = '0';

            const source = new EventSource(`/api/v1/analyze?q=${encodeURIComponent(q)}`);
            
            source.onmessage = function(e) {
                const raw = JSON.parse(e.data);
                const results = raw.responses?.researchProductComparison;
                
                if(results) {
                    const data = Object.values(results)[0];
                    
                    // Handle "Thinking" / "Status" Updates
                    if(data.statusLog) {
                        data.statusLog.forEach(log => {
                            if(log.statusMessageId !== currentStepId) {
                                currentStepId = log.statusMessageId;
                                appendStep(log.statusMessage);
                            }
                        });
                    }

                    // Handle Final Rich Content
                    if(data.data) {
                        displayVerdict(data.data);
                        source.close();
                    }
                }
            };

            source.onerror = () => source.close();
        }

        function appendStep(msg) {
            const flow = document.getElementById('narrative-flow');
            const step = document.createElement('div');
            step.className = 'step-node flex items-center gap-6';
            step.innerHTML = `
                <div class="flex-none"><div class="dot-loader"></div></div>
                <div class="text-sm uppercase tracking-widest text-gray-400 font-light">${msg}</div>
            `;
            flow.appendChild(step);
        }

        function displayVerdict(data) {
            const verdict = document.getElementById('final-verdict');
            const content = document.getElementById('verdict-content');
            
            // Hum data ko thoda "SaaS" style mein format karenge
            content.innerHTML = typeof data === 'object' ? 
                `<pre class="font-sans whitespace-pre-wrap">${JSON.stringify(data, null, 2)}</pre>` : data;
            
            verdict.style.opacity = '1';
        }
    </script>
</body>
</html>
"""

def server_intelligence(q):
    uid = f"session-{uuid.uuid4().hex[:8]}"
    qid = uuid.uuid4().hex[:12]
    url = "https://api.vetted.ai/queries"
    
    # Strictly Server Side - No leaks to client
    headers = {
        "Content-Type": "application/json",
        "x-session-id": f"anon:{uuid.uuid4()}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Origin": "https://vetted.ai",
        "Accept": "application/x-ndjson"
    }
    
    payload = {
        "queries": {
            "researchProductComparison": {
                qid: {
                    "localization": "IN",
                    "context": f"Synthesize a professional purchase advisory for: {q}. Evaluate sentiment from Reddit, EWG safety, and expert reviews."
                }
            }
        }
    }

    try:
        with requests.post(url, json=payload, headers=headers, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    yield f"data: {line.decode('utf-8')}\\n\\n"
    except:
        yield f"data: {json.dumps({'error': 'Intelligence Link Severed'})}\\n\\n"

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/v1/analyze')
def api():
    q = request.args.get('q', '')
    return Response(stream_with_context(server_intelligence(q)), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
