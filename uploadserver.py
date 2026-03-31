#!/usr/bin/env python3
import http.server, sys, os, email.parser, json

UPLOAD_DIR = os.environ.get('UPLOAD_DIR', os.path.expanduser('~/Downloads'))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

UPLOAD_PAGE = b'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, user-scalable=no">
<meta name="color-scheme" content="light dark">
<title>Upload</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#f4f5f7;--card:#fff;--border:#d0d5dd;--border-active:#6366f1;
  --text:#1a1a2e;--sub:#6b7280;--accent:#6366f1;--accent-hover:#4f46e5;
  --success:#10b981;--error:#ef4444;--radius:12px;--file-bg:#f9fafb}
@media(prefers-color-scheme:dark){:root{--bg:#111114;--card:#1c1c22;
  --border:#2e2e38;--border-active:#818cf8;--text:#e4e4e7;--sub:#9ca3af;
  --accent:#818cf8;--accent-hover:#6366f1;--success:#34d399;--error:#f87171;
  --file-bg:#1c1c22}}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  background:var(--bg);color:var(--text);min-height:100dvh;display:flex;
  align-items:center;justify-content:center;padding:1rem}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);
  padding:2rem;width:100%;max-width:480px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
h1{font-size:1.25rem;font-weight:600;margin-bottom:.25rem}
.sub{color:var(--sub);font-size:.85rem;margin-bottom:1.5rem}
.drop{border:2px dashed var(--border);border-radius:var(--radius);padding:2.5rem 1rem;
  text-align:center;cursor:pointer;transition:border-color .2s,background .2s}
.drop:hover,.drop.over{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 5%,transparent)}
.drop-icon{font-size:2rem;margin-bottom:.5rem;display:block;opacity:.5}
.drop p{color:var(--sub);font-size:.9rem}
.drop p span{color:var(--accent);text-decoration:underline;cursor:pointer}
input[type=file]{display:none}
.file-list{margin-top:1rem;display:flex;flex-direction:column;gap:.5rem}
.file-item{display:flex;align-items:center;gap:.75rem;padding:.6rem .75rem;
  background:var(--file-bg);border:1px solid var(--border);border-radius:8px;font-size:.85rem}
.file-item .name{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.file-item .size{color:var(--sub);font-size:.75rem;white-space:nowrap}
.file-item .remove{background:none;border:none;color:var(--sub);cursor:pointer;
  font-size:1.1rem;padding:0 .25rem;line-height:1}
.file-item .remove:hover{color:var(--error)}
.bar-wrap{height:4px;background:var(--border);border-radius:2px;overflow:hidden;
  margin-top:.35rem;display:none}
.bar-wrap .bar{height:100%;width:0;background:var(--accent);border-radius:2px;
  transition:width .15s}
.btn{display:block;width:100%;margin-top:1.25rem;padding:.7rem;border:none;
  border-radius:8px;background:var(--accent);color:#fff;font-size:.95rem;
  font-weight:500;cursor:pointer;transition:background .2s}
.btn:hover{background:var(--accent-hover)}
.btn:disabled{opacity:.5;cursor:not-allowed}
.status{margin-top:.75rem;text-align:center;font-size:.85rem;min-height:1.25rem}
.status.ok{color:var(--success)}.status.err{color:var(--error)}
.toast-wrap{position:fixed;top:1rem;left:50%;transform:translateX(-50%);z-index:99;
  display:flex;flex-direction:column;gap:.5rem;pointer-events:none;width:100%;max-width:420px;padding:0 1rem}
.toast{pointer-events:auto;display:flex;align-items:center;gap:.75rem;padding:.85rem 1rem;
  border-radius:10px;font-size:.9rem;font-weight:500;box-shadow:0 4px 16px rgba(0,0,0,.12);
  animation:slideIn .3s ease,fadeOut .4s ease 3.6s forwards}
.toast .icon{font-size:1.3rem;flex-shrink:0}
.toast .msg{flex:1}
.toast-ok{background:color-mix(in srgb,var(--success) 12%,var(--card));border:1px solid var(--success);color:var(--success)}
.toast-err{background:color-mix(in srgb,var(--error) 12%,var(--card));border:1px solid var(--error);color:var(--error)}
@keyframes slideIn{from{opacity:0;transform:translateY(-1rem)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeOut{to{opacity:0;transform:translateY(-1rem)}}
.file-item.done{border-color:var(--success);background:color-mix(in srgb,var(--success) 6%,var(--file-bg))}
.file-item.fail{border-color:var(--error);background:color-mix(in srgb,var(--error) 6%,var(--file-bg))}
</style>
</head>
<body>
<div class="card">
  <h1>Upload Files</h1>
  <p class="sub">Files are saved to the server\'s Downloads folder</p>

  <div class="drop" id="drop">
    <span class="drop-icon">&#8682;</span>
    <p>Drop files here or <span id="browse">browse</span></p>
  </div>
  <input type="file" id="input" multiple>

  <div class="file-list" id="list"></div>

  <button class="btn" id="btn" disabled>Upload</button>
  <div class="status" id="status"></div>
</div>
<div class="toast-wrap" id="toasts"></div>

<script>
const drop=document.getElementById("drop"),input=document.getElementById("input"),
  list=document.getElementById("list"),btn=document.getElementById("btn"),
  status=document.getElementById("status"),toasts=document.getElementById("toasts");
let files=[];

function toast(ok,msg){
  const t=document.createElement("div");
  t.className="toast "+(ok?"toast-ok":"toast-err");
  t.innerHTML='<span class="icon">'+(ok?"&#10003;":"&#10007;")+'</span><span class="msg">'+msg+"</span>";
  toasts.appendChild(t);
  setTimeout(()=>t.remove(),4000);
}

function render(){
  list.innerHTML="";
  files.forEach((f,i)=>{
    const d=document.createElement("div");d.className="file-item";
    const sz=f.size<1024?f.size+" B":f.size<1048576?(f.size/1024).toFixed(1)+" KB":(f.size/1048576).toFixed(1)+" MB";
    d.innerHTML='<span class="name">'+f.name+'</span><span class="size">'+sz+'</span><button class="remove" data-i="'+i+'">&times;</button><div class="bar-wrap"><div class="bar"></div></div>';
    d.querySelector(".remove").onclick=()=>{files.splice(i,1);render()};
    list.appendChild(d)});
  btn.disabled=!files.length;
  status.textContent="";status.className="status";
}

function addFiles(fl){
  for(const f of fl){if(!files.some(x=>x.name===f.name&&x.size===f.size))files.push(f)}
  render();
}

drop.addEventListener("dragover",e=>{e.preventDefault();drop.classList.add("over")});
drop.addEventListener("dragleave",()=>drop.classList.remove("over"));
drop.addEventListener("drop",e=>{e.preventDefault();drop.classList.remove("over");addFiles(e.dataTransfer.files)});
drop.addEventListener("click",()=>input.click());
input.addEventListener("change",()=>{addFiles(input.files);input.value=""});

btn.addEventListener("click",()=>{
  if(!files.length)return;
  const fd=new FormData();
  files.forEach(f=>fd.append("files",f));
  const xhr=new XMLHttpRequest();
  xhr.open("POST","/");
  xhr.timeout=3600000;

  const bars=list.querySelectorAll(".bar-wrap");
  bars.forEach(b=>b.style.display="block");

  xhr.upload.onprogress=e=>{
    if(!e.lengthComputable)return;
    const pct=Math.round(100*e.loaded/e.total);
    bars.forEach(b=>b.querySelector(".bar").style.width=pct+"%");
    status.textContent=pct<100?pct+"% uploaded":"Saving...";
    status.className="status";
  };

  xhr.onreadystatechange=()=>{
    if(xhr.readyState!==4)return;
    const items=list.querySelectorAll(".file-item");
    let res;try{res=JSON.parse(xhr.responseText)}catch(e){res=null}
    if(res&&res.ok){
      const names=res.files;
      items.forEach(el=>el.classList.add("done"));
      toast(true,names.length===1?names[0]+" uploaded":names.length+" files uploaded");
      status.textContent="";status.className="status";
      setTimeout(()=>{files=[];render()},1200);
    }else{
      const msg=res&&res.error?res.error:"Upload failed ("+xhr.status+")";
      items.forEach(el=>el.classList.add("fail"));
      toast(false,msg);
      status.textContent="";status.className="status";
    }
    btn.disabled=!files.length;
  };

  xhr.onerror=()=>{
    list.querySelectorAll(".file-item").forEach(el=>el.classList.add("fail"));
    toast(false,"Connection failed");btn.disabled=!files.length;
  };
  xhr.ontimeout=()=>{
    list.querySelectorAll(".file-item").forEach(el=>el.classList.add("fail"));
    toast(false,"Upload timed out");btn.disabled=!files.length;
  };

  btn.disabled=true;
  xhr.send(fd);
});
</script>
</body>
</html>
'''

def parse_multipart(rfile, content_type, content_length):
    boundary = None
    for part in content_type.split(';'):
        part = part.strip()
        if part.startswith('boundary='):
            boundary = part[len('boundary='):]
            break
    if not boundary:
        return []

    body = rfile.read(content_length)
    sep = ('--' + boundary).encode()
    parts = body.split(sep)
    files = []

    for part in parts:
        if part in (b'', b'--', b'--\r\n', b'\r\n'):
            continue
        if not part.startswith(b'\r\n'):
            continue
        part = part[2:]  # strip leading \r\n
        header_end = part.find(b'\r\n\r\n')
        if header_end == -1:
            continue
        header_bytes = part[:header_end]
        data = part[header_end + 4:]
        if data.endswith(b'\r\n'):
            data = data[:-2]

        headers = email.parser.Parser().parsestr(header_bytes.decode('utf-8', errors='replace'))
        disposition = headers.get('Content-Disposition', '')
        filename = None
        for param in disposition.split(';'):
            param = param.strip()
            if param.startswith('filename='):
                filename = param[len('filename='):]
                filename = filename.strip('"')
                break

        if filename:
            files.append((filename, data))

    return files

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(UPLOAD_PAGE)))
        self.end_headers()
        self.wfile.write(UPLOAD_PAGE)

    def do_POST(self):
        content_type = self.headers.get('Content-Type', '')
        if 'multipart/form-data' not in content_type:
            self.send_error(400, 'Expected multipart/form-data')
            return

        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_error(400, 'No content')
            return

        files = parse_multipart(self.rfile, content_type, content_length)
        saved = []
        for filename, data in files:
            name = os.path.basename(filename)
            if not name:
                continue
            dest = os.path.join(UPLOAD_DIR, name)
            if os.path.exists(dest):
                base, ext = os.path.splitext(dest)
                i = 1
                while os.path.exists(dest):
                    dest = f'{base} ({i}){ext}'
                    i += 1
            with open(dest, 'wb') as f:
                f.write(data)
            saved.append(name)
            self.log_message('Saved %s -> %s', name, dest)

        if saved:
            body = json.dumps({'ok': True, 'files': saved}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            body = json.dumps({'ok': False, 'error': 'No files received'}).encode()
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    do_HEAD = do_GET
    do_PUT = do_POST

if __name__ == '__main__':
    server = http.server.ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print(f'Upload server on http://0.0.0.0:{PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down.')
        server.server_close()
