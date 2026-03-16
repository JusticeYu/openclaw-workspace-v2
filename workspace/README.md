# OpenClaw Workspace

OpenClaw工作空间，包含自定义技能和工具。

## 🚀 包含的技能

### quarterly-planning (季度立项管理) ⭐

完整的季度Release Planning（发布规划）管理技能，协助PO和SM完成立项流程。

**功能：**
- ✅ 季度工作日计算（含节假日、补班）
- ✅ 项目组负荷评估（90-100%饱和管理）
- ✅ 特性优先级排序（MoSCoW方法）
- ✅ 用户故事拆分（≤10人天粒度）
- ✅ PPT规划报告生成（8页模板）
- ✅ 完整的立项评审检查清单

**位置：** `skills/quarterly-planning/`

**快速开始：**
```bash
# 计算工作日
python skills/quarterly-planning/scripts/workday_calculator.py --year 2026 --quarter 2

# 评估负荷
python skills/quarterly-planning/scripts/capacity_calculator.py \
  --workdays 62 \
  --dev-capacity 2.8 \
  --test-capacity 1.5 \
  --product-capacity 0.8 \
  --total-days 300

# 生成PPT
python skills/quarterly-planning/scripts/create_ppt_template.py
```

**详细文档：**
- 使用指南：`skills/quarterly-planning/references/USAGE.md`
- 检查清单：`skills/quarterly-planning/references/rp_checklist_quickref.md`
- 数据模板：`skills/quarterly-planning/references/data_templates.md`

**安装依赖：**
```bash
pip install python-pptx
```

---

## 📁 目录结构

```
workspace/
├── skills/
│   ├── quarterly-planning/         # 季度立项管理技能
│   │   ├── SKILL.md               # 技能主文档
│   │   ├── quarterly-planning.skill  # 打包文件
│   │   ├── scripts/               # 工具脚本
│   │   ├── references/            # 参考文档
│   │   └── assets/                # 资源文件（PPT模板）
│   └── ...
├── AGENTS.md                      # Agent配置
├── SOUL.md                        # 系统配置
├── USER.md                        # 用户配置
└── ...
```

---

## 🛠️ 其他技能

- `coze-image-gen` - 图像生成（基于Coze）
- `coze-voice-gen` - 语音合成和识别（基于Coze）
- `coze-web-fetch` - 网页内容抓取（基于Coze）
- `coze-web-search` - 网页搜索（基于Coze）

---

## 📝 使用方法

### 在OpenClaw中使用

直接在聊天中发送触发词：
```
季度立项
特性规划
负荷评估
工作日计算
规划报告
```

### 直接运行脚本

所有脚本都有完整的参数说明，使用 `--help` 查看：
```bash
python skills/quarterly-planning/scripts/workday_calculator.py --help
```

---

## 📦 安装技能

从打包文件安装：
```bash
unzip skills/quarterly-planning.skill -d /target/path/
```

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📄 许可证

MIT License

---

*本工作空间由 OpenClaw 管理*
