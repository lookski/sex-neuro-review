# -*- coding: utf-8 -*-
"""
编写时间: 2026-10-03 (系统时间实取)
脚本功能: (1) 报告1 表内 Sex Med IF 3.6 -> 2.4 并把脚注4 改为单条目实查口径说明;
              (2) 重写报告3 脚注1 (9 刊里 7 刊已补录, 仅 Clinics 与 Int J Gynaecol Obstet 保留 "—");
              (3) 报告3 表 #16 前追加 Ben Zion 一作更正说明。
          全部替换原子执行: 任一锚点未命中唯一一次即中止且不写盘。
输入: 两个 markdown 报告 (cwd)
输出: 原地修改 + 控制台明细
依赖: 无
备注: Sex Med 采用单条目值 2.4 的依据见第三篇脚注 2 ("以本轮 LetPub 单条目 2.4 为准"),
      报告1 原注 3.6 是按 "与 J Sex Med 同列" 推断得出, 属非直接读取, 故更正。
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

F1 = '文献调研_高潮差异与肛门快感原理_20260928.md'
F3 = '文献调研_高潮的个体差异_药物基因与进化_20260930.md'
SUP4 = '\u2074'
SUP1 = '\u00b9'

p1 = [
    ('| Sex Med (3.6)' + SUP4 + ' | 40463812 |', '| Sex Med (2.4)' + SUP4 + ' | 40463812 |'),
    ('LetPub \u4e0e J Sex Med \u540c\u5217 (IF 3.6 \u53e3\u5f84, \u5b9e\u67e5)\u3002',
     'LetPub \u72ec\u7acb\u5355\u6761\u76ee IF 2.4 (\u5b9e\u67e5)\u3002'
     '\u539f\u6ce8\u66fe\u6309 "\u4e0e J Sex Med \u540c\u5217" \u8bb0\u4e3a 3.6, \u8be5\u53e3\u5f84\u5c5e\u63a8\u65ad\u800c\u975e\u5355\u6761\u76ee\u76f4\u8bfb; '
     '2026-10-03 \u4f9d\u7b2c\u4e09\u7bc7\u811a\u6ce8' + SUP1 + ' \u660e\u786e\u7684\u4f18\u5148\u7ea7 '
     '(\u4ee5\u5355\u6761\u76ee 2.4 \u4e3a\u51c6) \u66f4\u6b63\u4e3a 2.4, \u4e0e\u7b2c\u56db\u7bc7\u4e00\u81f4\u3002'),
]

p3 = [
    ('> ' + SUP1 + ' \u672c\u8f6e LetPub \u672a\u6838\u5230\u8be5\u520a 2025 IF \u8bb0\u5f55 '
     '(Int J Clin Pract, Clinics, Int J Gynaecol Obstet, Curr Opin Urol, Mol Psychiatry, Eur Urol, '
     'J Neurosci Rural Pract, Int J Neurosci, JAMA Intern Med \u5747\u4e3a\u5b9e\u67e5\u672a\u4e2d\u6216\u672a\u5217\u5165\u68c0\u7d22), '
     '\u5b81\u7f3a\u52ff\u9519\u3002',
     '> ' + SUP1 + ' Clinics (Sao Paulo) \u4e0e Int J Gynaecol Obstet \u4e24\u520a\u7ecf LetPub '
     '\u540d\u79f0/ISSN \u901a\u9053\u591a\u6b21\u68c0\u7d22\u5747\u672a\u8fd4\u56de\u6761\u76ee, \u4fdd\u7559 "\u2014"; '
     '\u5176\u4f59\u5404\u520a IF \u5747\u5df2\u4e8e 2026-10-03 \u7531 LetPub \u5355\u520a\u5b9e\u67e5\u8865\u5f55 '
     '(Int J Clin Pract 2.0, Curr Opin Urol 2.3, Mol Psychiatry 10.4, Eur Urol 29.1, '
     'J Neurosci Rural Pract 1.3, Int J Neurosci 1.7, JAMA Intern Med 26.3)\u3002'
     '\u4e1a\u4e66\u4e0e\u975e JCR \u520a (Prog Brain Res, Lakartidningen, Handb Clin Neurol) '
     '\u5728 LetPub \u663e\u793a 0, \u4ee5 0* \u6807\u6ce8\u5e76\u52a0\u811a\u6ce8, \u4e0d\u731c\u6570\u3002'),
    ('| 16 | Ben Zion IZ, et al.',
     '| 16 | Ben Zion IZ, et al. <!-- \u4e00\u4f5c\u66f4\u6b63 2026-10-03: \u539f\u8bb0 "Lusher JM" '
     '\u7ecf efetch AU \u5b57\u6bb5\u6838\u5bf9\u4e3a\u9519\u8bef (\u8be5 PMID \u4e00\u4f5c\u5b9e\u4e3a Ben Zion IZ), '
     '\u6807\u9898\u4e5f\u7531\u7b80\u79f0\u6539\u4e3a\u6458\u8981\u539f\u6587 -->'),
]


def apply(path, pairs):
    s = open(path, encoding='utf-8').read()
    for i, (old, new) in enumerate(pairs, 1):
        n = s.count(old)
        if n != 1:
            print('  [ABORT]', path, '#' + str(i), 'hits', n, repr(old[:46]))
            sys.exit(1)
        s = s.replace(old, new, 1)
        print('  [OK', str(i) + ']', repr(old[:42]))
    open(path, 'w', encoding='utf-8', newline='\n').write(s)
    print('  [WRITE]', path)


print('=== 报告1: Sex Med 口径 ===')
apply(F1, p1)
print('=== 报告3: 脚注 + Ben Zion 注记 ===')
apply(F3, p3)
print('DONE')
