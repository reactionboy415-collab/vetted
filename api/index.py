import os
import uuid
import requests
import traceback
from flask import Flask, Response, render_template_string, request, jsonify

app = Flask(__name__)

# Live progress messages
PROGRESS_MSGS = [
    "🔄 Initializing Vetted.ai Deep Engine...",
    "📡 Querying India market data...",
    "🧠 AI analyzing reviews & sentiment...",
    "💰 Price comparison across sellers...",
    "✨ Extracting pros/cons & recommendations...",
    "✅ Deep scan complete!"
]

# EMBEDDED HTML (minified for Vercel size limit <250MB)[web:20]
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en" class="dark"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Shop Scene AI</title><script src="https://cdn.tailwindcss.com"></script><script>tailwind.config={darkMode:"class",theme:{extend:{colors:{primary:"#8b5cf6"}}}}</script></head><body class="bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 min-h-screen text-white">
<div class="container mx-auto px-4 py-8 max-w-4xl">
<header class="text-center mb-12"><h1 class="text-5xl md:text-6xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-indigo-400 bg-clip-text text-transparent mb-4 animate-pulse">Shop Scene AI</h1><p class="text-xl text-slate-300 max-w-2xl mx-auto">AI Deep Research • India Deals • Live Streaming</p></header>
<div class="bg-white/5 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-white/20">
<div class="flex flex-col lg:flex-row gap-4 mb-8"><input id="productInput" placeholder="iPhone 15, PS5..." class="flex-1 bg-white/10 backdrop-blur-md rounded-3xl px-6 py-5 text-xl border-2 border-white/20 focus:border-purple-400 focus:outline-none text-white placeholder-slate-400"><button id="scanBtn" class="bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 px-10 py-5 rounded-3xl font-bold text-xl shadow-2xl hover:shadow-3xl transition-all">🔥 Deep Scan</button></div>
<div id="status" class="text-center py-12 text-slate-400 hidden"><div class="text-2xl mb-4">Ready...</div><div class="w-24 h-24 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mx-auto"></div></div>
<div id="results" class="space-y-3 max-h-96 overflow-y-auto bg-black/30 backdrop-blur-md rounded-3xl p-6 border border-white/20 hidden"></div>
<div id="debug" class="mt-8 p-6 bg-red-900/50 rounded-2xl border-2 border-red-500/50 text-red-200 hidden"><h3 class="font-bold mb-2">Debug:</h3><pre id="debugText"></pre></div>
</div><footer class="mt-20 text-center text-slate-500 text-sm">Powered by Vetted.ai • Responsive</footer></div>
<script>
const scanBtn=document.getElementById('scanBtn'),productInput=document.getElementById('productInput'),status=document.getElementById('status'),results=document.getElementById('results'),debug=document.getElementById('debug'),debugText=document.getElementById('debugText');
scanBtn.onclick=async()=>{const product=productInput.value.trim();if(!product)return;status.classList.remove('hidden');results.classList.add('hidden');debug.classList.add('hidden');scanBtn.disabled=true;scanBtn.innerHTML='<span class="flex items-center gap-2"><div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>Scanning...</span>';try{const res=await fetch('/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product})});const reader=res.body.getReader(),decoder=new TextDecoder();results.innerHTML='<div class="p-4 text-purple-300">Receiving data...</div>';results.classList.remove('hidden');while(true){const{done,value}=await reader.read();if(done)break;const chunk=decoder.decode(value,{stream:true}),lines=chunk.split(/\
data: /).filter(Boolean);for(const line of lines){if(line.trim()){const data=line.trim(),chunkEl=document.createElement('div');chunkEl.className='p-4 bg-white/5 rounded-2xl border-l-4 border-purple-400';chunkEl.innerHTML=`<pre class="whitespace-pre-wrap text-sm">${escapeHtml(data)}</pre>`;results.appendChild(chunkEl)}}results.scrollTop=results.scrollHeight}status.classList.add('hidden');scanBtn.innerHTML='✨ Complete!';}catch(e){debugText.textContent=e.message;debug.classList.remove('hidden');scanBtn.innerHTML='🔥 Retry';}scanBtn.disabled=false};
productInput.onkeypress=e=>{if(e.key==='Enter')scanBtn.click()};function escapeHtml(t){const m={'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#039;"};return t.replace(/[&<>"']/g,c=>m[c])};productInput.focus();
</script></body></html>'''

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
        try:
            # Live progress
            def generate():
                for msg in PROGRESS_MSGS:
                    yield f"data: {msg}

"
                    import time; time.sleep(0.5)  # Simulate thinking

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
                resp = requests.post(url, json=payload, headers=self.headers, stream=True, timeout=120)
                for chunk in resp.iter_lines():
                    if chunk:
                        decoded = chunk.decode('utf-8').strip()
                        if decoded: yield f"data: {decoded}

"
            return generate()
        except Exception as e:
            def error():
                yield f"data: ❌ Error: {str(e)}

"
            return error()

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['POST'])
def scan():
    try:
        product = request.json.get('product', '').strip()
        if not product:
            return jsonify({'error': 'Product required'}), 400
        generator = VettedDeepEngine().fire_full_research(product)
        return Response(generator(), mimetype='text/plain')
    except Exception:
        app.logger.error(traceback.format_exc())
        return "Internal Error", 500

# Vercel requires this handler
@app.route('/api/index.py', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD'])
def vercel_handler():
    return index() if request.method == 'GET' else scan()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
