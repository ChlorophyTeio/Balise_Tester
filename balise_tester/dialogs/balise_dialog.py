import json

from PySide6.QtWidgets import QDialog, QMessageBox

from ui.balise_config import Ui_balise_config_form
from ..core.packet_utils import (
    encode_packet,
    decode_packet,
    translate_to_cn,
    translate_to_var,
    PACKET_DEFS,
    PACKET_TYPE_MAP,
)


class BaliseConfigDialog(QDialog, Ui_balise_config_form):
    def __init__(self, parent=None, config_data=None, max_length=None):
        """
        初始化应答器配置对话框。

        参数:
            parent: 父级控件。
            config_data (dict): 现有的应答器配置数据。
            max_length (float): 用于验证的最大线路长度限制。
        """
        super().__init__(parent)
        self.setupUi(self)
        self.config_data = config_data or {}
        self.max_length = max_length
        self.load_data()
        self.pushButton_save.clicked.connect(self.save_data)
        self.pushButton_cancel.clicked.connect(self.close)

        # Initialize Combo Box for Packet Selection
        self.comboBox_balise_add_config.addItem("选择添加信息包...")
        for pkt_name in PACKET_DEFS.keys():
            desc = PACKET_TYPE_MAP.get(pkt_name, pkt_name)
            self.comboBox_balise_add_config.addItem(f"{pkt_name} - {desc}", pkt_name)

        # Connect signal
        self.comboBox_balise_add_config.currentIndexChanged.connect(self.add_packet_template)

    def add_packet_template(self, index):
        """
        根据用户选择，向配置文本框中添加对应信息包的JSON模板。
        """
        if index <= 0:
            return

        pkt_name = self.comboBox_balise_add_config.currentData()
        if not pkt_name or pkt_name not in PACKET_DEFS:
            return

        # Reset selection
        self.comboBox_balise_add_config.setCurrentIndex(0)

        # Determine existing data
        try:
            current_text = self.textEdit_config.toPlainText()
            current_data = json.loads(current_text) if current_text.strip() else {}
        except json.JSONDecodeError:
            QMessageBox.warning(self, "警告", "当前配置内容格式错误，无法追加新包。请先修正JSON格式。")
            return

        if pkt_name in current_data:
            QMessageBox.information(self, "提示", f"信息包 {pkt_name} 已存在。")
            return

        # Generate Template
        defs = PACKET_DEFS[pkt_name]
        template = {}

        # Create a temporary dict with variable names first
        var_data = {}
        for field in defs:
            # Use default value if defined, else 0/empty
            val = field.get("val", 0)
            # Special case for optional
            if field.get("optional", False):
                continue
            if "cond" in field:
                # If conditional, we might skip or include default.
                # Including default is safer for template to show user what's available.
                pass

            var_data[field["name"]] = val

        # Translate to Chinese
        cn_data = translate_to_cn(var_data, pkt_name)

        # Add to current data
        current_data[pkt_name] = cn_data

        # Update Text Edit
        self.textEdit_config.setText(json.dumps(current_data, indent=4, ensure_ascii=False))

    def load_data(self):
        """
        从配置字典加载数据到 UI 控件中。
        处理变量名到中文的翻译以及二进制报文的解码。
        """
        self.lineEdit_name.setText(str(self.config_data.get("name", "")))
        self.lineEdit_location.setText(str(self.config_data.get("location", "")))
        self.comboBox_balise_type.setCurrentIndex(int(self.config_data.get("type", 0)))
        self.lineEdit_father_balise.setText(
            str(self.config_data.get("father_balise", ""))
        )
        self.lineEdit_subid.setText(str(self.config_data.get("sub_id", "")))

        # Load other data into textEdit_config as JSON
        # Exclude known fields
        exclude_keys = {"name", "location", "type", "father_balise", "sub_id"}

        # Start constructing the display JSON (Chinese keys, decoded packets)
        display_data = {}

        # Prepare header data from config or defaults
        defaults = {
            "q_updown": "1",
            "m_version": "0010000",
            "q_media": "0",
            "n_total": "1",
            "m_dup": "00",
            "nid_c": "0",
            "nid_bg": "0",
            "q_link": "0",
        }

        # Populate display_data with ALL config_data (excluding known) but translated
        # First pass: gather raw data
        raw_data = {k: v for k, v in self.config_data.items() if k not in exclude_keys}

        # Add defaults if missing
        for k, v in defaults.items():
            if k not in raw_data or not str(raw_data[k]).strip():
                raw_data[k] = v

        # N_PIG Logic overwrite
        sub_id_val = self.config_data.get("sub_id", "0")
        try:
            raw_data["n_pig"] = bin(int(sub_id_val))[2:].zfill(3)[-3:]
        except ValueError:
            pass

        # Process translation
        for k, v in raw_data.items():
            # If it looks like a packet (ETCS/CTCS)
            if k.startswith("ETCS-") or k.startswith("CTCS-"):
                # Try to decode binary if it looks like binary
                if isinstance(v, str) and len(v) > 8 and all(c in "01" for c in v):
                    decoded = decode_packet(k, v)
                    # Translate inner keys to Chinese
                    decoded_cn = translate_to_cn(decoded, k)
                    display_data[k] = (
                        decoded_cn  # We keep packet name as key, content as Chinese dict
                    )
                else:
                    # If not binary (maybe already legacy format?), just pass it
                    # But we should still try to translate if it's already a dict?
                    if isinstance(v, dict):
                        display_data[k] = translate_to_cn(v, k)
                    else:
                        display_data[k] = v
            else:
                # Header fields: Translate Key to Chinese
                cn_key = translate_to_cn({k: v}).popitem()[0]
                display_data[cn_key] = v

        self.textEdit_config.setText(
            json.dumps(display_data, indent=4, ensure_ascii=False)
        )

    def save_data(self):
        """
        验证并将数据从 UI 控件保存回配置字典。
        处理中文键名回译为变量名以及二进制报文的编码。
        """
        # Create a new dict to ensure removed keys from JSON are actually removed
        new_data = {}

        try:
            location = float(self.lineEdit_location.text())
            if self.max_length is not None and location > self.max_length:
                QMessageBox.warning(
                    self, "警告", f"位置不能超过线路总长度 ({self.max_length} km)"
                )
                return
            new_data["location"] = location
        except ValueError:
            new_data["location"] = 0.0

        new_data["name"] = self.lineEdit_name.text()
        new_data["type"] = self.comboBox_balise_type.currentIndex()
        new_data["father_balise"] = self.lineEdit_father_balise.text()
        new_data["sub_id"] = self.lineEdit_subid.text()

        # Parse JSON from textEdit_config
        try:
            json_text = self.textEdit_config.toPlainText()
            if json_text.strip():
                extra_data = json.loads(json_text)
                if isinstance(extra_data, dict):
                    # We need to translate BACK to System Format (Variable Keys, Binary Packets)
                    converted_extra = {}

                    # 1. Separate Header fields from Packets
                    # Packets usually have keys "ETCS-xxx" or "CTCS-xxx"
                    # Header fields are now in Chinese, e.g. "信息传输方向"

                    for k, v in extra_data.items():
                        # Check if key is a known Packet Name
                        if k.startswith("ETCS-") or k.startswith("CTCS-"):
                            # This is a packet. v should be a dict of Chinese keys
                            if isinstance(v, dict):
                                var_dict = translate_to_var(v, k)
                                # Encode to binary
                                bin_str = encode_packet(k, var_dict)
                                converted_extra[k] = bin_str
                            else:
                                # Maybe raw string?
                                converted_extra[k] = v
                        else:
                            # Must be a Header field (Chinese Key) -> Translate to Var
                            var_key = translate_to_var({k: v}).popitem()[0]
                            converted_extra[var_key] = v

                    # Merge into new_data
                    # Ensure we don't overwrite fixed fields with JSON data if user manually added them
                    # Fixed fields are handled by UI widgets, so we ignore them from JSON if exist
                    exclude_keys = {
                        "name",
                        "location",
                        "type",
                        "father_balise",
                        "sub_id",
                    }
                    filtered_extra = {
                        k: v
                        for k, v in converted_extra.items()
                        if k not in exclude_keys
                    }
                    new_data.update(filtered_extra)

                else:
                    QMessageBox.warning(self, "警告", "配置内容必须是JSON对象")
                    return
        except json.JSONDecodeError as e:
            error_msg = f"JSON格式错误:\n{e.msg}\nLine: {e.lineno}, Column: {e.colno}"
            QMessageBox.warning(self, "警告", error_msg)
            return

        # Auto-Correction / Optimization of Protocol Fields based on UI Inputs

        # 1. Update N_PIG based on Sub ID
        try:
            sid = int(new_data["sub_id"])
            new_data["n_pig"] = bin(sid)[2:].zfill(3)[-3:]
        except ValueError:
            pass

        # 2. Update M_MCOUNT based on Type if not manually set to something else reasonable
        current_mcount = str(new_data.get("m_mcount", ""))
        current_type = new_data["type"]  # 0=Passive/无源, 1=Active/有源

        # Requirement: Passive=255, Active=252
        if current_type == 0:
            new_data["m_mcount"] = "255"
        elif current_type == 1:
            new_data["m_mcount"] = "252"

        # 3. Update ETCS-79 to match Location if present
        # ETCS-79 is a binary packet now. So simple update is harder unless we decode-update-encode.
        # But for now, if ETCS-79 is missing, we might want to auto-generate it.
        # If present, we trust user edits (via JSON).
        # We skip auto-updating binary ETCS-79 for now to avoid complexity unless requested.

        self.config_data = new_data
        self.accept()
