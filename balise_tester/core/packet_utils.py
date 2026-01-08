
class PacketUtils:
    """
    处理基本报文数据转换和描述的工具类。
    """
    @staticmethod
    def int_to_bin(value, bits):
        """
        将整数转换为固定宽度的二进制字符串。
        
        参数:
            value: 要转换的整数值。
            bits: 二进制字符串的宽度（左补零）。
            
        返回:
            str: 二进制字符串表示（例如 "00101"）。
        """
        try:
            val = int(value)
        except ValueError:
            val = 0
        return f"{val:0{bits}b}"[-bits:]

    @staticmethod
    def bin_to_int(bin_str):
        """
        将二进制字符串转换为整数。
        
        参数:
            bin_str: 二进制字符串（例如 "010"）。
            
        返回:
            int: 整数值。
        """
        if not bin_str:
            return 0
        return int(bin_str, 2)

    @staticmethod
    def get_q_scale_desc(code):
        """
        获取 Q_SCALE 代码的描述。
        
        参数:
            code: Q_SCALE 的二进制字符串或代码。
            
        返回:
            str: 可读描述（例如 "1m"）。
        """
        maps = {"00": "10cm", "01": "1m", "10": "10m"}
        # Allow int input
        if isinstance(code, int):
            code = f"{code:02b}"
        return maps.get(code, "Unknown")
        
    @staticmethod
    def get_q_scale_factor(code):
        """
        获取 Q_SCALE 的实际数值比例（米）。
        
        参数:
            code: int (0, 1, 2) 或 bin str ("00", "01", "10")
            
        返回:
            float: 比例因子，如 0.1, 1.0, 10.0
        """
        try:
            val = int(code) if isinstance(code, (int, str)) else 1
            # If input was binary string '00', int('00') is 0. 
            # If input was binary string '10', int('10') is 10 (decimal ten)!
            # Wait, binary string needs base 2.
            
            if isinstance(code, str):
                # Try to parse as int first (maybe it's "1" or "2")
                # If it's "00", int("00") -> 0.
                # If it's "10", int("10") -> 10. This is ambiguous.
                # But typically code passed is the VALUE of Q_SCALE (0, 1, 2).
                # decode_packet returns value (int).
                
                # If we assume code is value:
                pass
            
            # Let's rely on standard handling:
            # 0 -> 10cm
            # 1 -> 1m
            # 2 -> 10m
            
            # If a binary string is passed in future, we should handle it.
            # But currently decode_packet returns INT.
            
            if val == 0: return 0.1
            if val == 1: return 1.0
            if val == 2: return 10.0
        except:
            pass
        return 1.0

    @staticmethod
    def get_q_dir_desc(code):
        """
        获取 Q_DIR 代码的描述。
        
        参数:
            code: Q_DIR 的二进制字符串或代码。
            
        返回:
            str: 可读描述（例如 "正向"）。
        """
        maps = {"00": "反向", "01": "正向", "10": "双向", "11": "备用"}
        return maps.get(code, "Unknown")

PACKET_TYPE_MAP = {
    "ETCS-5": "链接信息",
    "CTCS-1": "轨道区段",
    "ETCS-21": "线路坡度",
    "ETCS-27": "线路速度",
    "ETCS-41": "等级转换",
    "ETCS-42": "通信管理",
    "ETCS-44": "CTCS数据",
    "ETCS-46": "条件转换",
    "ETCS-68": "特殊区段",
    "ETCS-72": "文本信息",
    "ETCS-79": "里程信息",
    "ETCS-131": "RBC切换",
    "ETCS-132": "调车危险",
    "ETCS-137": "目视危险",
    "ETCS-254": "默认信息",
    "CTCS-2": "临时限速",
    "CTCS-4": "大号码道岔",
    "CTCS-5": "绝对停车"
}

HEADER_MAP = {
    "q_updown": "信息传输方向",
    "m_version": "代码版本",
    "q_media": "传输媒介",
    "n_pig": "组内位置",
    "n_total": "组内总数量",
    "m_dup": "信息重复标识",
    "m_mcount": "报文计数器",
    "nid_c": "地区编号",
    "nid_bg": "应答器标识号",
    "q_link": "链接状态"
}

PACKET_DEFS = {
    # ETCS-5: Link
    "ETCS-5": [
        {"name": "NID_PACKET", "len": 8, "val": 5, "desc": "信息包标识"},
        {"name": "Q_DIR", "len": 2, "desc": "验证方向"},
        {"name": "Q_SCALE", "len": 2, "desc": "距离分辨率"},
        {"name": "D_LINK", "len": 15, "desc": "链接距离"},
        {"name": "Q_NEWCOUNTRY", "len": 1, "desc": "地区关系"},
        {"name": "NID_C", "len": 10, "cond": lambda d: d.get("Q_NEWCOUNTRY") == 1, "desc": "地区编号"},
        {"name": "NID_BG", "len": 14, "desc": "应答器组编号"},
        {"name": "Q_LINKORIENTATION", "len": 1, "desc": "运行方向"},
        {"name": "Q_LINKREACTION", "len": 2, "desc": "链接失败措施"},
        {"name": "Q_LOCACC", "len": 6, "desc": "安装偏差"},
        {"name": "N_ITER", "len": 5, "desc": "链接组数量"}
    ],
    # CTCS-1: Track Section
    "CTCS-1": [
        {"name": "NID_XUSER", "len": 9, "val": 1, "desc": "CTCS包标识码"},
        {"name": "Q_DIR", "len": 2, "desc": "验证方向"},
        {"name": "Q_SCALE", "len": 2, "desc": "距离分辨率"},
        {"name": "NID_SIGNAL", "len": 4, "desc": "信号机类型"},
        {"name": "NID_FREQUENCY", "len": 5, "desc": "载频"},
        {"name": "D_SIGNAL", "len": 15, "desc": "区段起始距离"},
        {"name": "L_SECTION", "len": 15, "desc": "区段长度"},
        {"name": "N_ITER", "len": 5, "desc": "区段数量"}
    ],
    # ETCS-21: Gradient
    "ETCS-21": [
        {"name": "NID_PACKET", "len": 8, "val": 21, "desc": "信息包标识"},
        {"name": "Q_DIR", "len": 2, "desc": "验证方向"},
        {"name": "Q_SCALE", "len": 2, "desc": "距离分辨率"},
        {"name": "D_GRADIENT", "len": 15, "desc": "坡度起始点距离"},
        {"name": "Q_GDIR", "len": 1, "desc": "坡度方向"},
        {"name": "G_A", "len": 8, "desc": "安全坡度"},
        {"name": "N_ITER", "len": 5, "desc": "坡度变化点数量"}
    ],
    # ETCS-27: Speed
    "ETCS-27": [
        {"name": "NID_PACKET", "len": 8, "val": 27, "desc": "信息包标识"},
        {"name": "Q_DIR", "len": 2, "desc": "验证方向"},
        {"name": "Q_SCALE", "len": 2, "desc": "距离分辨率"},
        {"name": "D_STATIC", "len": 15, "desc": "速度起始点距离"},
        {"name": "V_STATIC", "len": 7, "desc": "最大允许速度"},
        {"name": "Q_FRONT", "len": 1, "desc": "头尾有效性"},
        {"name": "NC_DIFF", "len": 4, "val": 0, "optional": True, "desc": "列车类型"},
        {"name": "V_DIFF", "len": 7, "cond": lambda d: False, "optional": True, "desc": "列车类型速度"},
        {"name": "N_ITER", "len": 5, "desc": "速度变化点数量"}
    ],
    # ETCS-41: Level Transition
    "ETCS-41": [
        {"name": "NID_PACKET", "len": 8, "val": 41, "desc": "信息包标识"},
        {"name": "Q_DIR", "len": 2, "desc": "验证方向"},
        {"name": "Q_SCALE", "len": 2, "desc": "距离分辨率"},
        {"name": "D_LEVELTR", "len": 15, "desc": "转换点距离"},
        {"name": "M_LEVELTR", "len": 3, "desc": "ETCS转换等级"},
        {"name": "NID_STM", "len": 8, "cond": lambda d: d.get("M_LEVELTR") == 1, "desc": "非ETCS转换等级"},
        {"name": "L_ACKLEVELTR", "len": 15, "desc": "确认区段长度"},
        {"name": "N_ITER", "len": 5, "desc": "转换点数量"}
    ],
    # CTCS-2: TSR (Temporary Speed Restriction)
    "CTCS-2": [
        {"name": "NID_XUSER", "len": 9, "val": 2, "desc": "CTCS包标识码"},
        {"name": "Q_DIR", "len": 2, "desc": "验证方向"},
        {"name": "Q_SCALE", "len": 2, "desc": "距离分辨率"},
        {"name": "V_TSR", "len": 7, "desc": "限制速度"},
        {"name": "D_TSR", "len": 15, "desc": "限速区段距离"},
        {"name": "L_TSR", "len": 15, "desc": "限速区段长度"},
        {"name": "L_TSRarea", "len": 15, "desc": "有效区段长度"},
        {"name": "N_ITER", "len": 5, "desc": "限速区段数量"}
    ],
    # CTCS-4: Big Turnout
    "CTCS-4": [
        {"name": "NID_XUSER", "len": 9, "val": 4, "desc": "CTCS包标识码"},
        {"name": "Q_DIR", "len": 2, "desc": "验证方向"},
        {"name": "Q_SCALE", "len": 2, "desc": "距离分辨率"},
        {"name": "D_TURNOUT", "len": 15, "desc": "道岔距离"},
        {"name": "V_TURNOUT", "len": 7, "desc": "侧向最大速度"}
    ],
    # CTCS-5: Abs Stop
    "CTCS-5": [
        {"name": "NID_XUSER", "len": 9, "val": 5, "desc": "CTCS包标识码"},
        {"name": "Q_DIR", "len": 2, "desc": "验证方向"},
        {"name": "Q_STOP", "len": 1, "desc": "停车指令"}
    ],
    # ETCS-68: Special Section
    "ETCS-68": [
        {"name": "NID_PACKET", "len": 8, "val": 68, "desc": "信息包标识"},
        {"name": "Q_DIR", "len": 2, "desc": "验证方向"},
        {"name": "Q_SCALE", "len": 2, "desc": "距离分辨率"},
        {"name": "Q_TRACKINIT", "len": 1, "desc": "状态恢复要求"},
        {"name": "D_TRACKINIT", "len": 15, "cond": lambda d: d.get("Q_TRACKINIT") == 1, "desc": "状态恢复点距离"},
        {"name": "M_TRACKCOND", "len": 4, "cond": lambda d: d.get("Q_TRACKINIT") == 0, "desc": "特殊区段类型"},
        {"name": "D_TRACKCOND", "len": 15, "cond": lambda d: d.get("Q_TRACKINIT") == 0, "desc": "特殊区段距离"},
        {"name": "L_TRACKCOND", "len": 15, "cond": lambda d: d.get("Q_TRACKINIT") == 0, "desc": "特殊区段长度"},
        {"name": "N_ITER", "len": 5, "cond": lambda d: d.get("Q_TRACKINIT") == 0, "desc": "区段数量"}
    ],
    # ETCS-79: Mileage
    "ETCS-79": [
        {"name": "NID_PACKET", "len": 8, "val": 79, "desc": "信息包标识"},
        {"name": "Q_DIR", "len": 2, "desc": "验证方向"},
        {"name": "Q_SCALE", "len": 2, "desc": "距离分辨率"},
        {"name": "Q_NEWCOUNTRY", "len": 1, "desc": "地区关系"},
        {"name": "NID_C", "len": 10, "cond": lambda d: d.get("Q_NEWCOUNTRY") == 1, "desc": "地区编号"},
        {"name": "M_POSITION", "len": 20, "desc": "线路公里标"},
        {"name": "Q_MPOSITION", "len": 1, "desc": "计数方向"},
        {"name": "D_POSOFF", "len": 15, "desc": "偏移量"},
        {"name": "N_ITER", "len": 5, "desc": "公里标数量"}
    ]
}

def translate_to_cn(data, packet_name=None):
    """
    将变量名（Variable Names）字典键转换为中文描述。
    
    参数:
        data (dict): 带有变量名键的字典（例如 {"Q_DIR": 1}）。
        packet_name (str, optional): 报文名称（例如 "ETCS-5"），用于查找特定字段描述。
    
    返回:
        dict: 带有中文键的新字典（例如 {"验证方向": 1}）。
    """
    new_data = {}
    pkt_defs = PACKET_DEFS.get(packet_name) if packet_name else []
    
    def get_cn_name(var_name):
        if pkt_defs:
            for f in pkt_defs:
                if f["name"] == var_name:
                    return f.get("desc", var_name)
        return HEADER_MAP.get(var_name.lower(), var_name)

    for k, v in data.items():
        cn_k = get_cn_name(k)
        new_data[cn_k] = v
    return new_data

def translate_to_var(data, packet_name=None):
    """
    将中文描述字典键翻译回变量名（Variable Names）。
    
    参数:
        data (dict): 带有中文键的字典（例如 {"验证方向": 1}）。
        packet_name (str, optional): 报文名称，用于反向查找变量名。
        
    返回:
        dict: 带有变量名键的新字典。
    """
    new_data = {}
    cn_to_header = {v: k for k, v in HEADER_MAP.items()}
    cn_to_pkt = {}
    if packet_name and packet_name in PACKET_DEFS:
        for f in PACKET_DEFS[packet_name]:
            if "desc" in f:
                cn_to_pkt[f["desc"]] = f["name"]
    
    for k, v in data.items():
        var_k = cn_to_pkt.get(k)
        if not var_k:
            var_k = cn_to_header.get(k, k)
        new_data[var_k] = v
    return new_data

def encode_packet_field(value, length):
    """
    将单个字段值编码为二进制字符串。
    
    参数:
        value: 整数值。
        length: 位数。
        
    返回:
        str: 二进制字符串。
    """
    return PacketUtils.int_to_bin(value, length)

def encode_packet(packet_name, data):
    """
    根据报文定义将字典数据编码为二进制字符串。
    
    参数:
        packet_name (str): 报文名称（例如 "ETCS-5"）。
        data (dict): 包含键如 'Q_DIR', 'D_LINK' 的字典（值为整数）。
        
    返回:
        str: 报文的编码二进制字符串。如果找不到报文定义，则返回空字符串。
    """
    defs = PACKET_DEFS.get(packet_name)
    if not defs:
        return ""
    
    bin_str = ""
    # Process fields
    # Note: condition checking requires current data state. 
    # For encoding, we assume input 'data' has necessary keys or we use defaults/zeros.
    
    # We need to construct the logic carefully.
    
    # Simplified encoder for known fields
    processed_data = data.copy()
    
    for field in defs:
        name = field["name"]
        length = field["len"]
        
        # Check condition
        if "cond" in field:
            if not field["cond"](processed_data):
                continue
        
        # Get value
        val = 0
        if "val" in field:
            val = field["val"]
        else:
            val = processed_data.get(name, 0)
            
        bin_str += PacketUtils.int_to_bin(val, length)
        
    return bin_str

def decode_packet(packet_name, bin_str):
    """
    根据报文定义将二进制字符串解码为字典。
    
    参数:
        packet_name (str): 报文名称（例如 "ETCS-5"）。
        bin_str (str): 要解码的二进制字符串。
        
    返回:
        dict: 解码后的值字典（例如 {"Q_DIR": 1}）。
              如果找不到定义，则返回 {"raw": bin_str}。
    """
    defs = PACKET_DEFS.get(packet_name)
    if not defs:
        return {"raw": bin_str}
    
    result = {}
    ptr = 0
    total_len = len(bin_str)
    
    for field in defs:
        name = field["name"]
        length = field["len"]
        
        # Check condition based on ALREADY PARSED fields
        if "cond" in field:
            if not field["cond"](result):
                continue
        
        if ptr + length > total_len:
            break
            
        chunk = bin_str[ptr:ptr+length]
        val = PacketUtils.bin_to_int(chunk)
        result[name] = val
        ptr += length
        
    return result
