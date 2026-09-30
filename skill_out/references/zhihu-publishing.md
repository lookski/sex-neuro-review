# 知乎自动登录与发布 — 完整操作程序 (pi CDP 浏览器)

> 本文件是 lit-review-pipeline 技能的 reference, 主 SKILL.md §4.3 只留保命事实,
> 发布知乎前读本文件。全部结论来自 2026-09-30 对 zhihu.com/signin 的实测探针
> (原探针记录已并入本文件附录), 后续每次成功/失败发布都应把新坑追加到本文件。

## 1. 工具链

`launch_browser` → `navigate_browser` → `evaluate_browser` / `act_ui` / `wait_for` / `observe_ui`。

- CDP profile 持久保存 cookie: 上一次登录成功后, 后续会话大概率已带会话, 先验证再登录。
- Windows 原生窗口坐标点击会被 "Windows refused to foreground" 拒绝 (后台窗口不给物理
  输入) — 一律走 CDP 页面树 (@r1 browser_page), 不要碰桌面窗口 root。

## 2. 登录态判断 (先做)

1. navigate 到 `https://www.zhihu.com/explore`。
2. 判断依据 (按可靠性排序):
   - 页面右上角出现用户头像/昵称 → 已登录;
   - evaluate 查 DOM: `.AppHeader-profile` 或 `button.AppHeader-login` 存在与否
     (登录按钮存在 = 未登录);
   - **不要**用 JS 读 cookie 判断: 登录令牌 `z_c0` 是 HttpOnly 读不到; `d_c0` 是设备号
     人人都有, 不代表登录。
3. 未登录 → 走 §3; 已登录 → 跳 §4。

## 3. 登录 (按优先级)

### 3.0 通用事实 (实测)

- 登录页 outline 里的 @e 输入框 ref 是**幽灵 ref** (rect 0×0), `act_ui` 的 click/setText
  一律被拒 ("Browser click requires an actionable @e ref")。**不要在知乎登录页用 act_ui
  直接操作 @e 输入框。**
- 可用输入路径 (实测成功, React 受控组件接受):
  ```
  evaluate_browser: document.querySelector('input[name=username]').focus()
  act_ui: [{action: "typeText", text: "<账号>"}]   # 省略 ref, 输入跟随 focus
  ```
- 清空输入: focus 后 `document.execCommand('selectAll'); document.execCommand('delete')`
  (实测 Ctrl+A/Delete 键序无效, execCommand 有效)。

### 3.1 DOM 锚点 (写死, 不每次重找)

| 元素 | 选择器 |
|---|---|
| 用户名输入 | `input[name=username]` (placeholder "手机号或邮箱") |
| 密码输入 | `input[name=password]` |
| 提交按钮 | `.SignFlow-submitButton` |
| 表单容器 | `.SignFlow.Login-content` |
| 密码登录 tab | class 前缀 `SignFlow-switchPassword` 的 button |
| 隐藏验证码注入点 | `input[name=NECaptchaValidate]` (网易易盾, 通过后注入) |

### 3.2 扫码登录 (首选)

1. navigate 到 `https://www.zhihu.com/signin?next=%2F`, 默认二维码页。
2. observe 确认二维码图存在, 告诉用户 "请在可见浏览器窗口扫码"。
3. `wait_for` 轮询: URL 离开 /signin 或页面出现头像即成功。
4. 一次扫码 cookie 存活数月, 之后全自动 — 这是首选的根本原因。

### 3.3 密码登录 (备选)

1. 若当前是验证码登录 tab, 先 evaluate 确认 `input[name=password]` 存在 (存在即已在
   密码 tab; 不存在则点 `SignFlow-switchPassword` 按钮)。
2. 按 §3.0 路径填入账号、密码。
3. evaluate 确认两个 input 的 value 已写入, 再点 `.SignFlow-submitButton`。
4. **预期弹网易易盾滑块/点选验证码** (`wait_for` 检测 `.yidun` 容器出现) — 机器硬刚
   成功率低, **失败两次即停**, 转扫码 (§3.2) 或问用户。
5. 验证码出现时: 告诉用户 "需要人工过验证码", 用户在可见窗口手动完成后
   (NECaptchaValidate 被注入值), 重新点提交。

## 4. 发布文章 (zhuanlan)

1. navigate `https://zhuanlan.zhihu.com/write`。
2. 标题: `.WriteIndex-titleInput textarea` (备选 `textarea[placeholder*="标题"]`)。
   输入前先 evaluate 确认存在 — 类名随改版漂移, 每次先确认再操作, 不盲点。
3. 正文: `.public-DraftEditor-content` (Draft.js 编辑器)。富文本粘贴比逐字 typeText 快:
   写好 HTML 片段 → 用剪贴板粘贴路线, 或分段 typeText。发之前 evaluate 检查正文长度。
4. 发布: 点 `.PublishPanel-triggerButton` 触发发布面板 → 弹层补封面/话题 →
   面板内确认按钮 (`.PublishPanel button`) → 等跳转。
5. **发布验证 (硬性)**: 从返回的文章 URL 重新 GET / evaluate `location.href`, 断言
   标题与正文首句都在, 记入 research.log.md。URL 拿不到 = 未发布成功, 不算完成。

## 5. 降级路径

自动化全程失败 (验证码连环弹 / 风控 / DOM 大改版): 把成品文稿写到 `promo/zhihu_<date>.md`,
告诉用户手动粘贴发布。知乎账号安全 > 自动化面子, 不硬刚。

---

## 附录: 2026-09-30 登录页探针原始记录

1. launch_browser → navigate zhihu.com/signin 可正常打开登录页。
2. 密码登录 tab 的 @e ref 是幽灵 ref (rect 全 0), act_ui click/setText 全部被拒
   — 知乎 React 表单的 accessibility 树与视觉层脱节, outline 里的 textbox 不可直接操作。
3. evaluate_browser 直查 `input[name=username]` + `.focus()` + act_ui typeText 成功,
   值验证进入 DOM。
4. 清空输入 execCommand 有效, 键序无效 (§3.0)。
5. DOM 锚点实测确认: `.SignFlow-submitButton` / `.SignFlow Login-content` /
   `input[name=password]` / `input[name=NECaptchaValidate]`。
6. 登录态: 未登录时 explore 页 cookie 只有 `d_c0` (1582B), 无 `z_c0` (HttpOnly)。
7. 密码登录提交触发网易易盾验证码 — 自动登录的真正瓶颈, 不是表单。
8. Windows 原生窗口 (act_ui 坐标点击 Edge 桌面窗口) 被 "Windows refused to foreground"
   拒绝 — CDP 页面树是可靠路径。
