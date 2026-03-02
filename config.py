#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 包安装助手 - 共用配置模块
"""

import sys

# ============ 镜像源配置 ============
MIRRORS = [
    ("清华源", "https://pypi.tuna.tsinghua.edu.cn/simple"),
    ("阿里云", "https://mirrors.aliyun.com/pypi/simple/"),
    ("中科大", "https://pypi.mirrors.ustc.edu.cn/simple/"),
    ("腾讯云", "https://mirrors.cloud.tencent.com/pypi/simple"),
    ("豆瓣源", "http://pypi.douban.com/simple/"),
    ("华为云", "https://repo.huaweicloud.com/repository/pypi/simple"),
    ("官方源", "https://pypi.org/simple"),
]

# ============ 快捷包组 ============
PACKAGE_GROUPS = {
    "📊 数据处理": ["pandas", "numpy", "matplotlib", "scipy"],
    "📗 表格处理": ["xlwings", "openpyxl", "xlrd", "xlsxwriter"],
    "🕷 网络爬虫": ["requests", "beautifulsoup4", "selenium"],
    "🌐 网页开发": ["flask", "django", "fastapi", "uvicorn"],
    "🤖 机器学习": ["torch", "tensorflow", "transformers", "scikit-learn"],
    "🖱 自动化": ["pyautogui", "windnd", "pywin32", "keyboard"],
    "📄 办公文档": ["python-docx", "python-pptx", "pdfplumber", "PyPDF2"],
}

# ============ 包名到导入名的映射 ============
IMPORT_NAME_MAP = {
    "beautifulsoup4": "bs4",
    "pillow": "PIL",
    "pyyaml": "yaml",
    "python-docx": "docx",
    "python-pptx": "pptx",
    "scikit-learn": "sklearn",
    "opencv-python": "cv2",
    "pywin32": "win32api",
    "windnd": "windnd",
}

# ============ 默认 Python 解释器 ============
DEFAULT_PYTHON_PATH = sys.executable
