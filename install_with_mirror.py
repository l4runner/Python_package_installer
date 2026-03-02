#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 包安装助手 - GUI 主程序
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font, filedialog
import threading
from pathlib import Path
import json
import time

from config import MIRRORS, PACKAGE_GROUPS, DEFAULT_PYTHON_PATH
from pip_core import PackageValidator, install_one_package

print(f"✅ 使用默认 Python 解释器: {DEFAULT_PYTHON_PATH}")


class PipInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python包安装助手")
        self.root.minsize(600, 500)
        self.root.geometry("850x800")
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        self.setup_styles()
        self.create_widgets()
        self.bind_mousewheel()
        self.history_file = Path.home() / ".pip_gui_history.json"
        self.load_history()
        self.validator = PackageValidator()

    def _is_over_toplevel(self, widget):
        """判断事件是否发生在附属 Toplevel 内，若是则主窗口不应滚动"""
        try:
            w = widget
            while w:
                if w == self.root:
                    return False
                if isinstance(w, tk.Toplevel):
                    return True
                pid = w.winfo_parent()
                w = self.root.nametowidget(pid) if pid else None
        except Exception:
            pass
        return False

    def bind_mousewheel(self):
        """绑定鼠标滚轮事件（仅在主窗口内滚动，附属 Toplevel 内不干扰）"""
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.main_canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.main_canvas.bind_all("<Button-5>", self._on_mousewheel_linux)
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')

        self.bg_color = '#f5f6fa'
        self.root.configure(bg=self.bg_color)

    def create_widgets(self):
        """创建界面组件"""

        # ============ 顶部标题 ============
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=70)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="🐍 Python 包安装助手",
            bg='#2c3e50',
            fg='white',
            font=('Microsoft YaHei UI', 20, 'bold')
        )
        title_label.pack(expand=True)

        # ============ 主内容区域 ============
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill='both', expand=True)
        self.main_canvas = tk.Canvas(container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.main_canvas.yview)
        self.main_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.main_canvas.configure(yscrollcommand=scrollbar.set)
        self.main_frame = tk.Frame(self.main_canvas, bg=self.bg_color)
        self.window_id = self.main_canvas.create_window((0, 0), window=self.main_frame, anchor='nw')
        self.main_frame.bind('<Configure>', self.on_frame_configure)
        self.main_canvas.bind('<Configure>', self.on_canvas_configure)

        # ============ 包名输入区域 ============
        input_frame = tk.LabelFrame(
            self.main_frame,
            text="📦 要安装的包",
            bg=self.bg_color,
            font=('Microsoft YaHei UI', 10, 'bold'),
            padx=15, pady=15
        )
        input_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(input_frame, text="包名 (多个包用空格分隔):", bg=self.bg_color, font=('Microsoft YaHei UI', 9)).pack(
            anchor='w')

        entry_row = tk.Frame(input_frame, bg=self.bg_color)
        entry_row.pack(fill='x', pady=(8, 10))

        self.package_entry = tk.Entry(entry_row, font=('Consolas', 11), width=50)
        self.package_entry.pack(side='left', fill='x', expand=True)
        self.package_entry.insert(0, "pandas openpyxl requests")

        tk.Button(
            entry_row,
            text="📁 导入 requirements.txt",
            command=self.load_requirements,
            bg='#16a085', fg='white',
            relief='flat', padx=10, pady=4,
            cursor='hand2',
            font=('Microsoft YaHei UI', 9)
        ).pack(side='left', padx=(10, 0))

        # 快速选择常用包
        quick_frame = tk.Frame(input_frame, bg=self.bg_color)
        quick_frame.pack(fill='x', pady=(5, 0))

        tk.Label(quick_frame, text="快捷组:", bg=self.bg_color, font=('Microsoft YaHei UI', 9, 'bold')).pack(
            side='left', padx=(0, 10))
        btn_container = tk.Frame(quick_frame, bg=self.bg_color)
        btn_container.pack(side='left', fill='x', expand=True)
        button_config = {
            'bg': '#3498db',
            'fg': 'white',
            'activebackground': '#2980b9',
            'activeforeground': 'white',
            'relief': 'flat',
            'width': 20,
            'height': 1,
            'font': ('Microsoft YaHei UI', 9)
        }
        group_names = list(PACKAGE_GROUPS.keys())
        for i, group_name in enumerate(group_names):
            row = i // 4
            col = i % 4

            btn = tk.Button(
                btn_container,
                text=group_name,
                command=lambda g=group_name: self.select_group(g),
                **button_config
            )
            btn.grid(row=row, column=col, padx=3, pady=2, sticky='w')
        last_row_count = len(group_names) % 4
        if last_row_count > 0:
            for col in range(last_row_count, 4):
                placeholder = tk.Frame(btn_container, width=80, height=25, bg=self.bg_color)
                placeholder.grid(row=row, column=col, padx=3, pady=2)

        # ============ 镜像源信息显示 ============
        mirror_frame = tk.LabelFrame(
            self.main_frame,
            text="🌐 镜像源信息",
            bg=self.bg_color,
            font=('Microsoft YaHei UI', 10, 'bold'),
            padx=10, pady=8
        )
        mirror_frame.pack(fill='x', padx=20, pady=5)

        info_text = "安装时会自动尝试以下镜像源（按顺序尝试，直到成功）："
        tk.Label(mirror_frame, text=info_text, bg=self.bg_color, font=('Microsoft YaHei UI', 9)).pack(anchor='w')

        # 改为一行显示所有镜像源
        mirror_names = [name for name, _ in MIRRORS]
        mirror_text = " → ".join(mirror_names) + " → 官方源"
        tk.Label(
            mirror_frame,
            text=mirror_text,
            bg=self.bg_color,
            font=('Microsoft YaHei UI', 8),
            fg='#555'
        ).pack(anchor='w', pady=(2, 0))

        # ============ 安装选项 ============
        option_frame = tk.LabelFrame(
            self.main_frame,
            text="⚙️ 安装选项",
            bg=self.bg_color,
            font=('Microsoft YaHei UI', 10, 'bold'),
            padx=15, pady=15
        )
        option_frame.pack(fill='x', padx=20, pady=10)

        self.upgrade_var = tk.BooleanVar(value=False)
        self.user_var = tk.BooleanVar(value=True)
        self.verify_var = tk.BooleanVar(value=True)
        self.custom_python_path_var = tk.StringVar(value="")


        tk.Checkbutton(
            option_frame,
            text="升级已安装的包 (--upgrade)",
            variable=self.upgrade_var,
            bg=self.bg_color,
            font=('Microsoft YaHei UI', 9),
            selectcolor='#dfe6e9'
        ).pack(anchor='w', pady=2)

        tk.Checkbutton(
            option_frame,
            text="仅当前用户安装 (user) [避免权限错误]",
            variable=self.user_var,
            bg=self.bg_color,
            font=('Microsoft YaHei UI', 9),
            selectcolor='#dfe6e9'
        ).pack(anchor='w', pady=2)

        tk.Checkbutton(
            option_frame,
            text="安装后验证 (检查包是否能导入)",
            variable=self.verify_var,
            bg=self.bg_color,
            font=('Microsoft YaHei UI', 9, 'bold'),
            selectcolor='#dfe6e9'
        ).pack(anchor='w', pady=2)

        path_frame = tk.Frame(option_frame, bg=self.bg_color)
        path_frame.pack(fill='x', pady=(10, 0))

        tk.Label(
            path_frame,
            text="自定义 Python 路径 (留空则使用当前环境):",
            bg=self.bg_color,
            font=('Microsoft YaHei UI', 9)
        ).pack(anchor='w')

        path_entry_frame = tk.Frame(path_frame, bg=self.bg_color)
        path_entry_frame.pack(fill='x', pady=(5, 0))

        self.python_path_entry = tk.Entry(
            path_entry_frame,
            textvariable=self.custom_python_path_var,
            font=('Consolas', 9),
            width=60
        )
        self.python_path_entry.pack(side='left', fill='x', expand=True)

        tk.Button(
            path_entry_frame,
            text="...",
            command=self.browse_python,
            bg='#ecf0f1', fg='#2c3e50',
            relief='flat', padx=5, pady=2
        ).pack(side='left', padx=(5, 0))

        tk.Label(
            path_frame,
            text=f"💡 当前运行环境：{sys.executable}",
            bg=self.bg_color,
            font=('Microsoft YaHei UI', 8),
            fg='#7f8c8d'
        ).pack(anchor='w', pady=(5, 0))


        # ============ 操作按钮 ============
        btn_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        btn_frame.pack(fill='x', padx=20, pady=15)

        self.install_btn = tk.Button(
            btn_frame,
            text="🚀 开始安装",
            command=self.start_install,
            bg='#27ae60', fg='white',
            font=('Microsoft YaHei UI', 12, 'bold'),
            relief='flat', padx=30, pady=10,
            cursor='hand2'
        )
        self.install_btn.pack(side='left', padx=5)

        tk.Button(
            btn_frame,
            text="🧹 清空日志",
            command=self.clear_output,
            bg='#95a5a6', fg='white',
            relief='flat', padx=20, pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5)

        tk.Button(
            btn_frame,
            text="📋 历史记录",
            command=self.show_history,
            bg='#2980b9', fg='white',
            relief='flat', padx=20, pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5)

        tk.Button(
            btn_frame,
            text="🔍 单独验证",
            command=self.verify_only,
            bg='#9b59b6', fg='white',
            relief='flat', padx=20, pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5)

        # ============ 输出区域 ============
        output_frame = tk.LabelFrame(
            self.main_frame,
            text="📝 安装日志",
            bg=self.bg_color,
            font=('Microsoft YaHei UI', 10, 'bold'),
            padx=15, pady=15
        )
        output_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=15,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#2d2d2d', fg='#d4d4d4',
            insertbackground='white',
            relief='flat',
            padx=10, pady=10
        )
        self.output_text.pack(fill='both', expand=True)

        # 配置 tag 样式
        self.output_text.tag_config('success', foreground='#4ec9b0')
        self.output_text.tag_config('error', foreground='#f48771')
        self.output_text.tag_config('info', foreground='#9cdcfe')
        self.output_text.tag_config('warning', foreground='#ce9178')
        self.output_text.tag_config('cmd', foreground='#dcdcaa')
        self.output_text.tag_config('mirror_try', foreground='#c586c0')
        self.output_text.tag_config('verify_success', foreground='#4ec9b0', font=('Consolas', 10, 'bold'))
        self.output_text.tag_config('verify_fail', foreground='#f48771', font=('Consolas', 10, 'bold'))

        # ============ 底部状态栏 ============
        self.status_frame = tk.Frame(self.root, bg='#34495e', height=40)
        self.status_frame.pack(fill='x', side='bottom')
        self.status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            self.status_frame,
            text="就绪 | 检测到 Python: " + sys.version.split()[0],
            bg='#34495e', fg='#ecf0f1',
            font=('Microsoft YaHei UI', 9),
            anchor='w',
            padx=15
        )
        self.status_label.pack(side='left', fill='x', expand=True)

        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            mode='indeterminate',
            length=200
        )
        self.progress_bar.pack(side='right', padx=15, pady=10)

    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件（附属窗口内不滚动主界面）"""
        if self._is_over_toplevel(getattr(event, "widget", None)):
            return
        self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        """Linux 滚轮（附属窗口内不滚动主界面）"""
        if self._is_over_toplevel(getattr(event, "widget", None)):
            return
        if event.num == 4:
            self.main_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.main_canvas.yview_scroll(1, "units")

    def on_frame_configure(self, event):
        """重置滚动区域"""
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox('all'))

    def on_canvas_configure(self, event):
        """调整内部框架宽度以匹配 Canvas"""
        self.main_canvas.itemconfig(self.window_id, width=event.width)

    def load_requirements(self):
        """从 requirements.txt 导入包列表"""
        filepath = filedialog.askopenfilename(
            title="选择 requirements.txt",
            filetypes=[("requirements.txt", "requirements.txt"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return
        try:
            packages = []
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('-r ') or line.startswith('-e '):
                        continue
                    packages.append(line)
            if packages:
                self.package_entry.delete(0, tk.END)
                self.package_entry.insert(0, ' '.join(packages))
                self.log(f"📁 已从 {filepath} 导入 {len(packages)} 个包", 'info')
                messagebox.showinfo("导入成功", f"已导入 {len(packages)} 个包")
            else:
                messagebox.showwarning("提示", "文件中没有有效的包")
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败: {e}")

    def select_group(self, group_name):
        """选择常用包组"""
        packages = PACKAGE_GROUPS[group_name]
        current = self.package_entry.get().strip()
        if current:
            self.package_entry.insert(tk.END, " " + ' '.join(packages))
        else:
            self.package_entry.delete(0, tk.END)
            self.package_entry.insert(0, ' '.join(packages))

    def browse_python(self):
        """浏览选择 python.exe"""
        filename = filedialog.askopenfilename(
            title="选择 Python 解释器",
            filetypes=[("Python Executable", "python.exe"), ("All Files", "*.*")],
            initialdir=os.environ.get('LOCALAPPDATA', 'C:\\') + '\\Programs\\Python'
        )
        if filename:
            self.custom_python_path_var.set(filename)
            self.log(f"📍 已选择 Python: {filename}", 'info')

    def get_python_executable(self):
        """获取实际要使用的 Python 路径"""
        custom_path = self.custom_python_path_var.get().strip()
        if custom_path and os.path.exists(custom_path):
            return custom_path
        return DEFAULT_PYTHON_PATH

    def log(self, message, tag=None):
        """输出日志到文本框"""
        self.output_text.insert(tk.END, message + '\n', tag)
        self.output_text.see(tk.END)
        self.root.update_idletasks()

    def clear_output(self):
        """清空输出"""
        self.output_text.delete(1.0, tk.END)

    def load_history(self):
        """加载安装历史"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                self.history = {"installs": []}
                self.log(f"读取历史文件失败: {e}", 'warning')
        else:
            self.history = {"installs": []}

    def save_history(self, packages, success_count, fail_count, mirror_used, verification_results=None):
        """保存安装历史"""
        record = {
            "time": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "packages": packages,
            "success": success_count,
            "fail": fail_count,
            "mirror_used": mirror_used,
        }

        if verification_results:
            record["verification"] = verification_results

        self.history["installs"].append(record)
        if len(self.history["installs"]) > 50:
            self.history["installs"] = self.history["installs"][-50:]

        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"保存历史失败: {e}", 'error')

    def show_history(self):
        """显示安装历史"""
        history_win = tk.Toplevel(self.root)
        history_win.title("安装历史")
        history_win.geometry("700x500")
        history_win.configure(bg='#f0f0f0')

        text = scrolledtext.ScrolledText(history_win, font=('Consolas', 10), bg='#fff', relief='flat')
        text.pack(fill='both', expand=True, padx=15, pady=15)

        if not self.history["installs"]:
            text.insert(tk.END, "暂无安装历史", 'info')
        else:
            for record in reversed(self.history["installs"]):
                text.insert(tk.END, f"[{record['time']}]\n", 'info')
                text.insert(tk.END, f"使用镜像：{record.get('mirror_used', '未知')}\n")
                text.insert(tk.END, f"包：{', '.join(record['packages'])}\n")
                result_str = f"结果：✅ {record['success']} 成功"
                if record['fail'] > 0:
                    result_str += f", ❌ {record['fail']} 失败"
                text.insert(tk.END, result_str + "\n")

                # 显示验证结果
                if "verification" in record:
                    text.insert(tk.END, "验证结果：\n")
                    for pkg, status in record["verification"].items():
                        if status.startswith("✅"):
                            text.insert(tk.END, f"  {status}\n", 'success')
                        else:
                            text.insert(tk.END, f"  {status}\n", 'error')

                text.insert(tk.END, "-" * 50 + "\n\n")

        text.config(state='disabled')

    def start_install(self):
        """开始安装（在新线程中运行）"""
        packages_input = self.package_entry.get().strip()
        if not packages_input:
            messagebox.showwarning("提示", "请输入要安装的包名")
            return

        packages = packages_input.split()

        target_python = self.get_python_executable()
        self.log(f"🐍 使用 Python 解释器: {target_python}", 'info')
        self.install_btn.config(state='disabled', text='⏳ 正在安装...')
        self.progress_bar.start(10)
        self.status_label.config(text="正在连接镜像源并安装...")
        self.clear_output()
        self.log(f"🚀 开始安装任务", 'info')
        self.log(f"📦 目标包：{', '.join(packages)}", 'info')
        self.log(f"🌐 将依次尝试 {len(MIRRORS)} 个镜像源", 'info')
        self.log(
            f"⚙️ 选项：Upgrade={self.upgrade_var.get()}, User={self.user_var.get()}, Verify={self.verify_var.get()}",
            'info')
        self.log("-" * 30)
        thread = threading.Thread(target=self.install_packages, args=(packages, target_python),
                                  daemon=True)  # Pass target_python
        thread.start()

    def verify_packages(self, packages, python_executable):  # Add python_executable argument
        """验证包是否安装成功"""
        self.log("\n🔍 开始验证包...", 'info')

        results = {}
        all_success = True

        for package in packages:
            self.log(f"  验证: {package}", 'info')
            self.validator.verify_pip_list(python_executable, package)
            can_import, version_or_error, import_name = self.validator.verify_import(python_executable, package)
            test_result, test_msg = self.validator.run_simple_test(python_executable, package)

            if can_import:
                msg = f"✅ {package} 验证成功"
                if version_or_error != 'UnknownVersion':
                    msg += f" (版本: {version_or_error})"
                if import_name != package:
                    msg += f" [导入名: {import_name}]"
                self.log(f"    {msg}", 'verify_success')

                if test_result is True:
                    self.log(f"      ✓ {test_msg}", 'success')
                elif test_result is False:
                    self.log(f"      ⚠️ {test_msg}", 'warning')

                results[package] = f"✅ {version_or_error}"
            else:
                self.log(f"    ❌ {package} 验证失败: {version_or_error}", 'verify_fail')
                results[package] = f"❌ 失败"
                all_success = False
            time.sleep(0.5)

        self.log("🔍 验证完成", 'info')
        return results, all_success

    def verify_only(self):
        """只验证不安装"""
        packages_input = self.package_entry.get().strip()
        if not packages_input:
            messagebox.showwarning("提示", "请输入要验证的包名")
            return

        packages = packages_input.split()
        target_python = self.get_python_executable()
        self.log(f"🔍 使用 Python 解释器进行验证: {target_python}", 'info')

        self.clear_output()
        self.log("🔍 单独验证模式", 'info')
        self.log(f"📦 验证包：{', '.join(packages)}", 'info')
        self.log("-" * 30)

        thread = threading.Thread(target=self.verify_only_thread, args=(packages, target_python),daemon=True)
        thread.start()

    def verify_only_thread(self, packages, python_executable):
        """验证线程"""
        results, all_success = self.verify_packages(packages, python_executable)

        self.log("\n" + "=" * 50, 'info')
        if all_success:
            self.log("✅ 所有包验证通过", 'verify_success')
            self.status_label.config(text="✅ 验证通过")
        else:
            self.log("⚠️ 部分包验证失败", 'warning')
            self.status_label.config(text="⚠️ 验证失败")

    def install_packages(self, packages, python_executable):
        """安装包的具体逻辑（自动遍历镜像源）"""
        success_count = 0
        fail_count = 0
        overall_mirror_used = None
        successfully_installed = []

        def on_try(name):
            self.log(f"  🔄 尝试镜像 [{name}]...", 'mirror_try')

        def on_fail(name):
            self.log(f"     [{name}] 失败，尝试下一个...", 'warning')

        for i, package in enumerate(packages, 1):
            self.log(f"\n[{i}/{len(packages)}] 正在处理：{package}", 'info')

            success, mirror_used = install_one_package(
                python_executable, package, MIRRORS,
                user=self.user_var.get(), upgrade=self.upgrade_var.get(),
                on_mirror_try=on_try, on_mirror_fail=on_fail
            )

            if success:
                self.log(f"  ✅ 使用 [{mirror_used}] 安装成功", 'success')
                success_count += 1
                successfully_installed.append(package)
                if not overall_mirror_used:
                    overall_mirror_used = mirror_used
            else:
                self.log(f"  ❌ {package} 在所有镜像源上都安装失败", 'error')
                fail_count += 1

        # 验证环节
        verification_results = None
        if self.verify_var.get() and successfully_installed:
            self.log("\n" + "-" * 30, 'info')
            verification_results, verify_success = self.verify_packages(successfully_installed, python_executable)
            if not verify_success:
                self.log("\n⚠️ 部分包虽然安装成功但验证失败，可能需要手动检查", 'warning')
        self.save_history(packages, success_count, fail_count, overall_mirror_used, verification_results)
        self.root.after(0, self.install_finished, success_count, fail_count, overall_mirror_used, verification_results)

    def install_finished(self, success_count, fail_count, mirror_used, verification_results=None):
        """安装完成后的界面更新"""
        self.progress_bar.stop()
        self.install_btn.config(state='normal', text='🚀 开始安装')

        self.log("\n" + "=" * 50, 'info')
        msg = f"📊 任务完成：✅ {success_count} 成功"
        if fail_count > 0:
            msg += f", ❌ {fail_count} 失败"

        if mirror_used:
            msg += f" (主要使用镜像: {mirror_used})"

        self.log(msg, 'info' if fail_count == 0 else 'warning')
        if verification_results:
            self.log("\n📋 验证结果汇总:", 'info')
            all_good = True
            for pkg, status in verification_results.items():
                if status.startswith("✅"):
                    self.log(f"  {status}", 'verify_success')
                else:
                    self.log(f"  {status}", 'verify_fail')
                    all_good = False

            if all_good:
                self.log("\n✅ 所有已安装包验证通过！", 'verify_success')
            else:
                self.log("\n⚠️ 部分包验证失败，可能需要手动检查", 'warning')

        if fail_count == 0:
            self.status_label.config(text=f"✅ 全部安装成功 (镜像: {mirror_used})")
            if self.verify_var.get() and verification_results:
                all_verified = all(v.startswith("✅") for v in verification_results.values())
                if all_verified:
                    messagebox.showinfo("完成", f"所有包安装并验证成功！\n使用镜像: {mirror_used}")
                else:
                    messagebox.showwarning("完成", f"安装成功但部分包验证失败，请查看日志。\n使用镜像: {mirror_used}")
        else:
            self.status_label.config(text=f"⚠️ 部分失败 ({fail_count})")
            messagebox.showwarning("完成", f"安装结束。\n成功：{success_count}\n失败：{fail_count}\n请查看日志了解详情。")


def main():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    root = tk.Tk()
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family="Microsoft YaHei UI", size=9)
    app = PipInstallerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()