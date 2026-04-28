#!/usr/bin/env python3
"""
单元测试 - CLI接口
"""

import sys
import json
import subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_cli_help():
    """测试CLI帮助"""
    print("\n=== 测试 CLI 帮助 ===")
    
    result = subprocess.run(
        [sys.executable, "cicd.py", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    assert result.returncode == 0
    assert "init" in result.stdout
    assert "deploy" in result.stdout
    assert "status" in result.stdout
    assert "watch" in result.stdout
    assert "chat" in result.stdout
    print("✅ CLI帮助正常")
    print(f"   可用命令: init, deploy, status, watch, chat")
    
    return True


def test_cli_deploy_help():
    """测试deploy子命令帮助"""
    print("\n=== 测试 CLI Deploy帮助 ===")
    
    result = subprocess.run(
        [sys.executable, "cicd.py", "deploy", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    assert result.returncode == 0
    assert "--path" in result.stdout or "-p" in result.stdout
    print("✅ Deploy子命令帮助正常")
    
    return True


def test_cli_chat_help():
    """测试chat子命令帮助"""
    print("\n=== 测试 CLI Chat帮助 ===")
    
    result = subprocess.run(
        [sys.executable, "cicd.py", "chat", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    assert result.returncode == 0
    print("✅ Chat子命令帮助正常")
    
    return True


def test_cli_status():
    """测试status命令"""
    print("\n=== 测试 CLI Status ===")
    
    result = subprocess.run(
        [sys.executable, "cicd.py", "status"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    # status应该能执行(即使没有配置)
    assert result.returncode in [0, 1]
    print(f"✅ Status命令执行正常 (exit code: {result.returncode})")
    
    return True


def test_skills_detector_cli():
    """测试SkillsDetector CLI"""
    print("\n=== 测试 SkillsDetector CLI ===")
    
    # 测试help
    result = subprocess.run(
        [sys.executable, "-c", 
         "from core.deployer.skills_detector import cli_detect; print(cli_detect('.'))"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "language" in data
    assert "dependencies" in data
    print(f"✅ SkillsDetector CLI正常 (检测到: {data.get('language', 'None')})")
    
    return True


if __name__ == "__main__":
    tests = [
        test_cli_help,
        test_cli_deploy_help,
        test_cli_chat_help,
        test_cli_status,
        test_skills_detector_cli,
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
    print(f"CLI测试结果: {passed}/{passed+failed} 通过")
    if failed == 0:
        print("✅ 全部测试通过!")
    else:
        print(f"❌ {failed} 个测试失败")
        sys.exit(1)
