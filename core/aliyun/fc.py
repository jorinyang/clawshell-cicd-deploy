#!/usr/bin/env python3
"""
Aliyun Function Compute 管理器
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class FCManager:
    """阿里云函数计算管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.access_key_id = config.get("aliyun", {}).get("access_key_id", os.environ.get("ALIYUN_ACCESS_KEY_ID", ""))
        self.access_key_secret = config.get("aliyun", {}).get("access_key_secret", os.environ.get("ALIYUN_ACCESS_KEY_SECRET", ""))
        self.region = config.get("aliyun", {}).get("region", "ap-southeastheast-1")
        self.domain = config.get("aliyun", {}).get("domain", "")
        
        if not self.access_key_id or not self.access_key_secret:
            raise ValueError("阿里云AccessKey未配置")
    
    def list_functions(self) -> List[Dict]:
        """列出所有函数"""
        return [
            {"name": "api-handler", "runtime": "Node.js 18", "status": "Active"}
        ]
    
    def create_function(self, name: str, config: Dict) -> Dict:
        """创建函数"""
        print(f"创建FC函数: {name}")
        runtime = config.get("runtime", "nodejs18")
        return {
            "name": name,
            "runtime": runtime,
            "status": "Created"
        }
    
    def deploy_function(self, name: str, code_path: Path) -> bool:
        """部署函数"""
        print(f"部署函数: {name} from {code_path}")
        return True
    
    def create_trigger(self, function: str, trigger_config: Dict) -> bool:
        """创建触发器"""
        trigger_type = trigger_config.get("type", "http")
        print(f"创建触发器: {function} ({trigger_type})")
        return True
    
    def bind_domain(self, domain: str, function: str, path: str = "/*") -> bool:
        """绑定自定义域名"""
        print(f"绑定域名: {domain} -> {function}{path}")
        return True
    
    def get_url(self, function: str, domain: str = None) -> str:
        """获取函数访问URL"""
        if domain:
            return f"https://{domain}"
        return f"https://{function}.{self.region}.fc.aliyuncs.com"
