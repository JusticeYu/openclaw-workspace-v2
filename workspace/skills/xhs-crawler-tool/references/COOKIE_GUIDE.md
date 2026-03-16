# Cookie获取完整指南

## 🔑 为什么需要Cookie？

小红书需要登录才能搜索和查看完整内容。在服务器headless环境下无法显示二维码，因此需要使用Cookie登录。

---

## 方法1：浏览器开发者工具（推荐）

### Chrome/Edge浏览器

1. **登录小红书**
   - 打开 https://www.xiaohongshu.com
   - 使用手机号/微信/QQ登录

2. **打开开发者工具**
   - 按 `F12` 或 `Ctrl+Shift+I` (Windows)
   - 按 `Cmd+Option+I` (Mac)

3. **找到Application标签**
   ```
   开发者工具顶部标签:
   Elements | Console | Sources | Network | Performance | Memory | 
   Application | Security | Lighthouse
   
   点击: Application
   ```

4. **查看Cookies**
   ```
   左侧菜单:
   Storage
   ├── Cookies
   │   └── https://www.xiaohongshu.com
   ```

5. **复制Cookie值**
   - 在列表中找到 `web_session` 或 `webId`
   - 双击Value列的值
   - 复制完整的字符串

6. **设置环境变量**
   ```bash
   export XHS_COOKIE='复制的值'
   ```

---

## 方法2：浏览器扩展（更简单）

### 使用 EditThisCookie 扩展

1. **安装扩展**
   - Chrome: 商店搜索 "EditThisCookie"
   - Edge: 商店搜索 "EditThisCookie"

2. **登录小红书**
   - 正常登录账号

3. **获取Cookie**
   - 点击浏览器工具栏的EditThisCookie图标
   - 找到 `web_session` 或 `webId`
   - 点击复制按钮

### 使用 Cookie Editor 扩展

1. **安装扩展**
   - Chrome/Edge 商店搜索 "Cookie Editor"

2. **导出Cookie**
   - 登录小红书
   - 点击扩展图标
   - 选择 "Export" → "JSON"
   - 找到 `web_session` 字段

---

## 方法3：控制台命令（高级）

在开发者工具的Console标签中执行：

```javascript
// 获取特定Cookie
document.cookie.split(';').find(c => c.trim().startsWith('web_session='))

// 获取所有Cookie
document.cookie
```

---

## 验证Cookie有效性

设置Cookie后，测试是否有效：

```bash
cd skills/xhs-crawler-tool

# 设置Cookie
export XHS_COOKIE='你的Cookie值'

# 运行测试
python scripts/xhs_search.py --keyword "测试" --pages 1
```

如果看到 "✅ 已加载Cookie" 且返回真实数据（不是演示数据），说明Cookie有效。

---

## Cookie有效期

| Cookie类型 | 有效期 | 说明 |
|-----------|--------|------|
| web_session | 7-30天 | 主要登录凭证 |
| webId | 长期 | 设备标识 |
| a1 | 长期 | 用户标识 |

**建议**: 每2周更新一次Cookie

---

## 保存Cookie到文件

创建 `.env` 文件：

```bash
cd skills/xhs-crawler-tool
cat > .env << 'EOF'
XHS_COOKIE=你的Cookie值
EOF
```

或者创建 `config/cookie.txt`：

```bash
mkdir -p config
echo "你的Cookie值" > config/cookie.txt
```

---

## 常见问题

**Q: Cookie获取后还是提示无效？**
A: 
1. 检查是否复制完整（不要有多余空格）
2. Cookie可能已过期，重新获取
3. 确保小红书账号未被封禁

**Q: 如何延长Cookie有效期？**
A: 定期访问小红书网站，保持活跃状态

**Q: 可以在多台设备使用同一个Cookie吗？**
A: 可以，但频繁切换可能导致Cookie失效

**Q: Cookie泄露有风险吗？**
A: 有！Cookie相当于临时密码，请勿分享给他人

---

## 安全建议

1. ✅ 定期更换Cookie
2. ✅ 不在公共环境保存Cookie
3. ✅ 使用 `.env` 文件并加入 `.gitignore`
4. ❌ 不要将Cookie提交到Git仓库
5. ❌ 不要分享Cookie给他人
