#!/usr/bin/env python3
"""
单元测试 - DeployOrchestrator
"""

import sys
import json
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.deployer.orchestrator import DeployOrchestrator


def test_orchestrator_init():
    """测试编排器初始化"""
    print("\n=== 测试 DeployOrchestrator 初始化 ===")
    
    config = {
        "aliyun": {
            "access_key_id": "test_key",
            "access_key_secret": "test_secret",
            "region": "ap-southeastheast-1",
            "domain": "example.com"
        },
        "github": {
            "token": "test_token"
        },
        "supabase": {
            "url": "https://test.supabase.co",
            "anon_key": "anon",
            "service_role_key": "service"
        }
    }
    
    orch = DeployOrchestrator(config)
    assert orch.config == config
    assert orch.oss is not None
    assert orch.fc is not None
    assert orch.supabase is not None
    print("✅ DeployOrchestrator 初始化正常")
    
    return True


def test_analyze_nodejs_project():
    """测试Node.js项目分析"""
    print("\n=== 测试 项目分析 - Node.js ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        # 创建package.json
        package_json = {
            "name": "test-vue-app",
            "dependencies": {
                "vue": "^3.0.0",
                "vite": "^5.0.0"
            },
            "devDependencies": {
                "@vitejs/plugin-vue": "^5.0.0"
            }
        }
        
        with open(project_dir / "package.json", "w") as f:
            json.dump(package_json, f)
        
        orch = DeployOrchestrator({})
        result = orch._analyze_project(project_dir)
        
        assert result["language"] == "nodejs"
        assert result["framework"] in ["vite", "vue"]
        assert len(result["dependencies"]) > 0
        print(f"✅ 项目类型: {result['type']}")
        print(f"✅ 框架: {result['framework']}")
        print(f"✅ 依赖数: {len(result['dependencies'])}")
    
    return True


def test_analyze_express_project():
    """测试Express后端项目分析"""
    print("\n=== 测试 项目分析 - Express后端 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        # 创建package.json
        package_json = {
            "name": "test-api",
            "dependencies": {
                "express": "^4.18.0",
                "cors": "^2.8.0"
            }
        }
        
        with open(project_dir / "package.json", "w") as f:
            json.dump(package_json, f)
        
        orch = DeployOrchestrator({})
        result = orch._analyze_project(project_dir)
        
        assert result["language"] == "nodejs"
        assert result["type"] == "node"
        print(f"✅ 项目类型: {result['type']}")
    
    return True


def test_analyze_python_project():
    """测试Python项目分析"""
    print("\n=== 测试 项目分析 - Python ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        # 创建requirements.txt
        with open(project_dir / "requirements.txt", "w") as f:
            f.write("flask==2.0.0\nrequests>=2.25.0\n")
        
        orch = DeployOrchestrator({})
        result = orch._analyze_project(project_dir)
        
        assert result["language"] == "python"
        assert result["type"] == "python"
        print(f"✅ 项目类型: {result['type']}")
    
    return True


def test_analyze_fc_project():
    """测试FC项目分析"""
    print("\n=== 测试 项目分析 - FC项目 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        # 创建s.yaml
        with open(project_dir / "s.yaml", "w") as f:
            f.write("edition: 1.0.0\nname: fc-app\n")
        
        orch = DeployOrchestrator({})
        result = orch._analyze_project(project_dir)
        
        assert result["language"] == "nodejs"
        assert result["framework"] == "fc3"
        assert result["type"] == "fc"
        print(f"✅ 项目类型: {result['type']}")
        print(f"✅ 框架: {result['framework']}")
    
    return True


def test_generate_workflow():
    """测试Workflow生成"""
    print("\n=== 测试 Workflow生成 ===")
    
    orch = DeployOrchestrator({})
    workflow = orch._generate_workflow("test-project", {
        "type": "node",
        "framework": "express"
    })
    
    assert "Deploy to Aliyun" in workflow
    assert "nodejs" in workflow.lower() or "node" in workflow.lower()
    assert "oss" in workflow.lower() or "OSS" in workflow
    print("✅ Workflow生成正常")
    print(f"   长度: {len(workflow)} 字符")
    
    return True


def test_deploy_static_project():
    """测试静态项目部署 (模拟)"""
    print("\n=== 测试 静态项目部署 (模拟) ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        # 创建模拟项目
        (project_dir / "index.html").write_text("<html></html>")
        dist_dir = project_dir / "dist"
        dist_dir.mkdir()
        (dist_dir / "index.html").write_text("<html><body>Hello</body></html>")
        (dist_dir / "app.js").write_text("console.log('test');")
        
        config = {
            "aliyun": {
                "access_key_id": "test_key",
                "access_key_secret": "test_secret",
                "region": "ap-southeastheast-1"
            }
        }
        
        orch = DeployOrchestrator(config)
        result = orch.deploy(project_dir, {"name": "test-static"})
        
        assert result["success"] is True
        assert result["type"] == "static"
        assert "bucket" in result["details"]
        print(f"✅ 部署成功: {result['url']}")
    
    return True


if __name__ == "__main__":
    tests = [
        test_orchestrator_init,
        test_analyze_nodejs_project,
        test_analyze_express_project,
        test_analyze_python_project,
        test_analyze_fc_project,
        test_generate_workflow,
        test_deploy_static_project,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} 失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"DeployOrchestrator测试结果: {passed}/{passed+failed} 通过")
    if failed == 0:
        print("✅ 全部测试通过!")
    else:
        print(f"❌ {failed} 个测试失败")
        sys.exit(1)
