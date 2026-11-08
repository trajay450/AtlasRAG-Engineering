"""Localhost-only by default; deliberately no authentication or public hosting claims."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
import json
from .store import Store
from .retrieval import retrieve
from .answer import answer

HTML = """<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>AtlasRAG</title><style>body{font:16px system-ui;background:#101b2b;color:#e7eef8;max-width:850px;margin:50px auto;padding:16px}input,button{font:inherit;padding:12px;border-radius:8px;border:0}input{width:65%}button{background:#4ba3ff;cursor:pointer}article{background:#1c2c43;padding:16px;margin:12px 0;border-radius:12px}small{color:#aabbd0}pre{white-space:pre-wrap}</style><h1>AtlasRAG · Evidence Explorer</h1><p>Local-first retrieval with traceable citations. No LLM is used.</p><input id='q' placeholder='Ask about indexed documents'><button onclick='go()'>Search</button><div id='out'></div><script>async function go(){let q=document.getElementById('q').value;let out=document.getElementById('out');out.textContent='Searching...';try{let r=await fetch('/api/answer?q='+encodeURIComponent(q));let data=await r.json();out.textContent='';let p=document.createElement('p');p.textContent=data.answer;out.appendChild(p);for(let e of data.evidence||[]){let a=document.createElement('article');let h=document.createElement('strong');h.textContent=e.title+' · '+e.citation;a.appendChild(h);let t=document.createElement('pre');t.textContent=e.claim;a.appendChild(t);out.appendChild(a)}}catch(e){out.textContent='Request failed: '+e.message}}</script></html>"""

def serve(db_path,host="127.0.0.1",port=8765):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            u=urlparse(self.path)
            if u.path=="/":
                data=HTML.encode();typ="text/html; charset=utf-8";code=200
            elif u.path in ("/api/answer","/api/search"):
                params=parse_qs(u.query)
                q=params.get("q",[""])[0]
                try:
                    with_db=Store(db_path)
                    try: result=answer(with_db,q) if u.path.endswith("answer") else retrieve(with_db,q)
                    finally: with_db.close()
                    code=200
                except ValueError as exc:result={"error":str(exc)};code=400
                data=json.dumps(result).encode();typ="application/json"
            else:data=b"Not found";typ="text/plain";code=404
            self.send_response(code);self.send_header("Content-Type",typ);self.send_header("Content-Length",str(len(data)));self.send_header("X-Content-Type-Options","nosniff");self.end_headers();self.wfile.write(data)
    httpd=ThreadingHTTPServer((host,port),Handler)
    print(f"Open http://{host}:{port} (local development only)")
    try:httpd.serve_forever()
    except KeyboardInterrupt:pass
    finally:httpd.server_close()
