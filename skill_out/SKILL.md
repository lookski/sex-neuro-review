---
name: lit-review-pipeline
description: >-
  文献调研全流程技能: 从查文献 (PubMed E-utils 检索 + efetch 摘要逐条核实) 到撰写
  中文结构化报告 (TL;DR / 分主题章节 / 参考文献+影响因子 IF 表 / 机器核验的数字 /
  模型性陈述标注), 再到双语 README + GitHub 推送 (公开/私有) + 宣传页发布 (知乎专栏 /
  Hugging Face Space / 掘金 / 公众号 / 小红书, 用 pi CDP 浏览器 computer use 自动登录
  发布)。当用户要求"写文献综述"、"查文献写报告"、"写综述"、"调研 X 主题推到 GitHub"、
  "给仓库做宣传页/推广文章"、"发知乎/发 HuggingFace"、"查影响因子"时使用。衔接
  paper-tracker (追踪) 与 paper-download (下载全文)。
compatibility: Windows + pi CDP 浏览器 (launch_browser); GitHub 操作需 gh CLI (账号 lookski)
  已认证; NCBI/LetPub 需网络; 遵守 AGENTS.md 的科研数据完整性协议。
metadata:
  author: huxia
  version: "2.1"
  updated: "2026-09-30"
---

# LIT-REVIEW-PIPELINE — 文献调研到 GitHub 推送全流程

> **定位**: 一条龙管线。输入一个主题, 输出四层交付物:
> ① 核验过的中文报告 (.md) → ② 双语 GitHub 仓库 → ③ 宣传页 (知乎/HF 等, 自动发布) → ④ 工作日志。
> 每层有硬性门禁, 违反任何一条不算完成。
> §1.2/§3.4/§4.3 的"网络现实"与"陷阱"是 2026-09-30 实测积累 (sex-neuro-review 与
> lifespan-evidence 两仓全流程 + 知乎登录页探针), 照做, 别重新试错。
> 知乎发布前必读捆绑参考: `references/zhihu-publishing.md` (完整操作程序 + 探针附录)。

## 0. 什么时候用 / 不用

**用**: "写一篇关于 X 的文献综述"、"查文献写报告"、"把调研推到 GitHub"、"给仓库写宣传页"、"发知乎/发 HF"。

**不用**: 单篇文献下载 (→ paper-download)、定期追踪新论文 (→ paper-tracker)、纯代码项目备份 (→ git-backup)、会话启动恢复 (→ session-startup)。

## 1. 检索层 — 只认 E-utils 摘要

### 1.1 标准动作

```
# 1) esearch 找 PMID (每条消息 ≤2 个调用, 防限流)
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=<QUERY>&retmax=10&retmode=json

# 2) efetch 拉摘要 (一次 ≤3 个 PMID, 批间 sleep 1-2s)
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=<PMIDS>&rettype=abstract&retmode=text
```

- **每个写进报告的 PMID 必须经 efetch 摘要亲自读过**, 不许凭记忆、搜索摘要、二手转述引用。
- 检索词技巧: 作者限定用 `Author%5BAuthor%5D+AND+关键词`; 概念检索零命中时拆词重试
  (例: "Pavlicev orgasm evolution copulatory ovulatory" 零命中 → `Pavlicev%5BAuthor%5D+AND+orgasm` 命中 6 篇)。
- 多轮探底都零命中时, 把"空白"本身写成报告的一节 — 文献空白也是发现。
- **凡摘要里没有的数字**: 要么去全文核 (走 paper-download), 要么标"模型性陈述"。禁止编造 PMID/DOI/统计值。

### 1.2 本机网络现实 (2026-09-30 实测)

| 目标 | 通道 | 说明 |
|---|---|---|
| NCBI E-utils | `web_fetch` 或 python `urllib` | `curl` 走 schannel 报 `CRYPT_E_REVOCATION_OFFLINE` (exit 35), 别用 |
| E-utils 并发 | ≤2 个/消息, 批间 sleep | 超了返回 HTTP 429 |
| pmc.ncbi.nlm.nih.gov | 只用 efetch 摘要 | 全文页有 reCAPTCHA |
| academic.oup.com | 放弃 | 403 |
| LetPub | `curl` 或 urllib | 正常可用; 精确刊名搜不到时换宽词 (BMC Women's Health 例) |
| GitHub (gh/git/curl) | 见 §3.4 隧道方案 | 直连与 clash 均可能 TLS reset |

## 2. 报告层 — 中文结构化报告的固定骨架

每篇报告必须包含以下章节 (可合并不可缺):

```markdown
# 文献调研_<主题>_<YYYYMMDD>.md

## 0. TL;DR          <- 编号要点, 每条一个可独立引用的硬结论 + 作者年份
## 1..N. 主题章节     <- 每个硬数字后面跟 (**作者, 年份, 期刊, PMID**)
## N+1. 参考文献      <- 表格: | # | 引用 | 期刊 (IF) | PMID | DOI |, 按主题分组
## N+2. 小结/判断     <- 3 条左右, 允许综合, 但标注哪些是推断
```

**硬性规范**:

1. **数字保真**: 统计值 (HR, OR, CI, N, P, 遗传度, 患病率, 效应量…) 一律照抄摘要原文。
   记忆里的数字先 efetch 验证再用。这是 RESEARCH DATA INTEGRITY 协议在文献调研上的投影。
2. **模型性陈述**: 任何跨文献综合、机理解释、"这说明 X" 的推断, 显式标注 "模型性陈述"
   或放在引用块里写明是综合判断。这是报告可信度的边界线。
3. **口径附录**: 涉及患病率/效应量跨研究对比时, 加"测量口径对照表" — 不同研究问的问题
   不同, 数字不可直接比 (例: 同城 FSD 患病率 29.7% vs 63.3%, 差异全在切点与抽样)。
4. **IF 列**: 期刊 2025 IF 逐刊实查 LetPub:
   `https://www.letpub.com.cn/index.php?page=journalapp&view=search&searchname=<NAME>&searchkind=1`
   解析: 结果表 `<TR>/<TD>`, 列 0=ISSN, 列 1=刊名, 列 2=`IF: x.x h-index: n CiteScore: m`, 列 3=分区。
   匹配用首词+全词包含双校验防同名误配 (曾把 Andrology 3.4 误配成 Integr Med Nephrol Androl 7.4)。
   未进 JCR 标 "—" 不猜数。
5. 报告正文中文; 文件名保持中文稳定 (引用路径不漂移)。

## 3. 仓库层 — GitHub 双语 README

### 3.1 语言结构 (用户钦定格式)

点进仓库默认看到**英文**, 顶部有切换按钮:

```
README.md      <- 英文版, 第二行: **English** | [中文](README.zh.md)
README.zh.md   <- 中文版, 第二行: **中文** | [English](README.md)
```

- 两份文件信息等价; 英文不必逐句直译, 但所有数字/结论必须一致。
- 各报告正文保持中文, README 里注明 "reports are written in Chinese; TL;DR readable
  without specialist background"。
- 若仓库本来中文为主: 中文版整体移到 README.zh.md, 英文新写。删除旧语言文件后必须
  全仓搜索确认无残留死链 (`gh api "search/code?q=repo:<owner>/<repo>+<文件名>"` + 本地 grep)。
- GitHub Pages (docsify) 仓库: `index.html` 的 `homepage` 字段与 `_sidebar.md` 首行链接
  要跟 README 改名联动, 推完回读验证。
- 口吻: 像人写的项目主页 — 不用 emoji 轰炸, 不用 delve/comprehensive/revolutionize 类
  AI 高频词, 不写 AI 署名页脚。

### 3.2 README 内容骨架

`What's inside` 表格 (每文件一行, 双语说明) → `Method notes` (检索方式 / IF 来源 /
引用编号规则 / 模型性陈述声明) → `Status` 时间线。

### 3.3 推送流程与凭据

- 账号 `lookski` (`gh auth status` 验证)。
- 私有仓新建走 git-backup 技能 (三次确认)。**改可见性 (private→public) 必须用户显式
  同意后执行**: `gh repo edit <repo> --visibility public --accept-visibility-change-consequences`。
- commit 信息双语: 首行英文, 正文中文段落, 说明改了什么为什么。
- 大文件 (>8KB) 更新: `gh api --field` 会报 `Argument list too long`, 用 python 生成
  JSON payload (`{message, content, sha}`) + `gh api ... -X PUT --input payload.json`。
- **更新已存在文件必须带当前 sha** (先 GET contents 取 `.sha`), 否则 422。

### 3.4 GitHub 网络故障自救 (2026-09-30 实战验证)

症状: github.com 443 直连 TLS reset; clash 代理 (127.0.0.1:7897) 对 github 也 reset;
但 `curl --resolve` 指定 IP 可达 (CDN 单 IP 封锁是常见诱因)。

自救顺序:
1. **探可用 IP**: `curl -s -o /dev/null -w "%{http_code}" --resolve github.com:443:140.82.121.4 https://github.com`
   (备选段: 140.82.112-121.x, 20.205.243.x; api.github.com 用 140.82.121.6)
2. **git 少量操作**: `git -c http.curloptResolve="github.com:443:<IP>" push` (用完 unset)
3. **gh api / 批量请求**: 起本地 CONNECT 隧道 (本技能目录 `scripts/gh_proxy_tool.py`,
   监听 127.0.0.1:18964, github* 域名固定走可用 IP), 所有命令加
   `HTTPS_PROXY=http://127.0.0.1:18964`。隧道 30-90 分钟会被 bg_run 超时回收, 断了重跑。
4. `git clone` 走隧道会 403 (credential-manager 与代理不兼容) — 放弃 clone, 用 contents API 逐文件打补丁。
5. ssh.github.com:443 网络可达但 key 未注册 GitHub 账号时不可用。

## 4. 宣传层 — 一次撰写, 多平台发布

### 4.1 先写"母版", 再裁剪

写一篇 3000-5000 字**母版长文** (Markdown, 存仓库 `promo/` 目录):

```markdown
# 标题: 具体到数字, 别起"浅谈/漫谈"
   (例: "30 万人的队列说孤独和戒烟一样折寿: 一份逐条核验的延寿证据手册")

## 引子            <- 一个反直觉的具体发现, 300 字内钩住人
## 我们做了什么     <- 检索方法 + 核验方法 (数字全部照抄摘要), 这是差异化卖点
## 3-5 个硬核发现   <- 每个都是"数字 + 出处 + 一句人话解读", 挑最反直觉的
## 与直觉相反的部分 <- 单列, 传播力最强的素材
## 怎么用 / 链接    <- GitHub 仓库地址 + 阅读顺序
```

### 4.2 平台矩阵

| 平台 | 篇幅 | 要点 |
|---|---|---|
| **知乎** | 3000-5000 字, 母版近全量 | 标题带数字; 首段 300 字内抛反直觉发现; 引用规范 "(作者, 期刊, 年份)"; 文末仓库链接; 知乎编辑器 markdown 表格支持差, 转列表; 发布走 §4.3 自动流程 |
| **Hugging Face** | 800-1500 字 | 形态 A: HF Space 选 `static` SDK, README.md 用 HF 元数据头 (`---\ntitle: ...\nemoji: 🔬\ncolorFrom: blue\ncolorTo: green\nsdk: static\n---`) + 证据卡片 (每条发现一张卡: 数字+出处+一句话); 形态 B: `gradio` SDK 做交互页。推送 `git push https://huggingface.co/spaces/<user>/<name>`, 需 `huggingface-cli login` (问用户要 token 或浏览器自动登录) |
| **掘金/博客园/博客** | 技术向裁剪 | 侧重"怎么用代码核验文献数字"方法论, 附检索脚本片段 |
| **微信公众号** | 800-1500 字 | 单栏短段落; 数字加粗; 文末"阅读原文"链仓库; 只出文字稿, 排版交秀米/135; 公众号后台需扫码登录, 默认只出稿 |
| **小红书** | 300-500 字 + 3-5 图 | 一图一发现 ("数字+出处"卡片); 极口语 |
| **Twitter/X / 微博** | thread | 每条 = 一个发现 (数字+出处+链接), 3-5 条 |

**通用规则**:
1. 宣传页里的每个数字必须能在仓库报告里找到出处 — 宣传页是橱窗, 不是新数据源。
   想加新数据, 先回报告层补检索, 再同步宣传页。
2. 标题禁用 "震撼/震惊/必看/深度好文"; 用 "数字 + 对比 + 反直觉" 公式。
3. 医学/健康主题必须带 "不构成医疗建议" 一句 (README 有就复述)。
4. 发布前通读, 删掉所有 "本文将/接下来/综上所述" 的 AI 腔。

### 4.3 知乎自动登录与发布 (pi CDP 浏览器, 2026-09-30 探针实测)

**保命事实 (违反必失败)**:

1. 登录页 outline 的 @e 输入框 ref 是幽灵 ref (rect 0×0), act_ui click/setText 全被拒 —
   输入一律走 `evaluate_browser` focus + `act_ui` typeText (省略 ref)。
2. 登录态判断看页面行为 (signin 是否跳走/头像是否出现), 不查 JS cookie —
   `z_c0` 是 HttpOnly, `d_c0` 是设备号人人都有。
3. 登录方式优先级: 先探已有会话 (CDP profile 持久 cookie) → 扫码 (首选, cookie 存活数月)
   → 密码登录 (备选, 预期弹网易易盾验证码, 失败两次即停转扫码)。
4. 验证码容器 `.yidun` 出现时告诉用户人工处理, 不硬刚。
5. 发布后必须回读文章 URL 断言标题在, 否则不算发布成功。
6. 全程失败 → 文稿落 `promo/zhihu_<date>.md` 交用户手动发, 不无限重试。

完整操作程序 (DOM 锚点表 / 扫码轮询 / zhuanlan 发布链路 / 探针附录):
**读 `references/zhihu-publishing.md`**。

### 4.4 Hugging Face 自动化

- Space 发布优先 CLI/git (token 走 `huggingface-cli login`, 问用户要或用已有凭据),
  不走浏览器; 浏览器自动化仅在需要网页交互 (建 Space 选 SDK) 时用 §4.3 同款方法。
- 推送: `git push https://huggingface.co/spaces/lookski/<name> main`。

## 5. 日志层 — research.log.md

每完成一层追加 checkpoint:

```markdown
# ===== [YYYY-MM-DD HH:MM:SS] <层名> 完成 =====
## 动作        <- 做了什么, 引用 PMID 清单
## 关键方法    <- 这次的坑与解法 (给下次的自己)
## 文件状态    <- 尺寸/引用数
## 下一步
```

硬性: 时间戳必须 `date '+%Y-%m-%d %H:%M:%S'` 实取; 方法坑必写 — 本技能 §1.2/§3.4/§4.3
就是这么积累来的。

## 6. 交付清单 (全流程完成判定)

- [ ] 报告: 每个 PMID 都有 efetch 记录; 数字零手打; 模型性陈述已标注; IF 已实查
- [ ] 仓库: README.md (英文默认) + README.zh.md 双向链接正确; commit 双语; 推送后 `git ls-remote` 验证
- [ ] 回读审计: 推送后重新 GET 关键文件, 断言标题/链接/UTF-8 字节正确
- [ ] 宣传页: 母版入库; 各平台裁剪稿数字与报告一致; 医学主题带免责声明; 知乎发布后文章 URL 已验证
- [ ] 日志: research.log.md 有完整 checkpoint 链

## 7. 常见陷阱 (全部踩过)

1. **凭记忆填统计值** — 最严重违规。记忆数字必须先 efetch 验证。
2. **curl 打 NCBI/GitHub** — schannel 证书吊销检查在离线/代理下必挂, 用 python urllib 或 web_fetch。
3. **E-utils 并发超 2** — 429 限流; 串行 + sleep。
4. **LetPub 同名期刊误配** — 只匹配首词会撞车 (Andrology 例), 用全词包含校验。
5. **gh api --field 传大 base64** — `Argument list too long`, 用 --input JSON payload。
6. **contents API 更新不带 sha** — 422; 先 GET `.sha`。
7. **API 回传中文控制台乱码** — 显示层问题; `sys.stdout.reconfigure(encoding='utf-8')` 后断言验证, 别肉眼判断。
8. **改 README 语言结构后留死链** — 删文件前 grep 全仓; Pages 站点同步改 index.html/_sidebar.md。
9. **隧道当永久服务** — bg_run 超时会回收 (30/90 分钟都发生过); 断了重起。
10. **宣传页编新数字** — 宣传页只能引用报告已有数字。
11. **heredoc 含 `>` `<TD>` 等符号** — 会被 workdir-guard 误判为写外部路径; 改用 write 工具。
12. **知乎登录页用 act_ui 点 @e 输入框** — 幽灵 ref (rect 0×0) 必被拒; 走 evaluate_browser
    focus + typeText 路径 (§4.3, 详见 references/zhihu-publishing.md §3.0)。
13. **拿 d_c0 cookie 当登录态** — 那是设备号; 登录令牌 z_c0 是 HttpOnly, 以页面状态判断。
14. **密码登录硬刚验证码** — 网易易盾对机器不友好, 失败两次即转扫码, 不无限重试。

## 8. 标签

`lit-review`, `pubmed`, `eutils`, `bilingual-readme`, `github-api`, `promo`, `zhihu`, `huggingface`, `computer-use`, `letpub-impact-factor`, `research-data-integrity`
