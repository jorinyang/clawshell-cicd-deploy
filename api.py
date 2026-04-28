#!/usr/bin/env python3
"""
CI/CD Deploy Plugin - REST API Server

支持Webhook触发，供外部系统调用
也作为其他AI Agent的API接口
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading


class CICDAPIHandler(BaseHTTPRequestHandler):
    """API请求处理器"""
    
    # 存储活跃部署任务
    deployments: Dict[str, Dict] = {}
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[API] {args[0]}")
    
    def _send_json(self, status: int, data: Dict):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _parse_body(self) -> Optional[Dict]:
        """解析请求体"""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            return json.loads(body)
        return None
    
    def do_GET(self):
        """处理GET请求"""
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        
        if path == "/health":
            self._send_json(200, {"status": "ok"})
            
        elif path == "/status":
            task_id = query.get("task_id", [None])[0]
            if task_id and task_id in self.deployments:
                self._send_json(200, self.deployments[task_id])
            else:
                self._send_json(200, {"tasks": list(self.deployments.keys())})
                
        elif path == "/projects":
            # 列出已部署项目
            config_path = Path(__file__).parent / "config" / "projects.json"
            if config_path.exists():
                with open(config_path) as f:
                    projects = json.load(f)
                self._send_json(200, {"projects": projects})
            else:
                self._send_json(200, {"projects": []})
        else:
            self._send_json(404, {"error": "Not found"})
    
    def do_POST(self):
        """处理POST请求"""
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        body = self._parse_body()
        
        # 验证Token
        token = query.get("token", [None])[0]
        expected_token = os.environ.get("CICD_WEBHOOK_TOKEN", "cicd-secret")
        if token != expected_token:
            self._send_json(401, {"error": "Unauthorized"})
            return
        
        if path == "/deploy":
            # 触发部署
            task_id = self._handle_deploy(body)
            self._send_json(202, {"task_id": task_id, "status": "accepted"})
            
        elif path == "/webhook":
            # GitHub Webhook
            event = self.headers.get("X-GitHub-Event", "push")
            self._handle_webhook(event, body)
            self._send_json(200, {"status": "ok"})
            
        else:
            self._send_json(404, {"error": "Not found"})
    
    def _handle_deploy(self, body: Optional[Dict]) -> str:
        """处理部署请求"""
        from .core.deployer.orchestrator import DeployOrchestrator
        from .core.config_manager import ConfigManager
        
        task_id = f"deploy_{len(self.deployments) + 1}"
        
        config = ConfigManager().load()
        orchestrator = DeployOrchestrator(config)
        
        project_path = body.get("project_path") or body.get("project")
        if not project_path:
            raise ValueError("project_path is required")
        
        self.deployments[task_id] = {
            "status": "running",
            "project": project_path,
            "message": "Deployment started"
        }
        
        # 后台执行部署
        def run_deploy():
            try:
                result = orchestrator.deploy(Path(project_path))
                self.deployments[task_id].update({
                    "status": "completed" if result["success"] else "failed",
                    "result": result
                })
            except Exception as e:
                self.deployments[task_id].update({
                    "status": "failed",
                    "error": str(e)
                })
        
        thread = threading.Thread(target=run_deploy)
        thread.start()
        
        return task_id
    
    def _handle_webhook(self, event: str, body: Optional[Dict]):
        """处理GitHub Webhook"""
        if event == "push":
            # 代码推送，触发部署
            repo = body.get("repository", {}).get("full_name")
            branch = body.get("ref", "").replace("refs/heads/", "")
            
            if branch == "main":
                print(f"[Webhook] Push to {repo}/{branch}, triggering deploy...")
                # 触发部署
                
        elif event == "workflow_run":
            # Workflow状态变更
            conclusion = body.get("workflow_run", {}).get("conclusion")
            print(f"[Webhook] Workflow concluded: {conclusion}")


class APIServer:
    """API服务器"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8743):
        self.host = host
        self.port = port
        self.server = None
    
    def start(self):
        """启动服务器"""
        self.server = HTTPServer((self.host, self.port), CICDAPIHandler)
        print(f"[API] Server starting on {self.host}:{self.port}")
        print(f"[API] Endpoints:")
        print(f"  GET  /health              - 健康检查")
        print(f"  GET  /status?task_id=xxx  - 查看部署状态")
        print(f"  POST /deploy?token=xxx   - 触发部署")
        print(f"  POST /webhook?token=xxx  - GitHub Webhook")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\n[API] Server stopped")
            self.server.shutdown()
    
    @staticmethod
    def run_background():
        """后台运行"""
        server = APIServer()
        thread = threading.Thread(target=server.start)
        thread.daemon = True
        thread.start()
        return thread


if __name__ == "__main__":
    APIServer().start()
