#!/usr/bin/env python3
"""
单元测试 - GitHub模块
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.github.repo import GitHubManager


def test_github_manager_init():
    """测试GitHub管理器初始化"""
    print("\n=== 测试 GitHubManager 初始化 ===")
    
    # 测试正常初始化
    config = {
        "github": {
            "token": "test_token_12345",
            "owner": "test_owner"
        }
    }
    
    gh = GitHubManager(config)
    assert gh.token == "test_token_12345"
    assert gh.owner == "test_owner"
    assert gh.api_base == "https://api.github.com"
    print("✅ GitHubManager 初始化正常")
    
    # 测试默认owner
    config_no_owner = {
        "github": {
            "token": "test_token"
        }
    }
    gh2 = GitHubManager(config_no_owner)
    assert gh2.owner == ""
    print("✅ 默认owner处理正常")
    
    return True


def test_github_manager_headers():
    """测试请求头生成"""
    print("\n=== 测试 GitHubManager 请求头 ===")
    
    config = {
        "github": {
            "token": "test_token"
        }
    }
    
    gh = GitHubManager(config)
    headers = gh._headers()
    
    assert "Authorization" in headers
    assert headers["Authorization"] == "token test_token"
    assert "Accept" in headers
    assert "application/vnd.github.v3+json" in headers["Accept"]
    print("✅ 请求头生成正常")
    
    return True


def test_github_manager_api_endpoints():
    """测试API端点"""
    print("\n=== 测试 GitHubManager API端点 ===")
    
    config = {
        "github": {
            "token": "test_token",
            "owner": "testowner"
        }
    }
    
    gh = GitHubManager(config)
    
    # 验证API端点格式
    assert "api.github.com" in gh.api_base
    print("✅ API基础URL正常")
    
    return True


if __name__ == "__main__":
    tests = [
        test_github_manager_init,
        test_github_manager_headers,
        test_github_manager_api_endpoints,
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
    print(f"GitHub模块测试结果: {passed}/{passed+failed} 通过")
    if failed == 0:
        print("✅ 全部测试通过!")
    else:
        print(f"❌ {failed} 个测试失败")
        sys.exit(1)
