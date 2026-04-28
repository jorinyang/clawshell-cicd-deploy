#!/usr/bin/env python3
"""
单元测试 - ConfigManager
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import ConfigManager


def test_config_manager():
    """测试配置管理器"""
    print("\n=== 测试 ConfigManager ===")
    
    # 创建临时配置目录
    with tempfile.TemporaryDirectory() as tmpdir:
        config_manager = ConfigManager(config_dir=Path(tmpdir))
        
        # 测试设置和获取
        config_manager.set("aliyun.access_key_id", "test_key_id")
        config_manager.set("aliyun.access_key_secret", "test_secret")
        config_manager.set("aliyun.region", "ap-southeastheast-1")
        
        assert config_manager.get("aliyun.access_key_id") == "test_key_id"
        assert config_manager.get("aliyun.access_key_secret") == "test_secret"
        assert config_manager.get("aliyun.region") == "ap-southeastheast-1"
        print("✅ 配置设置和获取正常")
        
        # 测试保存和加载
        config_manager.save()
        
        config_manager2 = ConfigManager(config_dir=Path(tmpdir))
        config_manager2.load()
        
        assert config_manager2.get("aliyun.access_key_id") == "test_key_id"
        assert config_manager2.get("aliyun.access_key_secret") == "test_secret"
        print("✅ 配置保存和加载正常")
        
        # 测试默认值
        assert config_manager.get("nonexistent", "default") == "default"
        print("✅ 默认值处理正常")
        
        # 测试嵌套key
        config_manager.set("github.owner", "test_owner")
        assert config_manager.get("github.owner") == "test_owner"
        print("✅ 嵌套key处理正常")
        
    print("✅ ConfigManager 全部测试通过!")
    return True


if __name__ == "__main__":
    test_config_manager()
