import json
import uuid
import requests
import os
from typing import Any

def handler(request):  # Vercel serverless format[web:25]
    try:
        print("🔥 Cold start OK - Shop Scene AI")  # Vercel log
        
        if request.path == '/scan':
            return handle_scan(request)
        else:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': get_html()
            }
    except Exception as e:
        print(f"🚨 ERROR: {str(e)}")
        print(str(e.__traceback__))  # Full stacktrace in logs
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'Server Error: {str(e)} - Check Vercel logs'
        }

def get_html():
    return '''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Shop Scene AI</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-gradient-to-br from-slate-900 to-purple-900 min-h-screen text-white p-8">
<div class="max-w-4xl mx-auto"><h1 class="text-5xl font-bold text-center mb-12 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">Shop Scene AI</h1>
<div class="bg-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20"><div class="flex flex-col md:flex-row gap-4 mb-8"><input id="product" placeholder="iPhone 15, PS5..." class="flex-1 p-4 rounded-2xl bg-white/20 text-xl border border-white/30 focus:border-purple-400"><button id="scan" class="bg-purple-600 hover:bg-purple-700 px-8 py-4 rounded-2xl font-bold text-lg">🔥 Deep Scan</button></div>
<div id="status" class="text-center py-12 hidden"><div class="text-2xl mb-4">🔄 Scanning...</div><div class="w-20 h-20 border-4 border-purple-500/30 border-t-purple-500 rounded-full mx-auto animate-spin"></div></div>
<div id="results" class="max-h-96 overflow-auto bg-black/20 p-6 rounded-2xl border border-white/20 hidden space-y-2"></div></div></div>
<script>
const btn=document.getElementById('scan'),input=document.getElementById('product'),status=document.getElementById('status'),results=document.getElementById('results');
btn.onclick=async()=>{
  const product=input.value.trim();if(!product)return;
  status.classList.remove('hidden');results.classList.add('hidden');btn.disabled=true;btn.textContent='⏳ Live...';
  try{
    const res=await fetch('/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product})});
    const reader=res.body.pipeThrough(new TextDecoderStream()),resultsDiv=document.getElementById('results');
    resultsDiv.innerHTML='<div class="p-4 bg-purple-900/50 rounded-xl">📡 Live stream starting...</div>';resultsDiv.classList.remove('hidden');
    for await(const chunk of reader){
      if(chunk.includes('data:')){
        const data=chunk.split('data:')[1]?.trim();if(data){const div=document.createElement('div');div.className='p-3 bg-white/10 rounded-xl';div.textContent=data;resultsDiv.appendChild(div);resultsDiv.scrollTop=resultsDiv.scrollHeight;}
      }
    }
  }catch(e){results.innerHTML=`<div class="p-4 bg-red-900/50 rounded-xl text-red-200">Error: ${e.message}</div>`;}
  status.classList.add('hidden');btn.disabled=false;btn.textContent='✅ Done! Scan Again';
};input.onkeypress=e=>{if(e.key==='Enter')btn.click()};input.focus();
</script></body></html>'''

def handle_scan(request):
    try:
        body = json.loads(request.body.decode())
        product = body.get('product', '').strip()
        if not product:
            return {'statusCode': 400, 'body': 'No product'}
        
        def stream():
            yield "🔄 Initializing Deep Engine
"
            yield "📡 Querying Vetted.ai IN data
"
            yield "🧠 Analyzing reviews...
"
            
            # Real API call
            session_id = f"anonymous:{uuid.uuid4()}"
            headers = {
                "Content-Type": "application/json",
                "x-session-id": session_id,
                "User-Agent": "Mozilla/5.0 (Linux; Android 12; LAVA Blaze)",
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
                            "context": f"I want to know if I should buy {product}. Analyze reviews, pros, cons, and value for money."
                        }
                    }
                }
            }
            
            resp = requests.post("https://api.vetted.ai/queries", json=payload, headers=headers, stream=True, timeout=120)
            for line in resp.iter_lines():
                if line:
                    decoded = line.decode('utf-8').strip()
                    if decoded: yield f"{decoded}
"
            yield "✅ Full analysis complete!
"
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain'},
            'body': stream()
        }
    except Exception as e:
        print(f"SCAN ERROR: {str(e)}")
        return {'statusCode': 500, 'body': f'Scan failed: {str(e)}'}

# Vercel auto-calls handler(request)
