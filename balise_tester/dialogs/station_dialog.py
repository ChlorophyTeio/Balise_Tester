from PySide6.QtWidgets import QDialog, QMessageBox
from ui.station_config import Ui_train_config_form as Ui_StationConfigForm

class StationConfigDialog(QDialog, Ui_StationConfigForm):
    """
    车站配置对话框类。
    
    用于创建或编辑车站的配置信息，如名称和位置。
    """
    def __init__(self, parent=None, config_data=None, max_length=None):
        """
        初始化车站配置对话框。
        
        Args:
            parent (QWidget, optional): 父窗口部件。
            config_data (dict, optional): 初始配置数据。如果是编辑模式则提供，创建模式可为None。
            max_length (float, optional): 线路最大长度限制，用于输入校验。
        """
        super().__init__(parent)
        self.setupUi(self)
        self.config_data = config_data or {}
        self.max_length = max_length
        self.load_data()
        self.pushButton_save.clicked.connect(self.save_data)
        self.pushButton_cancel.clicked.connect(self.close)

    def load_data(self):
        """
        从配置数据加载到界面控件。
        """
        self.lineEdit_name.setText(str(self.config_data.get("name", "")))
        self.lineEdit_location.setText(str(self.config_data.get("location", "")))

    def save_data(self):
        """
        保存界面数据到配置字典。
        会进行位置数据的类型转换和范围校验。
        """
        try:
            location = float(self.lineEdit_location.text())
            if self.max_length is not None and location > self.max_length:
                QMessageBox.warning(self, "警告", f"位置不能超过线路总长度 ({self.max_length} km)")
                return
            self.config_data["location"] = location
        except ValueError:
            self.config_data["location"] = 0.0
            
        self.config_data["name"] = self.lineEdit_name.text()
        self.accept()
