import os
import sys
import importlib
from pathlib import Path
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QWidget


class UILoader:
    def __init__(self, ui_path):
        self.ui_path = os.path.abspath(ui_path)
        self.original_sys_path = sys.path.copy()
        self.ui = None
        self.logic_instance = None

    def load(self):
        """加载UI文件并返回界面和逻辑实例"""
        try:
            # 添加UI文件所在目录到系统路径
            ui_dir = os.path.dirname(self.ui_path)
            if ui_dir not in sys.path:
                sys.path.insert(0, ui_dir)

            # 加载UI界面
            self.ui = loadUi(self.ui_path)

            # 加载对应的逻辑类
            logic_class = self._get_logic_class()

            # 实例化逻辑类
            self.logic_instance = logic_class()

            # 自动绑定组件
            self._auto_bind_components()

            # 自动连接信号
            self._auto_connect_signals()

            return self.ui, self.logic_instance
        finally:
            # 恢复原始系统路径
            sys.path = self.original_sys_path

    def _get_logic_class(self):
        """动态导入对应的逻辑类（支持多级目录）"""
        base_name = Path(self.ui_path).stem  # 获取无扩展的文件名
        module_name = f"{base_name}_logic"
        class_name = f"{base_name[0].upper()}{base_name[1:]}Logic"

        try:
            module = importlib.import_module(module_name)
            return getattr(module, class_name)
        except ModuleNotFoundError as e:
            # 尝试相对路径导入
            try:
                rel_path = Path(self.ui_path).relative_to(Path.cwd())
                module_path = ".".join(rel_path.parent.parts + (module_name,))
                module = importlib.import_module(module_path)
                return getattr(module, class_name)
            except Exception:
                raise ImportError(
                    f"无法加载逻辑类 {class_name}，请确认以下文件存在：\n"
                    f"1. 文件位置：{Path(self.ui_path).parent}/{module_name}.py\n"
                    f"2. 类定义：class {class_name} 存在于文件中\n"
                    f"3. 当前工作目录：{os.getcwd()}"
                )
        except AttributeError:
            raise AttributeError(f"模块 {module_name} 中缺少类 {class_name}")

    def _auto_bind_components(self):
        """增强型组件绑定"""
        annotations = getattr(self.logic_instance.__class__, '__annotations__', {})

        success = []
        failure = []
        for var_name, var_type in annotations.items():
            component = getattr(self.ui, var_name, None)
            if component and isinstance(component, QWidget):
                setattr(self.logic_instance, var_name, component)
                success.append(var_name)
            else:
                failure.append(var_name)

        print(f"组件绑定结果：{len(success)}成功, {len(failure)}失败")
        if failure:
            print(f"未找到的组件：{', '.join(failure)}")

    def _auto_connect_signals(self):
        """智能信号连接"""
        # 优先连接setup_connections方法
        if hasattr(self.logic_instance, 'setup_connections'):
            self.logic_instance.setup_connections()
            print("已连接显式信号")

        # 自动连接on_组件名_信号名方法
        connected = []
        for name in dir(self.ui):
            widget = getattr(self.ui, name)
            if isinstance(widget, QWidget):
                signals = [attr for attr in dir(widget) if attr.startswith('on_')]
                for signal_name in signals:
                    slot_name = f"{name}_{signal_name[3:]}"
                    if hasattr(self.logic_instance, slot_name):
                        getattr(widget, signal_name).connect(
                            getattr(self.logic_instance, slot_name)
                        )
                        connected.append(f"{name}.{signal_name} → {slot_name}")

        print(f"自动连接信号：{len(connected)}个")
        if connected:
            print("\n".join(connected))


# 使用示例（uu.py）
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    # 确保工作目录正确（如果从父目录运行）
    os.chdir(os.path.dirname(__file__))

    app = QApplication([])

    # 使用相对路径示例
    loader = UILoader("u.ui")  # UI文件在子目录test1中
    window, logic = loader.load()
    window.show()

    app.exec()