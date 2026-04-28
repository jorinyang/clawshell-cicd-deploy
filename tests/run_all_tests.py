#!/usr/bin/env python3
"""
单元测试运行器 - CI/CD Deploy Plugin
"""

import sys
import subprocess
from pathlib import Path
import json


def run_test_file(test_file: Path) -> tuple:
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"运行: {test_file.name}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable, str(test_file)],
        capture_output=True,
        text=True,
        cwd=test_file.parent.parent
    )
    
    return result.returncode, result.stdout, result.stderr


def main():
    """运行所有测试"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║           CI/CD Deploy Plugin - 单元测试                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
    """)
    
    test_dir = Path(__file__).parent
    
    # 收集测试文件
    test_files = sorted(test_dir.glob("test_*.py"))
    
    print(f"发现 {len(test_files)} 个测试文件:")
    for tf in test_files:
        print(f"  - {tf.name}")
    print()
    
    # 运行测试
    results = []
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        if test_file.name == "__init__.py" or test_file.name == "run_all_tests.py":
            continue
            
        returncode, stdout, stderr = run_test_file(test_file)
        
        # 解析输出
        if "通过" in stdout or "pass" in stdout.lower():
            total_passed += 1
            results.append((test_file.name, "PASS", stdout))
        elif returncode == 0:
            total_passed += 1
            results.append((test_file.name, "PASS", ""))
        else:
            total_failed += 1
            results.append((test_file.name, "FAIL", stderr))
    
    # 输出汇总
    print(f"""
╠══════════════════════════════════════════════════════════════════════════════╣
║                          测试结果汇总                               ║
╠══════════════════════════════════════════════════════════════════════════════╣""")
    
    for name, status, _ in results:
        icon = "✅" if status == "PASS" else "❌"
        print(f"║  {icon} {name:<40} {status:<10} ║")
    
    print(f"""╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                      ║""")
    
    if total_failed == 0:
        print(f"""║           🎉 全部 {total_passed} 个测试通过! 🎉                           ║
╚══════════════════════════════════════════════════════════════════════════════╝""")
        return 0
    else:
        print(f"""║           ❌ {total_failed} 个测试失败, {total_passed} 个通过                        ║
╚══════════════════════════════════════════════════════════════════════════════╝""")
        return 1


if __name__ == "__main__":
    sys.exit(main())
