# 探针记录: pi CDP 浏览器操作知乎登录页 (2026-09-30 11:51:35)

## 结论
1. launch_browser → navigate 到 zhihu.com/signin 可正常打开登录页。
2. 密码登录 tab 的 @e ref 是幽灵 ref (rect 全 0), act_ui click/setText 全部被拒
   ("Browser click requires an actionable @e ref") — 这不是偶发, 是知乎 React 表单
   的 accessibility 树与视觉层脱节, outline 里的 textbox 不可直接操作。
3. 可用替代路径 (实测成功):
   - evaluate_browser 直接查 `input[name=username]` (placeholder 手机号或邮箱),
     `.focus()` 后用 act_ui `typeText` (省略 ref) 键入 — 值成功进入, React 受控组件接受。
   - 清空输入: focus + execCommand('selectAll') + execCommand('delete') (Ctrl+A/Delete
     键序无效, execCommand 有效)。
   - 登录按钮 class: `.SignFlow-submitButton`; 表单 class: `.SignFlow Login-content`;
     密码框 `input[name=password]`; 隐藏验证码注入点 `input[name=NECaptchaValidate]` (网易易盾)。
4. 登录态判断: cookie 含 `d_c0` (设备) 不代表登录; 登录令牌是 `z_c0` (HttpOnly, JS 读不到,
   需以页面右上角出现头像/用户名或跳转离开 /signin 为准)。
5. 密码登录提交会触发网易易盾滑块/点选验证码 — 机器人通过率低, 这是自动登录的真正瓶颈。
   扫码登录 (二维码轮询) 更稳: 手机扫码一次, cookie 存活数月。
6. Windows 原生窗口 (act_ui 坐标点击 Edge 窗口) 被 "Windows refused to foreground" 拒绝
   — 后台窗口不给物理输入; CDP 页面树 (@r1 browser_page) 是可靠路径。
