#!/usr/bin/env python3
"""
Skills 检测器 - 自动检测和安装项目依赖

支持解耦调用：
- OpenClaw: 通过exec调用
- Claude Code: 通过工具调用
- 阿里悟空: 通过Agent调用
- 其他AI Agent: 通过标准CLI/API调用
"""

import os
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class SkillsDetector:
    """项目依赖检测器"""
    
    def __init__(self):
        self.detectors = {
            "package.json": self._detect_nodejs,
            "requirements.txt": self._detect_python,
            "Pipfile": self._detect_python,
            "pyproject.toml": self._detect_python,
            "go.mod": self._detect_go,
            "Cargo.toml": self._detect_rust,
            "composer.json": self._detect_php,
            "Gemfile": self._detect_ruby,
            "pom.xml": self._detect_java,
            "build.gradle": self._detect_java,
            "s.yaml": self._detect_fc,  # 阿里云FC项目
        }
    
    def detect(self, project_path: Path) -> Dict[str, Any]:
        """
        检测项目依赖
        
        Returns:
            {
                "language": str,
                "framework": str,
                "dependencies": List[str],
                "dev_dependencies": List[str],
                "install_command": str,
                "build_command": str,
                "skills_md": str  # 可供其他Agent使用的SKILL.md内容
            }
        """
        result = {
            "language": None,
            "framework": None,
            "dependencies": [],
            "dev_dependencies": [],
            "install_command": None,
            "build_command": None,
            "skills_md": None
        }
        
        for filename, detector in self.detectors.items():
            file_path = project_path / filename
            if file_path.exists():
                detected = detector(file_path)
                result.update(detected)
                break
        
        # 生成SKILL.md
        result["skills_md"] = self._generate_skills_md(result)
        
        return result
    
    def _detect_nodejs(self, file_path: Path) -> Dict:
        """检测Node.js项目"""
        with open(file_path) as f:
            pkg = json.load(f)
        
        deps = list(pkg.get("dependencies", {}).keys())
        dev_deps = list(pkg.get("devDependencies", {}).keys())
        
        # 检测框架
        framework = None
        if "next" in deps:
            framework = "next"
        elif "nuxt" in deps:
            framework = "nuxt"
        elif "vite" in dev_deps:
            framework = "vite"
        elif "webpack" in dev_deps:
            framework = "webpack"
        elif "express" in deps:
            framework = "express"
        elif "koa" in deps:
            framework = "koa"
        elif "fastify" in deps:
            framework = "fastify"
        
        # 构建命令
        build_cmd = pkg.get("scripts", {}).get("build", "npm run build")
        
        return {
            "language": "nodejs",
            "framework": framework,
            "dependencies": deps,
            "dev_dependencies": dev_deps,
            "install_command": "npm ci",
            "build_command": build_cmd
        }
    
    def _detect_python(self, file_path: Path) -> Dict:
        """检测Python项目"""
        deps = []
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # 处理 requirements.txt
                    if "==" in line:
                        deps.append(line.split("==")[0])
                    elif ">=" in line:
                        deps.append(line.split(">=")[0])
                    elif "<=" in line:
                        deps.append(line.split("<=")[0])
                    else:
                        deps.append(line)
        
        return {
            "language": "python",
            "framework": None,
            "dependencies": deps,
            "dev_dependencies": [],
            "install_command": "pip install -r requirements.txt",
            "build_command": None  # Python项目通常不需要构建
        }
    
    def _detect_fc(self, file_path: Path) -> Dict:
        """检测阿里云FC项目"""
        with open(file_path) as f:
            content = f.read()
        
        runtime = "nodejs18"
        if "python" in content.lower():
            runtime = "python3.9"
        elif "java" in content.lower():
            runtime = "java11"
        elif "php" in content.lower():
            runtime = "php7.2"
        
        return {
            "language": runtime.split("php")[0] if "php" in runtime else runtime.replace("python3.9", "python").replace("java11", "java"),
            "framework": "fc3",
            "dependencies": [],
            "dev_dependencies": [],
            "install_command": None,
            "build_command": None
        }
    
    def _detect_go(self, file_path: Path) -> Dict:
        return {"language": "go", "framework": None, "dependencies": [], "dev_dependencies": [], "install_command": "go mod download"}
    
    def _detect_rust(self, file_path: Path) -> Dict:
        return {"language": "rust", "framework": None, "dependencies": [], "dev_dependencies": [], "install_command": "cargo build"}
    
    def _detect_php(self, file_path: Path) -> Dict:
        return {"language": "php", "framework": None, "dependencies": [], "dev_dependencies": [], "install_command": "composer install"}
    
    def _detect_ruby(self, file_path: Path) -> Dict:
        return {"language": "ruby", "framework": None, "dependencies": [], "dev_dependencies": [], "install_command": "bundle install"}
    
    def _detect_java(self, file_path: Path) -> Dict:
        return {"language": "java", "framework": "spring" if "spring" in file_path.read_text().lower() else None, "dependencies": [], "dev_dependencies": [], "install_command": "mvn install" if "pom.xml" in str(file_path) else "./gradlew build"}
    
    def _generate_skills_md(self, detection: Dict) -> str:
        """生成SKILL.md内容，供其他AI Agent使用"""
        language = detection.get("language", "unknown")
        framework = detection.get("framework")
        deps = detection.get("dependencies", [])
        install_cmd = detection.get("install_command", "")
        build_cmd = detection.get("build_command", "")
        
        return f"""# 项目环境依赖

## 语言和框架
- **语言**: {language}
- **框架**: {framework or "无"}

## 依赖包
{chr(10).join(f'- `{d}`' for d in deps[:20])}
{"- ..." if len(deps) > 20 else ""}

## 安装命令
```bash
{install_cmd}
```

## 构建命令
```bash
{build_cmd or "# 无需构建"}
```

---
*此文件由CI/CD插件自动生成*
"""


class SkillsInstaller:
    """依赖安装器"""
    
    @staticmethod
    def install(detection: Dict, project_path: Path, dry_run: bool = False) -> Dict:
        """
        安装项目依赖
        
        Args:
            detection: SkillsDetector.detect() 的结果
            project_path: 项目路径
            dry_run: 是否仅模拟安装
            
        Returns:
            {"success": bool, "installed": List[str], "failed": List[str], "output": str}
        """
        results = {
            "success": True,
            "installed": [],
            "failed": [],
            "output": ""
        }
        
        install_cmd = detection.get("install_command")
        if not install_cmd:
            results["output"] = "无需安装依赖"
            return results
        
        if dry_run:
            results["output"] = f"[Dry Run] Would run: {install_cmd}"
            return results
        
        try:
            result = subprocess.run(
                install_cmd,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            results["output"] = result.stdout + result.stderr
            
            if result.returncode == 0:
                results["installed"] = detection.get("dependencies", [])
            else:
                results["success"] = False
                results["failed"] = detection.get("dependencies", [])
                
        except subprocess.TimeoutExpired:
            results["success"] = False
            results["output"] = "安装超时 (10分钟)"
        except Exception as e:
            results["success"] = False
            results["output"] = str(e)
        
        return results


# ========== CLI接口 (供AI Agent调用) ==========

def cli_detect(path: str) -> str:
    """CLI: 检测项目依赖"""
    detector = SkillsDetector()
    result = detector.detect(Path(path))
    return json.dumps(result, indent=2, ensure_ascii=False)


def cli_install(path: str, dry_run: bool = False) -> str:
    """CLI: 安装项目依赖"""
    detector = SkillsDetector()
    detection = detector.detect(Path(path))
    
    installer = SkillsInstaller()
    result = installer.install(detection, Path(path), dry_run)
    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Skills检测器CLI")
    parser.add_argument("command", choices=["detect", "install"], help="命令")
    parser.add_argument("path", help="项目路径")
    parser.add_argument("--dry-run", action="store_true", help="仅模拟")
    
    args = parser.parse_args()
    
    if args.command == "detect":
        print(cli_detect(args.path))
    else:
        print(cli_install(args.path, args.dry_run))
