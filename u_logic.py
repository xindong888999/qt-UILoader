from PyQt6.QtWidgets import QPushButton, QLineEdit

class ULogic:
    pushButton: QPushButton  # 必须与UI中的objectName一致
    lineEdit: QLineEdit

    def setup_connections(self):
        """显式信号连接"""
        self.pushButton.clicked.connect(self.on_button_clicked)
        print("显式连接成功")

    def on_button_clicked(self):
        """按钮点击事件处理"""
        text = self.lineEdit.text() or "World"
        print(f"[显式] Hello {text}!")

    def pushButton_clicked(self):
        """自动连接事件（命名规范：组件名_信号名）"""
        print("[自动] 按钮点击事件通过命名规范连接成功")