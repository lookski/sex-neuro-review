#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编写时间: 2026-09-30 10:31:12 (系统时间实取, 见 date 输出 10:29 区间)
脚本功能: 用 urllib+正则从 LetPub 期刊搜索结果页批量抓取 2025 影响因子, 输出 "期刊 => IF" 对照, 供第三篇报告引用表填 IF 列。
参数: 无 (期刊清单 JOURNALS 硬编码, 与第三篇报告新增引用期刊一一对应)。
输入格式: 无文件输入; www.letpub.com.cn journalapp&view=search 页面, searchname 参数。
输出格式: stdout 每行 "期刊 => IF值 或 NOT-IN-JCR 或 NOT-FOUND 或 ERROR..."。
依赖: Python 3 标准库 (urllib.request, urllib.parse, re, html, time, sys)。
注意事项: (1) LetPub 限速, 请求间隔 1.5s; (2) 结果表列序: 0=ISSN, 1=刊名(含隐藏div), 2="IF: x.x h-index: n CiteScore: m", 3=分区; (3) 匹配时用首词+全名包含双校验, 避免同名误配; (4) curl 走 schannel 报 CRYPT_E_REVOCATION_OFFLINE, 所以用 urllib; (5) 2026-09-30 实测该页面结构可解析。
"""
import urllib.request, urllib.parse, re, html, time, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

JOURNALS = [
    "Translational Psychiatry",
    "Sexual Medicine",
    "International Journal of Impotence Research",
    "Spinal Cord",
    "Journal of Neurotrauma",
    "Expert Opinion on Pharmacotherapy",
    "Cochrane Database of Systematic Reviews",
    "Journals of Gerontology Series A",
    "Andrology",
    "Neurourology and Urodynamics",
    "Clinical Therapeutics",
    "Psychoneuroendocrinology",
    "Journal of Experimental Zoology Part B",
    "Twin Research and Human Genetics",
    "Maturitas",
    "BMC Women's Health",
    "Gynecological Endocrinology",
    "Chinese Medical Journal",
    "Supportive Care in Cancer",
    "Journal of Sexual Medicine",
]

def fetch(name):
    q = urllib.parse.quote(name)
    url = (f'https://www.letpub.com.cn/index.php?page=journalapp&view=search'
           f'&searchname={q}&searchkind=1&searchjingzhun=1')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    data = urllib.request.urlopen(req, timeout=30).read()
    for enc in ('utf-8', 'gbk'):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode('utf-8', errors='replace')

def clean(c):
    c = re.sub(r'<[^>]+>', ' ', c)
    c = html.unescape(c)
    return re.sub(r'\s+', ' ', c).strip()

def extract(h, name):
    i = h.find('journallisttable')
    if i < 0:
        return None, None
    seg = h[i:]
    trs = re.findall(r'(<TR.*?</TR>)', seg, re.S | re.I)
    words = [w.lower() for w in re.split(r'[^A-Za-z0-9]+', name) if w]
    for tr in trs:
        cells = [clean(c) for c in re.findall(r'<TD.*?</TD>', tr, re.S | re.I)]
        if len(cells) < 3:
            continue
        # 刊名单元格里通常是大写全名+重复, 归一小写比较
        cell_name = cells[1].upper()
        # 全名所有词都出现才算命中
        if all(w.upper() in cell_name for w in words[:4]):
            m = re.search(r'IF[:：]\s*([\d.]+)', cells[2])
            return cells[1][:60], (m.group(1) if m else None)
    return None, None

for j in JOURNALS:
    try:
        htm = fetch(j)
        cname, ifv = extract(htm, j)
        if cname is None:
            print(f'{j} => NOT-FOUND')
        elif ifv is None:
            print(f'{j} => NOT-IN-JCR ({cname})')
        else:
            print(f'{j} => {ifv} ({cname})')
    except Exception as e:
        print(f'{j} => ERROR {type(e).__name__} {e}')
    time.sleep(1.5)
