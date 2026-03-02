#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 包安装助手 - 核心安装与验证逻辑
"""

import subprocess

from config import MIRRORS, IMPORT_NAME_MAP
def get_import_name(package_name):
    """获取包导入时的模块名"""
    base_name = package_name.split('==')[0].split('>=')[0].split('<=')[0].strip()
    if base_name in IMPORT_NAME_MAP:
        return IMPORT_NAME_MAP[base_name]
    if '-' in base_name:
        return base_name.replace('-', '_')
    return base_name


class PackageValidator:
    """包验证器"""

    @staticmethod
    def get_import_name(package_name):
        return get_import_name(package_name)

    @staticmethod
    def verify_import(python_executable, package_name):
        """通过 subprocess 验证包能否导入"""
        import_name = get_import_name(package_name)
        cmd = [
            python_executable, "-c",
            f"import {import_name}; print(getattr({import_name}, '__version__', 'UnknownVersion'))"
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10,
                encoding='utf-8', errors='replace'
            )
            if result.returncode == 0:
                return True, result.stdout.strip(), import_name
            return False, result.stderr.strip(), import_name
        except subprocess.TimeoutExpired:
            return False, "验证超时", import_name
        except Exception as e:
            return False, str(e), import_name

    @staticmethod
    def verify_pip_list(python_executable, package_name):
        """验证包是否在 pip list 中"""
        try:
            result = subprocess.run(
                [python_executable, "-m", "pip", "list"],
                capture_output=True, text=True, check=True,
                encoding='utf-8', errors='replace'
            )
            base_name = package_name.split('==')[0].split('>=')[0].split('<=')[0].strip().lower()
            return base_name in result.stdout.lower()
        except Exception:
            return False

    @staticmethod
    def run_simple_test(python_executable, package_name):
        """运行简单的功能测试"""
        import_name = get_import_name(package_name)
        test_cases = {
            "pandas": "import pandas as pd; pd.DataFrame({'a': [1,2,3]})",
            "numpy": "import numpy as np; np.array([1,2,3])",
            "requests": "import requests; requests.get('https://httpbin.org/get', timeout=2)",
            "openpyxl": "import openpyxl; openpyxl.Workbook()",
            "xlwings": "import xlwings as xw; xw.App(visible=False)",
            "matplotlib": "import matplotlib.pyplot as plt; plt.figure()",
            "flask": "import flask; flask.Flask(__name__)",
            "django": "import django; django.get_version()",
            "pillow": "from PIL import Image; Image.new('RGB', (100,100))",
            "pyautogui": "import pyautogui; pyautogui.size()",
        }
        for key, test_code in test_cases.items():
            if key in package_name.lower() or key in import_name.lower():
                try:
                    result = subprocess.run(
                        [python_executable, "-c", test_code],
                        capture_output=True, text=True, timeout=10,
                        encoding='utf-8', errors='replace'
                    )
                    if result.returncode == 0:
                        return True, "基础功能测试通过"
                    return False, f"功能测试失败: {result.stderr.strip()[:50]}"
                except subprocess.TimeoutExpired:
                    return False, "功能测试超时"
                except Exception as e:
                    return False, f"功能测试异常: {str(e)[:50]}"
        return None, "无特定测试"


def install_one_package(python_executable, package, mirrors=None, user=True, upgrade=False, timeout=180,
                       on_mirror_try=None, on_mirror_fail=None):
    """
    使用镜像源安装单个包，依次尝试直到成功。

    Args:
        on_mirror_try: 可选回调，尝试每个镜像前调用 on_mirror_try(mirror_name)
        on_mirror_fail: 可选回调，某个镜像失败时调用 on_mirror_fail(mirror_name)

    Returns:
        tuple: (success: bool, mirror_used: str|None)
    """
    if mirrors is None:
        mirrors = MIRRORS

    for mirror_name, mirror_url in mirrors:
        if on_mirror_try:
            on_mirror_try(mirror_name)
        try:
            mirror_host = mirror_url.split("://")[1].split("/")[0]
        except IndexError:
            mirror_host = mirror_url

        cmd = [
            python_executable, "-m", "pip", "install", package,
            "-i", mirror_url, "--trusted-host", mirror_host, "--timeout", str(timeout)
        ]
        if user:
            cmd.append("--user")
        if upgrade:
            cmd.append("--upgrade")

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True,
                          encoding='utf-8', errors='replace', timeout=timeout)
            return True, mirror_name
        except subprocess.TimeoutExpired:
            if on_mirror_fail:
                on_mirror_fail(mirror_name)
            continue
        except subprocess.CalledProcessError as e:
            stderr = e.stderr or ""
            if "No matching distribution" in stderr:
                return False, None
            if on_mirror_fail:
                on_mirror_fail(mirror_name)
            continue
        except Exception:
            if on_mirror_fail:
                on_mirror_fail(mirror_name)
            continue

    return False, None


def install_packages_cli(python_executable, packages, mirrors=None, user=True, upgrade=False):
    """
    CLI 模式：批量安装包，打印进度到 stdout。
    返回 (success_count, fail_count, mirror_used)
    """
    if mirrors is None:
        mirrors = MIRRORS

    success_count = 0
    fail_count = 0
    mirror_used = None

    for package in packages:
        print(f"\n正在安装: {package}")
        success, used = install_one_package(python_executable, package, mirrors, user, upgrade)
        if success:
            print(f"  ✓ {package} 安装成功！")
            success_count += 1
            if mirror_used is None:
                mirror_used = used
        else:
            print(f"  ✗ {package} 安装失败，所有镜像源都尝试过了")
            fail_count += 1

    return success_count, fail_count, mirror_used
