#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编写时间: 2026-10-01 02:05:00 (系统时间实取, 见 date 输出)
脚本功能: 本地代理诊断: (1) 探测 Clash/mihomo 外部控制 API 端口并读取 version/proxies;
          (2) 经指定代理端口对目标 URL 做 GET 测试, 输出状态码与耗时。
参数: 无 (诊断目标硬编码: github.com / api.github.com / gstatic 204)。
输入格式: 无。
输出格式: stdout 文本 (端口探测结果 + 每目标一行 "code 耗时s")。
依赖: Python 3 标准库 (urllib.request, socket, sys)。
注意事项: (1) 7897=verge-mihomo 混合端口, 18964=未知进程 (PID 17288) 监听;
          (2) Clash API 常见端口 9090/9097 逐一试; (3) 只读诊断, 不改配置。
"""
import urllib.request, socket, sys, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def try_port(port, path="/version", timeout=3):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as r:
            return r.status, r.read(200).decode('utf-8', errors='replace')
    except Exception as e:
        return None, f"{type(e).__name__}"

def proxy_get(port, url, timeout=8):
    proxy = urllib.request.ProxyHandler({'http': f'http://127.0.0.1:{port}', 'https': f'http://127.0.0.1:{port}'})
    opener = urllib.request.build_opener(proxy)
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/8.2 diag'})
        with opener.open(req, timeout=timeout) as r:
            return r.status, time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, time.time() - t0
    except Exception as e:
        return f"ERR:{type(e).__name__}", time.time() - t0

# 1) Clash API 探测
print("== Clash external-controller 探测 ==")
for p in (9090, 9097, 33221, 9095, 62823):
    st, body = try_port(p)
    if st:
        print(f"  {p}: HTTP {st} {body}")

# 2) 两个代理端口对三目标的测试
print("== 代理 GET 测试 ==")
targets = [
    "http://www.gstatic.com/generate_204",
    "https://api.github.com/zen",
    "https://github.com/manifest.json",
]
for port in (7897, 18964):
    print(f"-- 经 127.0.0.1:{port} --")
    for u in targets:
        code, dt = proxy_get(port, u)
        print(f"  {code} {dt:.2f}s  {u}")
