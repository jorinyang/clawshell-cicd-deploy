#!/usr/bin/env python3
"""
单元测试 - Supabase模块
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.supabase.client import SupabaseManager


def test_supabase_manager_init():
    """测试Supabase管理器初始化"""
    print("\n=== 测试 SupabaseManager 初始化 ===")
    
    # 测试正常初始化
    config = {
        "supabase": {
            "url": "https://test-project.supabase.co",
            "anon_key": "test_anon_key",
            "service_role_key": "test_service_role_key"
        }
    }
    
    sb = SupabaseManager(config)
    assert sb.url == "https://test-project.supabase.co"
    assert sb.anon_key == "test_anon_key"
    assert sb.service_role_key == "test_service_role_key"
    print("✅ SupabaseManager 初始化正常")
    
    # 测试环境变量备用
    import os
    os.environ["SUPABASE_URL"] = "https://env-project.supabase.co"
    config_empty = {"supabase": {}}
    sb2 = SupabaseManager(config_empty)
    assert sb2.url == "https://env-project.supabase.co"
    del os.environ["SUPABASE_URL"]
    print("✅ 环境变量备用正常")
    
    return True


def test_supabase_manager_headers():
    """测试请求头生成"""
    print("\n=== 测试 SupabaseManager 请求头 ===")
    
    config = {
        "supabase": {
            "url": "https://test.supabase.co",
            "anon_key": "anon_key_123",
            "service_role_key": "service_role_456"
        }
    }
    
    sb = SupabaseManager(config)
    
    # 测试anon headers
    anon_headers = sb._headers(admin=False)
    assert anon_headers["apikey"] == "anon_key_123"
    assert "Bearer" in anon_headers["Authorization"]
    print("✅ Anon请求头正常")
    
    # 测试admin headers
    admin_headers = sb._headers(admin=True)
    assert admin_headers["apikey"] == "service_role_456"
    assert "Bearer" in admin_headers["Authorization"]
    print("✅ Admin请求头正常")
    
    return True


def test_supabase_manager_methods():
    """测试Supabase管理器方法"""
    print("\n=== 测试 SupabaseManager 方法 ===")
    
    config = {
        "supabase": {
            "url": "https://test.supabase.co",
            "anon_key": "anon_key",
            "service_role_key": "service_role_key"
        }
    }
    
    sb = SupabaseManager(config)
    
    # 测试list_tables
    tables = sb.list_tables()
    assert isinstance(tables, list)
    print("✅ list_tables 正常")
    
    # 测试create_table (模拟)
    result = sb.create_table("test_table", {"id": "int", "name": "text"})
    assert result is True
    print("✅ create_table 正常")
    
    # 测试execute_sql (模拟)
    result = sb.execute_sql("CREATE TABLE test (id int);")
    assert result is True
    print("✅ execute_sql 正常")
    
    return True


if __name__ == "__main__":
    tests = [
        test_supabase_manager_init,
        test_supabase_manager_headers,
        test_supabase_manager_methods,
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
    print(f"Supabase模块测试结果: {passed}/{passed+failed} 通过")
    if failed == 0:
        print("✅ 全部测试通过!")
    else:
        print(f"❌ {failed} 个测试失败")
        sys.exit(1)
