# CI/CD 自动化部署插件

## 概述

通用的CI/CD自动化部署插件，**解耦设计**，支持多种AI Agent调用。

**用户只需提供凭据，AI自动完成所有部署工作。**

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **🔌 解耦设计** | 标准CLI/API接口，适配多种AI Agent |
| **🤖 多Agent适配** | OpenClaw、Claude Code、阿里悟空等 |
| **⚡ 一键部署** | 发送项目文件，AI自动完成全流程 |
| **🔄 三种触发** | Git推送 / AI对话 / Webhook |
| **☁️ 阿里云OSS+FC** | 香港节点，自动配置域名+SSL |
| **🗄️ Supabase集成** | 自动创建表、执行迁移、配置RLS |

---

## 多Agent适配 (解耦设计)

本插件采用**标准CLI和REST API接口**，可被任何AI Agent调用：

### OpenClaw 调用示例

```
用户: "帮我部署这个Vue项目"
Agent: exec("cicd deploy --path ./my-project")
```

### Claude Code 调用示例

```
/command Deploy the project to Aliyun
-> cicd deploy --path ./my-project
```

### 阿里悟空调用示例

```
悟空: 执行 cicd chat "部署项目到阿里云"
```

### 外部系统调用 (Webhook)

```bash
curl -X POST "https://your-server.com:8743/deploy?token=xxx" \
  -H "Content-Type: application/json" \
  -d '{"project_path": "./my-project", "type": "static"}'
```

### Python API调用

```python
from cicd_deploy.api import APIServer
from cicd_deploy.core.deployer import DeployOrchestrator
from cicd_deploy.core.config_manager import ConfigManager

config = ConfigManager().load()
orchestrator = DeployOrchestrator(config)
result = orchestrator.deploy("./my-project")
```

---

## 快速开始

### 首次配置

```bash
cicd init
```

按引导提供凭据信息。

### 使用方式

#### 方式一: AI对话触发 (推荐)

```
用户: "帮我部署这个Vue项目到阿里云"
Agent: (自动完成分析→创建→配置→部署→返回URL)
```

#### 方式二: Git推送触发

```bash
git add . && git commit -m "deploy"
git push
# 自动触发部署
```

#### 方式三: Webhook触发

```bash
# 触发部署
curl -X POST "https://your-server.com:8743/deploy?token=xxx" \
  -d '{"project_path": "./my-project"}'

# GitHub Webhook (自动)
# 在GitHub仓库设置Webhook -> Payload URL: https://your-server.com:8743/webhook?token=xxx
```

---

## 前置要求

用户需提供以下凭据信息（由Agent引导完成）:

| 凭据 | 获取指引 | 用途 |
|------|---------|------|
| 阿里云 AccessKey | RAM控制台创建用户 (由Agent自动完成) | OSS/FC部署 |
| 阿里云 域名 | 已有或新建 (由Agent自动完成) | 域名绑定/SSL |
| Supabase Keys | 项目设置获取 (由Agent自动完成) | 数据库 |
| GitHub Token | Settings → Developer settings (由Agent自动完成) | 仓库/Actions |

### 免费SSL证书指引

阿里云提供免费DVSSL证书 (由Agent自动申请):

1. 访问 [SSL证书控制台](https://yundun.console.aliyun.com)
2. 选择"免费证书" → "立即购买"
3. 选择"DV单域名证书" → "免费使用"
4. 填入域名，选择自动验证
5. 等待签发 (约5-10分钟)

---

## 命令行使用

```bash
# 初始化配置
cicd init

# 部署项目
cicd deploy --path ./my-project

# 查看状态
cicd status --project my-project

# 监听模式
cicd watch --path ./my-project

# AI对话模式 (供AI Agent调用)
cicd chat "帮我部署这个项目"

# 启动API服务器 (Webhook支持)
cicd api
```

---

## 部署流程

```
1. 接收需求 → 用户发送项目文件或描述需求
2. 项目分析 → AI分析结构、依赖、架构 (Agent自动完成)
3. 环境创建 → 创建OSS Bucket、FC函数、数据库 (Agent自动完成)
4. CI/CD配置 → 配置Secrets、生成Actions工作流 (Agent自动完成)
5. 部署执行 → 推送代码、构建、部署、验证 (Agent自动完成)
6. 结果反馈 → 返回URL、状态、问题解决 (Agent自动完成)
```

---

## API接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/status?task_id=xxx` | GET | 查看部署状态 |
| `/deploy?token=xxx` | POST | 触发部署 |
| `/webhook?token=xxx` | POST | GitHub Webhook |

---

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent (任意)                         │
│         OpenClaw / Claude Code / 阿里悟空 / 其他          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              cicd CLI / REST API (标准接口)                 │
├─────────────────────────────────────────────────────────────┤
│  core/                                                     │
│  ├── aliyun/     # 阿里云OSS/FC自动化 (解耦)            │
│  ├── supabase/   # Supabase管理自动化 (解耦)            │
│  ├── github/     # GitHub仓库/Actions自动化 (解耦)      │
│  └── deployer/   # 统一部署编排 (解耦)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 项目迭代

```
用户发送更新
      ↓
AI分析差异
      ↓
更新仓库
      ↓
触发CI/CD
      ↓
自动部署
      ↓
返回新URL
```

---

## 许可证

MIT
