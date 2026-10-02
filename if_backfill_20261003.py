# -*- coding: utf-8 -*-
"""
编写时间: 2026-10-03 (系统时间实取)
脚本功能: 把本轮 LetPub 实查得到的 IF 回填报告1/报告3 的 "—" 占位, 并修正报告3 的
          两条引用错误 (Ben Zion 一作误标为 Lusher; Cochrane 刊名缩写不规范)。
          每一步替换都做断言, 任一不匹配即中止, 不做部分写入。
输入: 两个 markdown 报告文件 (cwd 内)
输出: 原地修改后的两个文件 + 控制台回显替换明细
依赖: 无第三方依赖
注意事项:
  - IF 数值全部来自本轮 LetPub 单刊实查 (_if_batch.json), 未查到的保留 "—" 或标 0* 加脚注, 不猜数;
  - Sexual Medicine 的 IF 仍沿用本轮早前核到的 2.4 (LetPub 单条目口径), 不做变更;
  - 替换全部成功后才会写盘, 中途失败不写盘。
"""
import sys, io, json, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

F1 = '文献调研_高潮差异与肛门快感原理_20260928.md'
F3 = '文献调研_高潮的个体差异_药物基因与进化_20260930.md'


def apply(path, pairs):
    s = open(path, encoding='utf-8').read()
    for i, (old, new) in enumerate(pairs, 1):
        n = s.count(old)
        if n != 1:
            print(f"  [ABORT] {path} 第{i}对 命中 {n} 次: {old[:60]!r}")
            sys.exit(1)
        s = s.replace(old, new, 1)
        print(f"  [OK {i}] {old[:46]!r} -> {new[:46]!r}")
    open(path, 'w', encoding='utf-8', newline='\n').write(s)
    print(f"  [WRITE] {path}")


# ---------- 报告 1 ----------
p1 = [
    ('Brain Res (—)\u00b9', 'Brain Res (3.2)'),                      # 15451368, 0006-8993
    ('Prog Brain Res (—)\u00b2', 'Prog Brain Res (0)*'),             # 0079-6123
    ('Neuroimage (—)\u00b3', 'NeuroImage (5.3)'),                    # 1053-8119
    ('Clin Anat (—)\u00b9', 'Clin Anat (2.4)'),                      # 0897-3806
    ('Lakartidningen (—)', 'Lakartidningen (0)*'),                   # 0023-7205
    ('Neurosci Biobehav Rev (—)\u00b9', 'Neurosci Biobehav Rev (8.5)'),  # 0149-7634
    ('Int J Urol (—)\u00b9', 'Int J Urol (2.9)'),                    # 0919-8172
    ('BMJ Public Health (—)\u2075', 'BMJ Public Health (1.7)'),       # 2753-4294
    # 脚注: 删掉已被填数的三条, 更新丛书/非 JCR 说明
    ('> \u00b9 \u672a\u9010\u520a\u6838\u5230 LetPub \u8bb0\u5f55, \u4e0d\u586b\u6570 (\u5b81\u7f3a\u52ff\u9519)\u3002\n', ''),
    ('> \u00b3 Neuroimage \u5df2\u4e8e\u8fd1\u5e74\u505c\u520a/\u5e76\u5165, 2025 \u7248\u65e0 IF\u3002\n', ''),
    ('> \u2075 BMJ Public Health \u4e3a\u65b0\u520a, \u5c1a\u672a\u8fdb\u5165 JCR, \u65e0 IF\u3002\n', ''),
    ('> \u00b2 Prog Brain Res \u4e3a\u7cfb\u5217\u4e1b\u4e66, \u65e0\u5e38\u89c4 JCR IF\u3002',
     '> * Prog Brain Res \u4e0e Lakartidningen \u5728 LetPub \u9875\u9762\u7684 IF \u5b57\u6bb5\u5747\u663e\u793a 0 '
     '(\u524d\u8005\u4e3a\u7cfb\u5217\u4e1b\u4e66, \u540e\u8005\u4e3a\u745e\u5178\u8bed\u975e JCR \u520a), '
     '\u975e\u96f6\u5f15\u7528\u5f71\u54cd\u529b\u4e4b\u610f\u3002 '
     '(2026-10-03 \u56de\u586b: Brain Res 3.2, NeuroImage 5.3, Clin Anat 2.4, Neurosci Biobehav Rev 8.5, '
     'Int J Urol 2.9, BMJ Public Health 1.7 \u5747\u4e3a LetPub \u5355\u520a\u5b9e\u67e5\u503c\u3002)'),
]

# ---------- 报告 3 ----------
p3 = [
    ('Int J Clin Pract (\u2014)\u00b9', 'Int J Clin Pract (2.0)'),
    ('Clinics (\u2014)\u00b9', 'Clinics (\u2014)'),
    ('Int J Gynaecol Obstet (\u2014)\u00b9', 'Int J Gynaecol Obstet (\u2014)'),
    ('Curr Opin Urol (\u2014)\u00b9', 'Curr Opin Urol (2.3)'),
    ('Mol Psychiatry (\u2014)\u00b9', 'Mol Psychiatry (10.4)'),
    ('Eur Urol (\u2014)\u00b9', 'Eur Urol (29.1)'),
    ('J Neurosci Rural Pract (\u2014)\u00b9', 'J Neurosci Rural Pract (1.3)'),
    ('Int J Neurosci (\u2014)\u00b9', 'Int J Neurosci (1.7)'),
    ('JAMA Intern Med (\u2014)\u00b9', 'JAMA Intern Med (26.3)'),
    ('Cochrane DB Syst Rev (11.1)', 'Cochrane Database Syst Rev (11.1)'),
    # 作者 + 标题 + 卷期页更正 (efetch 原文)
    ('| 16 | Lusher JM, et al. DRD4 polymorphisms and human sexual behavior. Mol Psychiatry. 2006;11(8).',
     '| 16 | Ben Zion IZ, et al. Polymorphisms in the dopamine D4 receptor gene (DRD4) '
     'contribute to individual differences in human sexual behavior: desire, arousal '
     'and sexual function. Mol Psychiatry. 2006;11(8):782-6.'),
    ('(**Lusher et al., 2006, Mol Psychiatry, PMID 16619053**)',
     '(**Ben Zion et al., 2006, Mol Psychiatry, PMID 16619053**)'),
]

print('=== 报告 1 回填 ===')
apply(F1, p1)
print('=== 报告 3 回填 ===')
apply(F3, p3)
print('DONE')
