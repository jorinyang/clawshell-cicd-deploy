#!/usr/bin/env python3
"""
单元测试 - Aliyun模块
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.aliyun.oss import OSSManager
from core.aliyun.fc import FCManager


def test_oss_manager_init():
    """测试OSS管理器初始化"""
    print("\n=== 测试 OSSManager 初始化 ===")
    
    # 测试正常初始化
    config = {
        "aliyun": {
            "access_key_id": "test_key",
            "access_key_secret": "test_secret",
            "region": "ap-southeastheast-1",
            "domain": "example.com"
        }
    }
    
    oss = OSSManager(config)
    assert oss.access_key_id == "test_key"
    assert oss.access_key_secret == "test_secret"
    assert oss.region == "ap-southeastheast-1"
    assert oss.domain == "example.com"
    print("✅ OSSManager 初始化正常")
    
    # 测试默认值
    config_minimal = {
        "aliyun": {
            "access_key_id": "test_key",
            "access_key_secret": "test_secret"
        }
    }
    oss2 = OSSManager(config_minimal)
    assert oss2.region == "ap-southeastheast-1"
    print("✅ 默认值处理正常")
    
    return True


def test_oss_manager_methods():
    """测试OSS管理器方法"""
    print("\n=== 测试 OSSManager 方法 ===")
    
    config = {
        "aliyun": {
            "access_key_id": "test_key",
            "access_key_secret": "test_secret",
            "region": "ap-southeastheast-1"
        }
    }
    
    oss = OSSManager(config)
    
    # 测试list_buckets
    buckets = oss.list_buckets()
    assert isinstance(buckets, list)
    print("✅ list_buckets 正常")
    
    # 测试create_bucket
    result = oss.create_bucket("test-bucket")
    assert result["name"] == "test-bucket"
    assert result["status"] == "created"
    print("✅ create_bucket 正常")
    
    # 测试upload_file (模拟)
    from pathlib import Path
    import tempfile
    with tempfile.NamedTemporaryFile() as f:
        result = oss.upload_file("test-bucket", Path(f.name), "test.txt")
        assert result is True
    print("✅ upload_file 正常")
    
    # 测试set_cors
    result = oss.set_cors("test-bucket", {"allowed": ["*"]})
    assert result is True
    print("✅ set_cors 正常")
    
    # 测试bind_domain
    result = oss.bind_domain("test-bucket", "www.example.com")
    assert result is True
    print("✅ bind_domain 正常")
    
    # 测试get_website_url
    url = oss.get_website_url("test-bucket")
    assert "test-bucket" in url
    print("✅ get_website_url 正常")
    
    return True


def test_fc_manager_init():
    """测试FC管理器初始化"""
    print("\n=== 测试 FCManager 初始化 ===")
    
    config = {
        "aliyun": {
            "access_key_id": "test_key",
            "access_key_secret": "test_secret",
            "region": "ap-southeastheast-1"
        }
    }
    
    fc = FCManager(config)
    assert fc.access_key_id == "test_key"
    assert fc.access_key_secret == "test_secret"
    assert fc.region == "ap-southeastheast-1"
    print("✅ FCManager 初始化正常")
    
    return True


def test_fc_manager_methods():
    """测试FC管理器方法"""
    print("\n=== 测试 FCManager 方法 ===")
    
    config = {
        "aliyun": {
            "access_key_id": "test_key",
            "access_key_secret": "test_secret",
            "region": "ap-southeastheast-1"
        }
    }
    
    fc = FCManager(config)
    
    # 测试list_functions
    funcs = fc.list_functions()
    assert isinstance(funcs, list)
    print("✅ list_functions 正常")
    
    # 测试create_function
    result = fc.create_function("test-api", {"runtime": "nodejs18"})
    assert result["name"] == "test-api"
    assert result["runtime"] == "nodejs18"
    print("✅ create_function 正常")
    
    # 测试deploy_function
    from pathlib import Path
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = fc.deploy_function("test-api", Path(tmpdir))
        assert result is True
    print("✅ deploy_function 正常")
    
    # 测试create_trigger
    result = fc.create_trigger("test-api", {"type": "http"})
    assert result is True
    print("✅ create_trigger 正常")
    
    # 测试bind_domain
    result = fc.bind_domain("api.example.com", "test-api")
    assert result is True
    print("✅ bind_domain 正常")
    
    # 测试get_url
    url = fc.get_url("test-api")
    assert "test-api" in url
    print("✅ get_url 正常")
    
    return True


if __name__ == "__main__":
    tests = [
        test_oss_manager_init,
        test_oss_manager_methods,
        test_fc_manager_init,
        test_fc_manager_methods,
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
    print(f"Aliyun模块测试结果: {passed}/{passed+failed} 通过")
    if failed == 0:
        print("✅ 全部测试通过!")
    else:
        print(f"❌ {failed} 个测试失败")
        sys.exit(1)
