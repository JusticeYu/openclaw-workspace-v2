---
name: xhs-crawler-tool
description: 小红书数据爬取工具，支持Cookie登录、关键词搜索、数据导出。解决服务器headless环境下登录问题，提供简化的爬取接口。触发词：小红书爬取、xhs爬虫、爬取小红书数据、南山书城舞房。
---

# 小红书爬虫工具 (XHS Crawler Tool)

专门针对小红书平台的简化爬取工具，解决服务器环境登录难题。

## 特点

- ✅ **Cookie登录** - 无需二维码，直接使用Cookie登录
- ✅ **Headless支持** - 完美支持服务器无图形界面环境
- ✅ **简化接口** - 一条命令完成爬取
- ✅ **数据导出** - 支持JSON/CSV/Excel格式
- ✅ **防检测** - 内置反爬虫策略

## 快速开始

### 方式1：使用快速脚本（推荐）⭐

```bash
# 进入技能目录
cd skills/xhs-crawler-tool

# 搜索南山书城舞房转卡信息（1页演示）
./crawl.sh search "南山书城 舞房 转卡" 1

# 搜索并获取5页结果
./crawl.sh search "南山书城 舞房 转卡" 5

# 查看Cookie获取指南
./crawl.sh cookie
```

### 方式2：使用Python脚本

```bash
# 基础搜索
python scripts/xhs_search.py --keyword "南山书城 舞房 转卡"

# 指定页数
python scripts/xhs_search.py --keyword "南山书城 舞房 转卡" --pages 5

# 导出为CSV
python scripts/xhs_search.py --keyword "南山书城 舞房 转卡" --output csv

# 使用Cookie（获取真实数据）
export XHS_COOKIE="你的Cookie值"
python scripts/xhs_search.py --keyword "南山书城 舞房 转卡"
```

### 获取Cookie（获取真实数据）

**方法A：从浏览器获取（推荐）**
1. 在电脑浏览器登录小红书
2. 按F12打开开发者工具
3. 切换到 Application/Storage 标签
4. 找到 Cookies → www.xiaohongshu.com
5. 复制 `web_session` 或 `webId` 的值

**方法B：使用浏览器扩展**
1. 安装 "EditThisCookie" 或 "Cookie Editor" 扩展
2. 登录小红书
3. 导出Cookie，找到 `web_session`

**设置Cookie：**
```bash
# 方式1：设置环境变量
export XHS_COOKIE="你的Cookie值"

# 方式2：创建配置文件
echo "你的Cookie值" > config/cookie.txt
```

详细指南见：`references/COOKIE_GUIDE.md`

## 命令参数

```
python scripts/xhs_search.py [OPTIONS]

Options:
  --keyword TEXT    搜索关键词（必填）
  --pages INTEGER   爬取页数 [默认: 3]
  --output TEXT     输出格式: json/csv/excel [默认: json]
  --cookie TEXT     Cookie值（或从环境变量读取）
  --headless        启用headless模式 [默认: True]
```

## 数据字段

| 字段 | 说明 |
|------|------|
| title | 帖子标题 |
| content | 帖子内容 |
| author | 作者昵称 |
| likes | 点赞数 |
| comments | 评论数 |
| url | 帖子链接 |
| publish_time | 发布时间 |

## 示例

### 爬取舞房转卡信息

```bash
python scripts/xhs_search.py \
  --keyword "南山书城 舞房 转卡" \
  --pages 5 \
  --output csv
```

### 爬取多个关键词

```bash
python scripts/xhs_search.py \
  --keyword "深圳 舞蹈室 转卡" \
  --pages 10 \
  --output excel
```

## 注意事项

1. **Cookie有效期** - Cookie通常7-30天有效，过期需重新获取
2. **爬取频率** - 建议设置适当延迟，避免触发风控
3. **仅供学习** - 请遵守小红书使用条款

## 故障排除

**Q: 提示Cookie无效**
A: Cookie可能已过期，重新从浏览器获取

**Q: 爬取不到数据**
A: 检查关键词是否正确，或尝试更换Cookie

**Q: 被限制访问**
A: 降低爬取频率，增加延迟时间
