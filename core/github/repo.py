#!/usr/bin/env python3
"""
GitHub 仓库管理器
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any


class GitHubManager:
    """GitHub管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.token = config.get("github", {}).get("token", os.environ.get("GITHUB_TOKEN", ""))
        self.owner = config.get("github", {}).get("owner", "")
        self.api_base = "https://api.github.com"
        
        if not self.token:
            raise ValueError("GitHub Token未配置")
    
    def _headers(self) -> Dict:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def list_repos(self) -> List[Dict]:
        """列出仓库"""
        import urllib.request
        
        url = f"{self.api_base}/user/repos"
        req = urllib.request.Request(url, headers=self._headers())
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read())
        except Exception as e:
            print(f"列出仓库失败: {e}")
            return []
    
    def create_repo(self, name: str, private: bool = True) -> Dict:
        """创建仓库"""
        import urllib.request
        
        url = f"{self.api_base}/user/repos"
        data = json.dumps({
            "name": name,
            "private": private,
            "auto_init": True
        }).encode()
        
        req = urllib.request.Request(url, data=data, headers=self._headers())
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read())
        except Exception as e:
            print(f"创建仓库失败: {e}")
            return {"error": str(e)}
    
    def upload_file(self, repo: str, path: str, content: bytes, message: str = "Upload") -> bool:
        """上传文件"""
        import urllib.request
        
        url = f"{self.api_base}/repos/{self.owner or 'me'}/{repo}/contents/{path}"
        encoded_content = base64.b64encode(content).decode()
        
        data = json.dumps({
            "message": message,
            "content": encoded_content
        }).encode()
        
        req = urllib.request.Request(url, data=data, headers=self._headers())
        
        try:
            with urllib.request.urlopen(req) as response:
                return True
        except Exception as e:
            print(f"上传文件失败: {e}")
            return False
    
    def get_workflow_runs(self, repo: str) -> List[Dict]:
        """获取Workflow运行记录"""
        import urllib.request
        
        url = f"{self.api_base}/repos/{self.owner or 'me'}/{repo}/actions/runs"
        req = urllib.request.Request(url, headers=self._headers())
        
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read())
                return data.get("workflow_runs", [])
        except Exception as e:
            print(f"获取Workflow失败: {e}")
            return []
    
    def trigger_workflow(self, repo: str, workflow_id: str, inputs: Dict = None) -> bool:
        """触发Workflow"""
        import urllib.request
        
        url = f"{self.api_base}/repos/{self.owner or 'me'}/{repo}/actions/workflows/{workflow_id}/dispatches"
        data = json.dumps({
            "ref": "main",
            "inputs": inputs or {}
        }).encode()
        
        req = urllib.request.Request(url, data=data, headers=self._headers())
        
        try:
            urllib.request.urlopen(req)
            return True
        except Exception as e:
            print(f"触发Workflow失败: {e}")
            return False
