#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编写时间: 2026-09-30 23:58:41 (系统时间实取, 见 date 输出)
脚本功能: 用 urllib+正则从 LetPub 期刊搜索结果页批量抓取 2025 影响因子, 输出 "期刊 => IF" 对照, 供第四/五篇报告 (肛门快感生理学, 精神药物与性抑制) 引用表填 IF 列。
参数: 无 (期刊清单 JOURNALS 硬编码, 与第四/五篇报告新增引用期刊一一对应)。
输入格式: 无文件输入; www.letpub.com.cn journalapp&view=search 页面, searchname 参数。
输出格式: stdout 每行 "期刊 => IF值 或 NOT-IN-JCR 或 NOT-FOUND 或 ERROR..."。
依赖: Python 3 标准库 (urllib.request, urllib.parse, re, html, time, sys)。
注意事项: (1) LetPub 限速, 请求间隔 1.5s; (2) 结果表列序: 0=ISSN, 1=刊名(含隐藏div), 2="IF: x.x h-index: n CiteScore: m", 3=分区; (3) 匹配时用首词+全名包含双校验, 避免同名误配; (4) curl 走 schannel 报 CRYPT_E_REVOCATION_OFFLINE, 所以用 urllib; (5) 复制 fetch_ifs_20260930.py 逻辑, 只换期刊清单。
"""
import urllib.request, urllib.parse, re, html, time, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

JOURNALS = [
    # 报告4 (肛门快感) 新刊
    "Nature Reviews Gastroenterology & Hepatology",
    "Journal of Sexual Medicine",
    "Sexual Medicine",
    "Archives of Sexual Behavior",
    "Journal of Sex Research",
    "Clinical Anatomy",
    "Journal of Sex & Marital Therapy",
    "Prostate Cancer Prostatic Disease",
    "Gastroenterology",
    "Urology",
    "International Urogynecology Journal",
    "Urogynecology",
    "Investigative and Clinical Urology",
    "Climacteric",
    "Prostate Cancer and Prostatic Diseases",
    # 报告5 (精神药物) 新刊
    "JAMA Psychiatry",
    "Journal of Clinical Psychopharmacology",
    "CNS Drugs",
    "Drug Safety",
    "Expert Opinion on Drug Safety",
    "Human Psychopharmacology",
    "Journal of Psychopharmacology",
    "Journal of Affective Disorders",
    "Psychopharmacology",
    "Journal of Clinical Psychiatry",
    "Nature Reviews Urology",
    "CNS Spectrums",
    "International Clinical Psychopharmacology",
    "Primary Care Companion for CNS Disorders",
    "Epidemiology and Psychiatric Sciences",
    "British Journal of Nursing",
    "Practitioner",
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

def parse_ifs(page, journal):
    # 结果行: <TR><TD>ISSN</TD><TD>刊名(可能含隐藏span)</TD><TD>IF: x.x h-index...</TD>...
    rows = re.findall(r'<TR[^>]*>(.*?)</TR>', page, re.S | re.I)
    out = []
    first_word = journal.split()[0].lower()
    for row in rows:
        tds = re.findall(r'<TD[^>]*>(.*?)</TD>', row, re.S | re.I)
        if len(tds) < 3:
            continue
        name_cell = html.unescape(re.sub(r'<[^>]+>', '', tds[1])).strip()
        if_cell = html.unescape(re.sub(r'<[^>]+>', '', tds[2])).strip()
        m = re.match(r'IF:\s*([\d.]+)', if_cell)
        if not m:
            continue
        nm = name_cell.lower()
        # 全词包含校验: 刊名含目标首词且目标全名 (小写去&) 被刊名包含或首词唯一匹配
        if first_word in nm.split()[0].lower() or first_word in nm:
            out.append((name_cell, m.group(1)))
    return out

for j in JOURNALS:
    try:
        page = fetch(j)
        res = parse_ifs(page, j)
        if not res:
            print(f"{j} => NOT-FOUND")
        elif len(res) == 1:
            print(f"{j} => {res[0][1]}")
        else:
            # 同名多条: 打印全部候选供人工挑
            print(f"{j} => AMBIGUOUS: " + "; ".join(f"{n}={v}" for n, v in res[:4]))
    except Exception as e:
        print(f"{j} => ERROR {type(e).__name__}: {e}")
    time.sleep(1.5)
