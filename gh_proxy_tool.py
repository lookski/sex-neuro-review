import socket, threading, sys

LISTEN = ('127.0.0.1', 18964)
REMOTE = '140.82.121.6'   # github.com / api.github.com 当前可用 IP

def pipe(a, b):
    try:
        while True:
            d = a.recv(65536)
            if not d: break
            b.sendall(d)
    except OSError:
        pass
    finally:
        try: a.close()
        except: pass
        try: b.close()
        except: pass

def handle(c):
    try:
        c.settimeout(20)
        req = b''
        while b'\r\n\r\n' not in req:
            chunk = c.recv(4096)
            if not chunk: return
            req += chunk
        line = req.split(b'\r\n')[0].decode()
        method, target = line.split()[0], line.split()[1]
        if method != 'CONNECT':
            c.close(); return
        host = target.split(':')[0]
        port = int(target.split(':')[1]) if ':' in target else 443
        ip = REMOTE if (host == 'github.com' or host.endswith('.github.com') or host.endswith('githubusercontent.com')) else host
        up = socket.create_connection((ip, port), timeout=15)
        up.settimeout(None)
        c.sendall(b'HTTP/1.1 200 Connection established\r\n\r\n')
        t1 = threading.Thread(target=pipe, args=(c, up), daemon=True)
        t2 = threading.Thread(target=pipe, args=(up, c), daemon=True)
        t1.start(); t2.start(); t1.join(); t2.join()
    except Exception:
        try: c.close()
        except: pass

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(LISTEN); srv.listen(64)
print('proxy on', LISTEN, flush=True)
while True:
    conn, _ = srv.accept()
    threading.Thread(target=handle, args=(conn,), daemon=True).start()
