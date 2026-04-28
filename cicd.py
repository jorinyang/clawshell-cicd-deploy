#!/usr/bin/env python3
"""
CI/CD 自动化部署插件 - 主CLI

通用CI/CD部署工具，支持多种AI Agent调用
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

# 插件目录
PLUGIN_DIR = Path(__file__).parent
CONFIG_DIR = PLUGIN_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def cmd_init(args):
    """初始化配置"""
    from core.config_manager import ConfigManager
    
    config = ConfigManager()
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           CI/CD 部署插件 - 首次配置向导              ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    
    # 阿里云配置
    print("║  第一部分: 阿里云配置                                ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  请提供以下信息 (直接回车跳过，使用默认值):              ║")
    
    access_key_id = input("║  AccessKey ID: ") or ""
    access_key_secret = input("║  AccessKey Secret: ") or ""
    region = input("║  区域 (默认: ap-southeastheast-1 香港): ") or "ap-southeastheast-1"
    domain = input("║  域名 (已有域名或新建): ") or ""
    
    if access_key_id:
        config.set("aliyun.access_key_id", access_key_id)
    if access_key_secret:
        config.set("aliyun.access_key_secret", access_key_secret)
    config.set("aliyun.region", region)
    config.set("aliyun.domain", domain)
    
    # Supabase配置
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  第二部分: Supabase配置                               ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    
    supabase_url = input("║  Project URL (https://xxx.supabase.co): ") or ""
    anon_key = input("║  Anon Key: ") or ""
    service_role_key = input("║  Service Role Key: ") or ""
    
    if supabase_url:
        config.set("supabase.url", supabase_url)
    if anon_key:
        config.set("supabase.anon_key", anon_key)
    if service_role_key:
        config.set("supabase.service_role_key", service_role_key)
    
    # GitHub配置
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  第三部分: GitHub配置                                 ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    
    github_token = input("║  Personal Access Token: ") or ""
    github_owner = input("║  Owner/Org (默认: 个人仓库): ") or ""
    
    if github_token:
        config.set("github.token", github_token)
    if github_owner:
        config.set("github.owner", github_owner)
    
    # 保存
    config.save()
    
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  配置已保存!                                     ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # 验证
    if access_key_id:
        verify_aliyun(config)


def verify_aliyun(config):
    """验证阿里云连接"""
    print("║  正在验证阿里云连接...                              ║")
    try:
        from core.aliyun.oss import OSSManager
        oss = OSSManager(config)
        buckets = oss.list_buckets()
        print(f"║  ✅ 阿里云连接成功 (发现 {len(buckets)} 个Bucket)         ║")
    except Exception as e:
        print(f"║  ⚠️ 阿里云验证失败: {str(e)[:40]}                      ║")


def cmd_deploy(args):
    """部署项目"""
    from core.deployer.orchestrator import DeployOrchestrator
    
    config = load_config()
    project_path = Path(args.path).resolve()
    
    if not project_path.exists():
        print(f"❌ 项目路径不存在: {project_path}")
        return 1
    
    print(f"🚀 开始部署项目: {project_path}")
    
    orchestrator = DeployOrchestrator(config)
    result = orchestrator.deploy(project_path, {
        "name": args.name,
        "type": args.type,
    })
    
    if result["success"]:
        print(f"✅ 部署成功!")
        print(f"   URL: {result.get('url', 'N/A')}")
        return 0
    else:
        print(f"❌ 部署失败: {result.get('error', 'Unknown')}")
        return 1


def cmd_status(args):
    """查看状态"""
    config = load_config()
    project_name = args.project or "default"
    
    print(f"📊 项目状态: {project_name}")
    
    # 检查各组件状态
    from core.aliyun.oss import OSSManager
    from core.aliyun.fc import FCManager
    
    try:
        oss = OSSManager(config)
        buckets = oss.list_buckets()
        print(f"  OSS Buckets: {len(buckets)}")
    except Exception as e:
        print(f"  OSS: ❌ {e}")
    
    try:
        fc = FCManager(config)
        functions = fc.list_functions()
        print(f"  FC Functions: {len(functions)}")
    except Exception as e:
        print(f"  FC: ❌ {e}")
    
    return 0


def cmd_watch(args):
    """监听模式"""
    from core.deployer.orchestrator import DeployOrchestrator
    import time
    
    config = load_config()
    project_path = Path(args.path).resolve()
    
    print(f"👀 监听模式: {project_path}")
    print("按 Ctrl+C 停止")
    
    orchestrator = DeployOrchestrator(config)
    last_mtime = 0
    
    try:
        while True:
            mtime = project_path.stat().st_mtime
            if mtime != last_mtime:
                print(f"\n📝 检测到变更，重新部署...")
                result = orchestrator.deploy(project_path)
                if result["success"]:
                    print(f"✅ 部署成功: {result.get('url')}")
                else:
                    print(f"❌ 部署失败: {result.get('error')}")
                last_mtime = mtime
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n👋 停止监听")
    return 0


def cmd_chat(args):
    """AI对话模式 - 供AI Agent调用"""
    from core.deployer.orchestrator import DeployOrchestrator
    from core.github.repo import GitHubManager
    
    config = load_config()
    message = args.message
    
    print(f"💬 AI对话模式: {message}")
    
    orchestrator = DeployOrchestrator(config)
    
    # 解析意图
    if "部署" in message or "deploy" in message.lower():
        # 提取项目路径
        path = extract_path(message)
        if path:
            result = orchestrator.deploy(Path(path))
            return 0 if result["success"] else 1
    
    print("💡 请使用 'cicd deploy --path ./project' 命令部署项目")
    return 0


def extract_path(message: str) -> Optional[str]:
    """从消息中提取路径"""
    import re
    # 匹配 ./xxx 或 /xxx 或 ~/xxx
    patterns = [r'\./([^\s]+)', r'/([^\s]+)', r'~(/[^\s]+)']
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(0)
    return None


def load_config() -> Dict[str, Any]:
    """加载配置"""
    from core.config_manager import ConfigManager
    return ConfigManager().load()


def main():
    parser = argparse.ArgumentParser(
        description="CI/CD 自动化部署插件",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # init
    subparsers.add_parser("init", help="初始化配置")
    
    # deploy
    deploy_parser = subparsers.add_parser("deploy", help="部署项目")
    deploy_parser.add_argument("--path", "-p", required=True, help="项目路径")
    deploy_parser.add_argument("--name", "-n", help="项目名称")
    deploy_parser.add_argument("--type", "-t", default="auto", help="项目类型: static/node/python")
    
    # status
    status_parser = subparsers.add_parser("status", help="查看状态")
    status_parser.add_argument("--project", help="项目名称")
    
    # watch
    watch_parser = subparsers.add_parser("watch", help="监听模式")
    watch_parser.add_argument("--path", "-p", required=True, help="项目路径")
    
    # chat
    chat_parser = subparsers.add_parser("chat", help="AI对话模式")
    chat_parser.add_argument("message", help="消息")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    commands = {
        "init": cmd_init,
        "deploy": cmd_deploy,
        "status": cmd_status,
        "watch": cmd_watch,
        "chat": cmd_chat,
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
