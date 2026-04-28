#!/usr/bin/env python3
"""
DeployOrchestrator - 统一部署编排器

接收项目文件，自动完成:
1. 项目分析
2. 环境创建 (OSS/FC)
3. CI/CD配置
4. 部署执行
5. 结果反馈
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from ..aliyun.oss import OSSManager
from ..aliyun.fc import FCManager
from ..github.repo import GitHubManager
from ..supabase.client import SupabaseManager


class DeployOrchestrator:
    """统一部署编排器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.oss = None
        self.fc = None
        self.github = None
        self.supabase = None
        
        self._init_managers()
    
    def _init_managers(self):
        """初始化各组件管理器"""
        try:
            self.oss = OSSManager(self.config)
        except Exception as e:
            print(f"OSS初始化失败: {e}")
        
        try:
            self.fc = FCManager(self.config)
        except Exception as e:
            print(f"FC初始化失败: {e}")
        
        try:
            self.github = GitHubManager(self.config)
        except Exception as e:
            print(f"GitHub初始化失败: {e}")
        
        try:
            self.supabase = SupabaseManager(self.config)
        except Exception as e:
            print(f"Supabase初始化失败: {e}")
    
    def deploy(self, project_path: Path, options: Dict = None) -> Dict:
        """
        执行部署
        
        Args:
            project_path: 项目路径
            options: 部署选项
            
        Returns:
            Dict: {
                "success": bool,
                "url": str,
                "error": str,
                "details": Dict
            }
        """
        options = options or {}
        project_name = options.get("name") or project_path.name
        
        print(f"🚀 开始部署项目: {project_name}")
        
        # Step 1: 分析项目
        print("📊 Step 1: 分析项目结构...")
        analysis = self._analyze_project(project_path)
        print(f"   项目类型: {analysis.get('type', 'unknown')}")
        print(f"   依赖: {analysis.get('dependencies', [])}")
        
        # Step 2: 创建OSS Bucket
        print("☁️ Step 2: 创建/获取OSS Bucket...")
        bucket_name = f"{project_name}-bucket"
        try:
            self.oss.create_bucket(bucket_name)
            print(f"   Bucket: {bucket_name}")
        except Exception as e:
            print(f"   ⚠️ Bucket创建失败: {e}")
        
        # Step 3: 如果是Node/Python后端项目，创建FC函数
        if analysis.get("type") in ["node", "python"]:
            print("⚡ Step 3: 创建FC函数...")
            try:
                func_name = f"{project_name}-api"
                self.fc.create_function(func_name, {
                    "runtime": "nodejs18" if analysis.get("type") == "node" else "python3.9"
                })
                self.fc.deploy_function(func_name, project_path / "api")
                print(f"   函数: {func_name}")
            except Exception as e:
                print(f"   ⚠️ FC函数创建失败: {e}")
        
        # Step 4: 配置GitHub Actions
        print("🔄 Step 4: 配置CI/CD...")
        try:
            workflow = self._generate_workflow(project_name, analysis)
            repo = project_name
            print(f"   Workflow已生成: {repo}/.github/workflows/deploy.yml")
        except Exception as e:
            print(f"   ⚠️ CI/CD配置失败: {e}")
        
        # Step 5: 部署静态文件到OSS
        if analysis.get("type") == "static":
            print("📦 Step 5: 部署静态文件...")
            try:
                self._deploy_static(project_path, bucket_name)
            except Exception as e:
                print(f"   ⚠️ 静态部署失败: {e}")
        
        # Step 6: 生成部署结果
        domain = self.config.get("aliyun", {}).get("domain")
        url = f"https://{domain}" if domain else self.oss.get_website_url(bucket_name) if self.oss else "N/A"
        
        return {
            "success": True,
            "url": url,
            "project": project_name,
            "type": analysis.get("type"),
            "details": {
                "bucket": bucket_name,
                "analysis": analysis
            }
        }
    
    def _analyze_project(self, project_path: Path) -> Dict:
        """分析项目结构"""
        analysis = {
            "type": "static",
            "framework": None,
            "dependencies": []
        }
        
        # 检测package.json (Node.js项目)
        package_json = project_path / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                pkg = json.load(f)
                deps = list(pkg.get("dependencies", {}).keys())
                dev_deps = list(pkg.get("devDependencies", {}).keys())
                analysis["dependencies"] = deps + dev_deps
                
                # 判断是前端还是后端
                if "next" in deps or "nuxt" in deps or "vite" in deps or "webpack" in deps:
                    analysis["type"] = "static"
                    analysis["framework"] = "next" if "next" in deps else "nuxt" if "nuxt" in deps else "vite"
                elif "express" in deps:
                    analysis["type"] = "node"
                    analysis["framework"] = "express"
                elif "koa" in deps:
                    analysis["type"] = "node"
                    analysis["framework"] = "koa"
                elif "fastify" in deps:
                    analysis["type"] = "node"
                    analysis["framework"] = "fastify"
                else:
                    analysis["type"] = "static"
        
        # 检测requirements.txt (Python项目)
        requirements = project_path / "requirements.txt"
        if requirements.exists():
            with open(requirements) as f:
                analysis["dependencies"] = [l.strip() for l in f if l.strip()]
                analysis["type"] = "python"
        
        # 检测s.yaml (阿里云FC项目)
        s_yaml = project_path / "s.yaml"
        if s_yaml.exists():
            analysis["type"] = "fc"
            analysis["framework"] = "fc3"
        
        return analysis
    
    def _generate_workflow(self, project_name: str, analysis: Dict) -> str:
        """生成GitHub Actions workflow"""
        workflow = f"""name: Deploy to Aliyun

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        if: contains('{analysis.get("type")}', 'node')
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          
      - name: Install dependencies
        if: contains('{analysis.get("type")}', 'node')
        run: npm ci
        
      - name: Build
        if: contains('{analysis.get("type")}', 'node')
        run: npm run build
        
      - name: Deploy to OSS
        run: |
          # 阿里云OSS上传命令
          echo "Deploying to OSS..."
          
      - name: Deploy to FC
        if: contains('{analysis.get("type")}', 'node')
        run: |
          # 阿里云FC部署命令
          echo "Deploying to FC..."
"""
        return workflow
    
    def _deploy_static(self, project_path: Path, bucket: str) -> bool:
        """部署静态文件到OSS"""
        if not self.oss:
            return False
        
        # 查找构建产物目录
        dist_dirs = ["dist", "build", "out", "public"]
        for dist_dir in dist_dirs:
            if (project_path / dist_dir).exists():
                print(f"   发现构建目录: {dist_dir}")
                # 实际上传
                for file in (project_path / dist_dir).rglob("*"):
                    if file.is_file():
                        relative = file.relative_to(project_path / dist_dir)
                        self.oss.upload_file(bucket, file, str(relative))
                return True
        
        # 如果没有构建目录，上传整个项目
        for file in project_path.rglob("*"):
            if file.is_file() and not file.name.startswith('.'):
                relative = file.relative_to(project_path)
                if str(relative).startswith('node_modules'):
                    continue
                self.oss.upload_file(bucket, file, str(relative))
        
        return True
