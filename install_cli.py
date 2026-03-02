#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 包安装助手 - 命令行版 (CLI)
支持从命令行参数或 requirements.txt 安装包
"""

import sys
import argparse
from pathlib import Path
from pip_core import install_packages_cli, PackageValidator

def load_packages_from_requirements(filepath):
    """从 requirements.txt 解析包列表（忽略空行、注释、-r/-e 引用）"""
    packages = []
    path = Path(filepath)
    if not path.exists():
        return packages
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('-r ') or line.startswith('-e '):
                continue
            packages.append(line)
    return packages


def main():
    parser = argparse.ArgumentParser(description='Python 包安装助手 - 使用国内镜像源')
    parser.add_argument('packages', nargs='*', help='要安装的包名，如: pandas openpyxl requests')
    parser.add_argument('-r', '--requirements', metavar='FILE',
                        help='从 requirements.txt 文件安装')
    parser.add_argument('--no-user', action='store_true', help='不使用 --user 安装')
    parser.add_argument('--upgrade', action='store_true', help='升级已安装的包')
    parser.add_argument('--python', default=sys.executable, help='Python 解释器路径')
    parser.add_argument('--verify', action='store_true', help='安装后验证')
    args = parser.parse_args()

    packages = list(args.packages)

    if args.requirements:
        from_file = load_packages_from_requirements(args.requirements)
        packages.extend(from_file)
        if from_file:
            print(f"从 {args.requirements} 加载了 {len(from_file)} 个包")

    if not packages:
        parser.print_help()
        print("\n示例:")
        print("  python install_cli.py pandas openpyxl")
        print("  python install_cli.py -r requirements.txt")
        sys.exit(1)

    print("Python 包安装工具 - 使用国内镜像源")
    print("=" * 50)

    success, fail, mirror = install_packages_cli(
        args.python, packages,
        user=not args.no_user,
        upgrade=args.upgrade
    )

    if args.verify and success > 0:
        print("\n" + "=" * 50)
        print("验证安装结果:")
        validator = PackageValidator()
        for pkg in packages:
            can_import, ver_or_err, _ = validator.verify_import(args.python, pkg)
            status = f"✓ {pkg} ({ver_or_err})" if can_import else f"✗ {pkg} 导入失败"
            print(f"  {status}")

    print("\n" + "=" * 50)
    print(f"完成: {success} 成功, {fail} 失败")
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
