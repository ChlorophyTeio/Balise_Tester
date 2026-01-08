from PySide6.QtWidgets import QDialog, QMessageBox
from ui.line_config import Ui_train_config_form as Ui_LineConfigForm

class LineConfigDialog(QDialog, Ui_LineConfigForm):
    """
    线路全局配置对话框类。
    
    用于设置线路的总长度等全局参数。
    """
    def __init__(self, parent=None, config_data=None):
        """
        初始化线路配置对话框。
        
        Args:
            parent (QWidget, optional): 父窗口部件。
            config_data (dict, optional): 初始配置数据。
        """
        super().__init__(parent)
        self.setupUi(self)
        self.config_data = config_data or {}
        self.load_data()
        self.pushButton_save.clicked.connect(self.save_data)
        self.pushButton_cancel.clicked.connect(self.close)

    def load_data(self):
        """
        从配置数据加载到界面控件。
        """
        self.lineEdit_line_total_length.setText(str(self.config_data.get("total_length", "100.0")))
        self.lineEdit_line_total_speed.setText(str(self.config_data.get("max_speed", "350.0")))

    def save_data(self):
        """
        保存界面数据到配置字典。
        校验输入是否为正数。
        """
        try:
            length = float(self.lineEdit_line_total_length.text())
            speed = float(self.lineEdit_line_total_speed.text())
            
            if length <= 0 or speed <= 0:
                QMessageBox.warning(self, "警告", "线路长度和最大速度必须大于0")
                return
                
            self.config_data["total_length"] = length
            self.config_data["max_speed"] = speed
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的数字")
