from PySide6.QtWidgets import QDialog

from ui.train_config import Ui_train_config_form as Ui_TrainConfigForm


class TrainConfigDialog(QDialog, Ui_TrainConfigForm):
    """
    列车配置对话框类。
    
    用于创建或编辑列车的配置信息，包括名称、运行图设置、起止车站、初始速度等。
    """

    def __init__(self, parent=None, config_data=None, stations=None):
        """
        初始化列车配置对话框。
        
        Args:
            parent (QWidget, optional): 父窗口部件。
            config_data (dict, optional): 初始配置数据。
            stations (list, optional): 可选的车站列表，用于填充起止车站下拉框。
        """
        super().__init__(parent)
        self.setupUi(self)
        self.config_data = config_data or {}
        self.stations = stations or []
        self.load_data()
        self.pushButton_save.clicked.connect(self.save_data)
        self.pushButton_cancel.clicked.connect(self.close)

    def load_data(self):
        """
        从配置数据加载到界面控件。
        并根据提供的车站列表填充起止车站下拉框。
        """
        self.lineEdit_name.setText(str(self.config_data.get("name", "")))
        self.comboBox_setmap.setCurrentIndex(int(self.config_data.get("run_map", 0)))
        self.comboBox_setdelay.setCurrentIndex(int(self.config_data.get("start_mode", 0)))
        self.lineEdit_speed.setText(str(self.config_data.get("initial_speed", "0")))
        self.comboBox_opt.setCurrentIndex(int(self.config_data.get("end_action", 0)))

        # Populate start and end station comboboxes
        self.comboBox_set_start.clear()
        self.comboBox_set_end.clear()

        for station in self.stations:
            name = station.get("name", "Unknown Station")
            self.comboBox_set_start.addItem(name)
            self.comboBox_set_end.addItem(name)

        self.comboBox_set_start.addItem("根据运行图运行")
        self.comboBox_set_end.addItem("根据运行图运行")

        # Set current index for start station
        saved_start = self.config_data.get("start_station", "根据运行图运行")
        index_start = self.comboBox_set_start.findText(str(saved_start))
        if index_start >= 0:
            self.comboBox_set_start.setCurrentIndex(index_start)
        else:
            self.comboBox_set_start.setCurrentIndex(self.comboBox_set_start.count() - 1)

        # Set current index for end station
        saved_end = self.config_data.get("end_station", "根据运行图运行")
        index_end = self.comboBox_set_end.findText(str(saved_end))
        if index_end >= 0:
            self.comboBox_set_end.setCurrentIndex(index_end)
        else:
            self.comboBox_set_end.setCurrentIndex(self.comboBox_set_end.count() - 1)

    def save_data(self):
        """
        保存界面数据到配置字典。
        """
        self.config_data["name"] = self.lineEdit_name.text()
        self.config_data["run_map"] = self.comboBox_setmap.currentIndex()
        self.config_data["start_mode"] = self.comboBox_setdelay.currentIndex()
        self.config_data["start_station"] = self.comboBox_set_start.currentText()
        self.config_data["end_station"] = self.comboBox_set_end.currentText()
        self.config_data["end_action"] = self.comboBox_opt.currentIndex()

        try:
            speed = float(self.lineEdit_speed.text())
            self.config_data["initial_speed"] = speed
        except ValueError:
            self.config_data["initial_speed"] = 0.0

        self.accept()
