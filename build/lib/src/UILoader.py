import os
os.environ["QT_LOGGING_RULES"] = "qt.png.warning=false"
import sys
import importlib
import inspect
from pathlib import Path
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSignal, QObject, QMetaMethod
from PyQt6.QtWidgets import QWidget, QApplication


class UILoader:
    def __init__(self, ui_path):
        self.ui_path = Path(ui_path).absolute()
        self.original_sys_path = sys.path.copy()
        self.ui = None
        self.logic_instance = None

    def load(self):
        """加载并初始化UI界面和逻辑类"""
        try:
            # 添加UI目录到Python路径
            ui_dir = str(self.ui_path.parent)
            if ui_dir not in sys.path:
                sys.path.insert(0, ui_dir)

            # 加载UI文件
            self.ui = loadUi(str(self.ui_path))

            # 加载逻辑类
            logic_class = self._load_logic_class()
            self.logic_instance = logic_class()

            # 执行绑定和连接
            self._bind_components()
            self._connect_signals()

            return self.ui, self.logic_instance
        finally:
            # 恢复原始路径
            sys.path = self.original_sys_path

    def _load_logic_class(self):
        """动态加载逻辑类"""
        base_name = self.ui_path.stem
        module_name = f"{base_name}_logic"
        class_name = f"{base_name[0].upper()}{base_name[1:]}Logic"

        try:
            # 尝试直接导入
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            # 尝试相对导入
            try:
                rel_path = self.ui_path.relative_to(Path.cwd())
                parts = rel_path.parent.parts + (module_name,)
                module_path = ".".join(parts)
                module = importlib.import_module(module_path)
            except Exception as e:
                raise ImportError(
                    f"逻辑类加载失败：\n"
                    f"• 预期模块路径：{self.ui_path.parent}/{module_name}.py\n"
                    f"• 预期类名：{class_name}\n"
                    f"• 当前工作目录：{Path.cwd()}\n"
                    f"错误详情：{str(e)}"
                )

        if not hasattr(module, class_name):
            raise AttributeError(f"模块 {module.__name__} 中缺少类 {class_name}")
        return getattr(module, class_name)

    def _bind_components(self):
        """绑定UI组件到逻辑类"""
        annotations = getattr(self.logic_instance.__class__, '__annotations__', {})
        bind_results = {'success': [], 'fail': []}

        for name, expected_type in annotations.items():
            component = getattr(self.ui, name, None)
            if component and isinstance(component, expected_type):
                setattr(self.logic_instance, name, component)
                bind_results['success'].append(name)
            else:
                bind_results['fail'].append(name)

        print("\n组件绑定结果：")
        print(f"✅ 成功绑定 ({len(bind_results['success'])}): {', '.join(bind_results['success'])}")
        if bind_results['fail']:
            print(f"❌ 绑定失败 ({len(bind_results['fail'])}): {', '.join(bind_results['fail'])}")
            print("可能原因：")
            print("- objectName 不匹配")
            print("- 类型注解错误")
            print("- 组件未在UI文件中定义")

    def _connect_signals(self):
        """智能信号连接系统"""
        from PyQt6.QtCore import QMetaMethod

        # 显式连接
        explicit_conn = self._connect_explicit_signals()

        # 自动连接
        auto_conn = self._connect_auto_signals()

        # 显示连接结果
        print("\n信号连接汇总：")
        print(f"显式连接：{explicit_conn}个")
        print(f"自动连接：{auto_conn}个")

    def _connect_explicit_signals(self):
        """处理显式连接（setup_connections）"""
        if hasattr(self.logic_instance, 'setup_connections'):
            try:
                self.logic_instance.setup_connections()
                return 1
            except Exception as e:
                print(f"显式连接异常：{str(e)}")
                return 0
        return 0

    def _connect_auto_signals(self):
        """自动连接标准信号"""
        connection_count = 0

        for widget_name in dir(self.ui):
            widget = getattr(self.ui, widget_name)
            if not isinstance(widget, QWidget):
                continue

            # 获取所有可用信号
            signals = self._get_widget_signals(widget)

            for signal_name in signals:
                slot_name = f"on_{widget_name}_{signal_name}"
                if hasattr(self.logic_instance, slot_name):
                    try:
                        signal = getattr(widget, signal_name)
                        slot = getattr(self.logic_instance, slot_name)
                        signal.connect(slot)
                        connection_count += 1
                        print(f"🔌 自动连接: {widget_name}.{signal_name} → {slot_name}")
                    except Exception as e:
                        print(f"连接失败 {widget_name}.{signal_name}: {str(e)}")

        return connection_count

    def _get_widget_signals(self, widget):
        """获取组件的所有信号"""
        signals = []
        mo = widget.metaObject()
        for i in range(mo.methodCount()):
            method = mo.method(i)
            if method.methodType() == QMetaMethod.MethodType.Signal:
                name = method.methodSignature().data().decode().split('(')[0]
                signals.append(name)
        return list(set(signals))  # 去重


# ================= 使用示例 =================
if __name__ == "__main__":

    app = QApplication([])
    app.setStyle("Fusion")  # 使用无图标主题
    loader = UILoader("u.ui")
    window, logic = loader.load()
    window.show()

    app.exec()