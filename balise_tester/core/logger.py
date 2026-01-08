import datetime
import os

from .packet_utils import PACKET_TYPE_MAP


class SimulationLogger:
    """
    仿真日志记录器类。
    
    用于记录系统运行过程中的各种事件，如列车运行、经过应答器等信息。
    日志按日期自动分文件存储。
    """

    def __init__(self, log_dir=None):
        """
        初始化日志记录器。
        
        Args:
            log_dir (str, optional): 日志文件存储目录。如果不提供，
                                     默认使用项目根目录下的 data/logs。
        """
        if log_dir is None:
            # .../balise_tester/core/logger.py -> .../
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            self.log_dir = os.path.join(project_root, "data", "logs")
        else:
            self.log_dir = log_dir

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.current_log_file = self.get_log_file_path()

    def get_log_file_path(self):
        """
        根据当前日期获取日志文件路径。
        格式如: log_20230101.txt
        
        Returns:
            str: 完整的日志文件路径。
        """
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        log_file_name = f"log_{date_str}.txt"
        return os.path.join(self.log_dir, log_file_name)

    def log(self, message):
        """
        写入一条通用日志信息。
        如果日期发生变化，会自动切换到新的日志文件。
        
        Args:
            message (str): 日志内容。
        """
        new_log_file = self.get_log_file_path()
        if new_log_file != self.current_log_file:
            self.current_log_file = new_log_file

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        log_entry = f"[{timestamp}] {message}\n"

        try:
            with open(self.current_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Logging error: {e}")

    def log_balise_event(self, train_name, balise_data):
        """
        记录列车经过应答器的详细事件。
        
        Args:
            train_name (str): 列车名称。
            balise_data (dict): 应答器数据字典。
        """
        b_name = balise_data.get("name", "Unknown")
        b_id = f"{balise_data.get('nid_c', '0')}-{balise_data.get('nid_bg', '0')}"
        sub_id = balise_data.get("sub_id", "0")

        # Construct packet info string
        packets = []

        for p in PACKET_TYPE_MAP.keys():
            if balise_data.get(p):
                packets.append(p)

        packet_str = ", ".join(packets)

        msg = (f"Train '{train_name}' passed Balise '{b_name}' "
               f"(Region:{b_id}, GroupPos:{sub_id}). "
               f"Packets: [{packet_str}]")

        self.log(msg)
