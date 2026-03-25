import os
import uuid
import requests
from flask import Flask, Response, render_template_string, request, jsonify

app = Flask(__name__)

# EMBEDDED RESPONSIVE HTML + CSS + JS (Tailwind CDN)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shop Scene AI - Deep Product Research</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: { extend: { colors: { primary: '#8b5cf6' } } }
        }
    </script>
</head>
<body class="bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 min-h-screen text-white overflow-x-hidden">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <header class="text-center mb-12">
            <h1 class="text-5xl md:text-6xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-indigo-400 bg-clip-text text-transparent mb-4 animate-pulse">
                Shop Scene AI
            </h1>
            <p class="text-xl text-slate-300 max-w-2xl mx-auto">AI-Powered Deep Research • Live India Deals • Reviews • Pros/Cons</p>
        </header>

        <div class="bg-white/5 backdrop-blur-xl rounded-3xl p-8 md:p-12 shadow-2xl border border-white/20 hover:border-white/40 transition-all duration-300">
            <div class="flex flex-col lg:flex-row gap-4 mb-8">
                <input id="productInput" type="text" placeholder="🛒 Enter product (e.g., iPhone 15, PS5, Samsung Galaxy)" 
                       class="flex-1 bg-white/10 backdrop-blur-md rounded-3xl px-6 py-5 text-xl md:text-2xl border-2 border-white/20 focus:border-purple-400 focus:outline-none text-white placeholder-slate-400 transition-all duration-300 hover:border-white/30">
                <button id="scanBtn" class="bg-gradient-to-r from-purple-500 via-pink-500 to-indigo-500 hover:from-purple-600 hover:via-pink-600 hover:to-indigo-600 px-10 py-5 rounded-3xl font-bold text-xl shadow-2xl hover:shadow-3xl transform hover:-translate-y-1 transition-all duration-300 whitespace-nowrap">
                    🔥 Deep Scan Now
                </button>
            </div>

            <div id="status" class="text-center py-12 text-slate-400 hidden">
                <div class="text-2xl mb-4">Ready for Deep Analysis...</div>
                <div class="w-24 h-24 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mx-auto"></div>
            </div>

            <div id="results" class="space-y-3 max-h-96 md:max-h-[500px] overflow-y-auto bg-black/30 backdrop-blur-md rounded-3xl p-6 md:p-8 border border-white/20 hidden scroll-smooth">
                <!-- Live streaming chunks appear here -->
            </div>

            <div id="debug" class="mt-8 p-6 bg-red-900/50 rounded-2xl border-2 border-red-500/50 text-red-200 hidden">
                <h3 class="font-bold mb-2">⚠️ Debug Info:</h3>
                <pre id="debugText" class="text-sm overflow-auto max-h-40"></pre>
            </div>
        </div>

        <footer class="mt-20 text-center text-slate-500 text-sm space-y-2">
            <p>🚀 Built for Indian Shoppers • Powered by Vetted.ai Deep Engine</p>
            <p>📱 Fully Responsive • Live Streaming • No Login Needed</p>
        </footer>
    </div>

    <script>
        const scanBtn = document.getElementById('scanBtn');
        const productInput = document.getElementById('productInput');
        const status = document.getElementById('status');
        const results = document.getElementById('results');
        const debug = document.getElementById('debug');
        const debugText = document.getElementById('debugText');

        scanBtn.onclick = async () => {
            const product = productInput.value.trim();
            if (!product) {
                productInput.focus(); return;
            }

            // UI Reset
            status.classList.remove('hidden');
            results.classList.add('hidden');
            debug.classList.add('hidden');
            scanBtn.disabled = true;
            scanBtn.innerHTML = `
                <span class="flex items-center gap-2">
                    <div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Analyzing Deep...
                </span>
            `;

            status.innerHTML = `
                <div class="text-3xl mb-6 animate-pulse">🔥 Initializing Vetted.ai Deep Scan</div>
                <div class="text-xl space-y-2">
                    <div>📡 Connecting to Research Engine...</div>
                    <div class="flex items-center gap-3 mt-4">
                        <div class="w-8 h-8 bg-green-500/20 rounded-xl animate-ping"></div>
                        <span>Live streaming incoming...</span>
                    </div>
                </div>
            `;

            try {
                const res = await fetch('/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product })
                });

                if (!res.ok) throw new Error('Scan failed');

                const reader = res.body.getReader();
                const decoder = new TextDecoder();
                results.innerHTML = '<div class="text-purple-300 text-center py-8">📦 Receiving deep analysis chunks...</div>';
                results.classList.remove('hidden');

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split(/
(?=data: )/).filter(Boolean);

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6).trim();
                            if (data) {
                                // Create styled result chunk
                                const chunkEl = document.createElement('div');
                                chunkEl.className = 'p-4 bg-white/5 backdrop-blur-sm rounded-2xl border-l-4 border-purple-400 hover:border-l-purple-300 transition-all shadow-sm';
                                chunkEl.innerHTML = `<pre class="whitespace-pre-wrap text-sm md:text-base">${escapeHtml(data)}</pre>`;
                                results.appendChild(chunkEl);
                            }
                        }
                    }
                    results.scrollTop = results.scrollHeight;
                }

                status.classList.add('hidden');
                scanBtn.innerHTML = '✨ Scan Complete! Ready for Next';
                scanBtn.classList.add('bg-green-500/80', 'hover:bg-green-600/80');
            } catch (e) {
                status.classList.add('hidden');
                debugText.textContent = `Error: ${e.message}

Tip: Check connection or try different product.`;
                debug.classList.remove('hidden');
                scanBtn.innerHTML = '🔥 Retry Deep Scan';
            } finally {
                scanBtn.disabled = false;
            }
        };

        // Enter key trigger
        productInput.onkeypress = (e) => { if (e.key === 'Enter') scanBtn.click(); };

        // HTML escape for safety
        function escapeHtml(text) {
            const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        // Auto-focus input
        productInput.focus();
    </script>
</body>
</html>
"""

class VettedDeepEngine:
    def __init__(self):
        self.session_id = f"anonymous:{uuid.uuid4()}"
        self.headers = {
            "Content-Type": "application/json",
            "x-session-id": self.session_id,
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; LAVA Blaze)",
            "Origin": "https://vetted.ai",
            "Referer": "https://vetted.ai/",
            "Accept": "application/x-ndjson, application/json"
        }

    def fire_full_research(self, topic):
        print(f"🔥 Vercel Scan: {topic}")  # Server log
        query_id = uuid.uuid4().hex[:16]
        url = "https://api.vetted.ai/queries"
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
            response = requests.post(url, json=payload, headers=self.headers, stream=True, timeout=120)
            def generate():
                yield "data: 🔄 Analyzing market data...

"
                yield "data: 🧠 Processing reviews & sentiment...

"
                yield "data: 💰 Calculating India pricing & value...

"
                full_content = ""
                for i, chunk in enumerate(response.iter_lines()):
                    if chunk:
                        decoded_chunk = chunk.decode('utf-8').strip()
                        if decoded_chunk:
                            full_content += decoded_chunk + "
"
                            yield f"data: {decoded_chunk}

"
                            if i > 50:  # Live feel
                                yield "data: ✨ Extracting key insights...

"
                yield "data: ✅ Deep scan complete!

"
            return True, generate()
        except Exception as e:
            def error_gen():
                yield f"data: ❌ Scan Error: {str(e)}

"
                yield "data: 💡 Try: Check internet or different product name

"
            return False, error_gen()

engine = VettedDeepEngine()

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['POST'])
def scan():
    product = request.json.get('product', '').strip()
    if not product:
        return jsonify({'error': 'Product required'}), 400
    
    success, generator = engine.fire_full_research(product)
    return Response(generator(), mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
