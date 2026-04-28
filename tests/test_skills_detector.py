#!/usr/bin/env python3
"""
单元测试 - SkillsDetector
"""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.deployer.skills_detector import SkillsDetector, SkillsInstaller


def test_skills_detector_nodejs():
    """测试Node.js项目检测"""
    print("\n=== 测试 SkillsDetector - Node.js ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        # 创建package.json
        package_json = {
            "name": "test-project",
            "dependencies": {
                "express": "^4.18.0",
                "axios": "^1.0.0"
            },
            "devDependencies": {
                "vite": "^5.0.0",
                "typescript": "^5.0.0"
            },
            "scripts": {
                "build": "vite build",
                "dev": "vite"
            }
        }
        
        with open(project_dir / "package.json", "w") as f:
            json.dump(package_json, f)
        
        detector = SkillsDetector()
        result = detector.detect(project_dir)
        
        assert result["language"] == "nodejs"
        assert result["framework"] == "express"
        assert "express" in result["dependencies"]
        assert "axios" in result["dependencies"]
        assert "vite" in result["dev_dependencies"]
        assert result["install_command"] == "npm ci"
        assert result["build_command"] == "vite build"
        print("✅ Node.js项目检测正常")
        
        # 验证skills_md生成
        assert "test-project" in result["skills_md"] or "nodejs" in result["skills_md"].lower()
        print("✅ Skills.md生成正常")
    
    return True


def test_skills_detector_python():
    """测试Python项目检测"""
    print("\n=== 测试 SkillsDetector - Python ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        # 创建requirements.txt
        requirements = """
flask==2.0.0
requests>=2.25.0
numpy>=1.20.0
# 这是一个注释
pandas
        """
        
        with open(project_dir / "requirements.txt", "w") as f:
            f.write(requirements)
        
        detector = SkillsDetector()
        result = detector.detect(project_dir)
        
        assert result["language"] == "python"
        assert "flask" in result["dependencies"]
        assert "requests" in result["dependencies"]
        assert "numpy" in result["dependencies"]
        assert result["install_command"] == "pip install -r requirements.txt"
        print("✅ Python项目检测正常")
    
    return True


def test_skills_detector_fc():
    """测试FC项目检测"""
    print("\n=== 测试 SkillsDetector - FC项目 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        # 创建s.yaml
        s_yaml = """
edition: 1.0.0
name: fc-app
services:
  frontend:
    component: website
"""
        
        with open(project_dir / "s.yaml", "w") as f:
            f.write(s_yaml)
        
        detector = SkillsDetector()
        result = detector.detect(project_dir)
        
        assert result["language"] == "nodejs"
        assert result["framework"] == "fc3"
        print("✅ FC项目检测正常")
    
    return True


def test_skills_detector_empty():
    """测试空项目检测"""
    print("\n=== 测试 SkillsDetector - 空项目 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        detector = SkillsDetector()
        result = detector.detect(project_dir)
        
        assert result["language"] is None
        assert result["framework"] is None
        assert result["dependencies"] == []
        print("✅ 空项目检测正常 (返回None)")
    
    return True


def test_skills_detector_detectors_map():
    """测试detectors映射"""
    print("\n=== 测试 SkillsDetector - 探测文件映射 ===")
    
    detector = SkillsDetector()
    
    assert "package.json" in detector.detectors
    assert "requirements.txt" in detector.detectors
    assert "s.yaml" in detector.detectors
    assert "Pipfile" in detector.detectors
    assert "go.mod" in detector.detectors
    print("✅ 探测文件映射完整")
    
    return True


if __name__ == "__main__":
    tests = [
        test_skills_detector_nodejs,
        test_skills_detector_python,
        test_skills_detector_fc,
        test_skills_detector_empty,
        test_skills_detector_detectors_map,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} 失败: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"SkillsDetector 测试结果: {passed}/{passed+failed} 通过")
    if failed == 0:
        print("✅ 全部测试通过!")
    else:
        print(f"❌ {failed} 个测试失败")
        sys.exit(1)
