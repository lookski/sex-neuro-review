#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编写时间: 2026-10-01 02:15:30 (系统时间实取, 见 date 输出)
脚本功能: 回读审计: 经 18964 代理隧道从 GitHub raw 拉取刚推送的 3 个文件, 与本地副本做 SHA256 比对, 输出逐文件 PASS/FAIL。
参数: 无 (文件清单硬编码: 报告4, 报告5, README.md)。
输入格式: GitHub raw URL (urllib, 经 http://127.0.0.1:18964 代理) + 本地同名文件。
输出格式: stdout 每文件一行 "PASS/FAIL sha16_local sha16_remote"。
依赖: Python 3 标准库 (urllib.request, hashlib, sys)。
注意事项: (1) raw.githubusercontent.com 未被隧道 REMOTE 硬编码覆盖时会直连 host, 本次推送已验证隧道对 github.com 域名按 REMOTE 转发, raw 域走相同逻辑; (2) 失败重试 2 次。
"""
import urllib.request, hashlib, sys, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

FILES = [
    ("文献调研_接受方肛门快感生理学_20261001.md", "audit_r4.md"),
    ("文献调研_精神药物与性功能抑制_20261001.md", "audit_r5.md"),
    ("README.md", "audit_readme.md"),
]
PROXY = {'https': 'http://127.0.0.1:18964', 'http': 'http://127.0.0.1:18964'}
opener = urllib.request.build_opener(urllib.request.ProxyHandler(PROXY))

def fetch_raw(fname_local, tries=3):
    from urllib.parse import quote
    url = f"https://raw.githubusercontent.com/lookski/sex-neuro-review/main/{quote(fname_local)}"
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'audit'})
            with opener.open(req, timeout=25) as r:
                return r.read()
        except Exception as e:
            if t == tries - 1:
                raise
            time.sleep(3)

ok = 0
for local, tmp in FILES:
    data = fetch_raw(local)
    open(tmp, 'wb').write(data)
    h_remote = hashlib.sha256(data).hexdigest()[:16]
    h_local = hashlib.sha256(open(local, 'rb').read()).hexdigest()[:16]
    status = "PASS" if h_local == h_remote else "FAIL"
    ok += h_local == h_remote
    print(f"{status} {local} local={h_local} remote={h_remote}")
print(f"== {ok}/{len(FILES)} PASS ==")
