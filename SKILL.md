---
name: clawshell-cicd-deploy
version: 1.0.0
description: Universal CI/CD deployment plugin for Aliyun (OSS/FC), Supabase, and GitHub Actions. Supports AI Agent integration (OpenClaw, Claude Code, 阿里悟空). Auto-detects project type, installs dependencies, and deploys with single command.
---

# CI/CD Deploy Plugin 🔄

Universal CI/CD automation deployment plugin. **Deploy projects to Aliyun with one command.**

## When to Use

- User asks to deploy a project to cloud
- User wants to set up CI/CD pipeline
- User provides project files for deployment
- User asks to automate deployment workflow
- User needs GitHub Actions setup

## Capabilities

- **Aliyun OSS**: Static site hosting, Hong Kong node
- **Aliyun FC**: Serverless functions, Hong Kong node
- **Supabase**: PostgreSQL database, migrations, RLS policies
- **GitHub Actions**: Automated CI/CD workflows
- **Multi-Agent**: OpenClaw, Claude Code, 阿里悟空 compatible

## Prerequisites

1. Aliyun account with AccessKey (RAM recommended)
2. Domain name (or new registration)
3. Supabase project (or create new)
4. GitHub account with Personal Access Token

## Installation

### For OpenClaw

```bash
# Clone repository
git clone https://github.com/jorinyang/clawshell-cicd-deploy.git ~/.openclaw/plugins/cicd-deploy

# Run install
cd ~/.openclaw/plugins/cicd-deploy
chmod +x INSTALL.sh
./INSTALL.sh
```

### For Claude Code / 阿里悟空 / Other Agents

```bash
# Clone to any location
git clone https://github.com/jorinyang/clawshell-cicd-deploy.git

# Use CLI directly
cd clawshell-cicd-deploy
python3 cicd.py --help
```

## Configuration

### Interactive Setup

```bash
cicd init
```

### Manual Configuration

Create `~/.openclaw/plugins/cicd-deploy/config/config.json`:

```json
{
  "aliyun": {
    "access_key_id": "YOUR_ACCESS_KEY_ID",
    "access_key_secret": "YOUR_ACCESS_KEY_SECRET",
    "region": "ap-southeastheast-1",
    "domain": "your-domain.com"
  },
  "supabase": {
    "url": "https://xxx.supabase.co",
    "anon_key": "your_anon_key",
    "service_role_key": "your_service_role_key"
  },
  "github": {
    "token": "ghp_your_token"
  }
}
```

## Usage

### AI Agent Integration (Recommended)

```
User: "帮我部署这个Vue项目到阿里云"
Agent: exec("cicd deploy --path ./my-project")
```

### CLI Commands

```bash
# Initialize configuration
cicd init

# Deploy project
cicd deploy --path ./my-project

# Check status
cicd status --project my-project

# Watch mode (auto-redeploy on changes)
cicd watch --path ./my-project

# AI chat mode
cicd chat "帮我部署这个项目"
```

### API Server (for Webhooks)

```bash
# Start API server
cicd api
# Server runs on http://localhost:8743

# Trigger deployment via API
curl -X POST "http://localhost:8743/deploy?token=cicd-secret" \
  -H "Content-Type: application/json" \
  -d '{"project_path": "./my-project"}'
```

## Project Detection

The plugin auto-detects project types:

| Framework | Detection | Deployment |
|-----------|-----------|------------|
| Vue/React/Next | `package.json` + vite/webpack | OSS (static) |
| Express/Koa/Fastify | `package.json` + server deps | FC (Node.js) |
| Flask/FastAPI | `requirements.txt` | FC (Python) |
| Serverless | `s.yaml` (FC3) | FC (auto) |

## Deployment Flow

```
1. User provides project / describes need
2. AI Agent analyzes project structure
3. Auto-detect language, framework, dependencies
4. Create OSS bucket / FC function (if needed)
5. Generate GitHub Actions workflow
6. Configure Secrets
7. Push code → trigger CI/CD
8. Deploy to Aliyun (OSS/FC)
9. Return deployment URL
```

## Trigger Modes

### 1. AI Conversation (Recommended)

```
User → AI Agent → cicd deploy → Deployment
```

### 2. Git Push

```bash
git push → GitHub Actions → Auto-deploy
```

### 3. Webhook

```bash
# External system trigger
curl -X POST "https://your-server.com/cicd/webhook?token=xxx"
```

## Environment Detection

The plugin can generate `SKILL.md` for other agents:

```bash
python3 -c "from core.deployer.skills_detector import SkillsDetector; \
  d = SkillsDetector().detect('./my-project'); \
  print(d['skills_md'])"
```

## Directory Structure

```
clawshell-cicd-deploy/
├── cicd.py              # Main CLI
├── api.py               # REST API server
├── core/
│   ├── aliyun/         # Aliyun automation (OSS, FC)
│   ├── supabase/       # Supabase management
│   ├── github/         # GitHub automation
│   └── deployer/       # Deployment orchestrator
├── templates/
│   └── workflow.yml     # GitHub Actions template
└── config/
    └── config.json.example
```

## Error Handling

| Error | Solution |
|-------|----------|
| `AccessKey not configured` | Run `cicd init` or set in config |
| `OSS Bucket exists` | Auto-skip, use existing |
| `FC function timeout` | Check function code, increase timeout |
| `GitHub token invalid` | Regenerate token with repo scope |

## Security Notes

- Store AccessKeys in environment or config, not in code
- Use RAM users with minimal permissions
- Enable 2FA on GitHub and Aliyun
- Rotate tokens periodically

## Integration Examples

### OpenClaw

```python
# In your agent code
import subprocess
result = subprocess.run(
    ["python3", "cicd.py", "deploy", "--path", "./my-project"],
    capture_output=True, text=True
)
print(result.stdout)
```

### Claude Code

```
/command Deploy project to Aliyun
→ Exec: cicd deploy --path ./my-project
```

### 阿里悟空

```
悟空: 执行 cicd chat "部署项目到阿里云"
```

## License

MIT
