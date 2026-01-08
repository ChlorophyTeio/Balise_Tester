"""Configuration manager module using JSON and CSV files."""

import csv
import json
import os
import sys
from typing import Dict, List, Optional


class ConfigManager:
    """Configuration manager class for loading and saving application data.

    Manages balises, stations, trains, and line configuration.
    """

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the ConfigManager.

        Args:
            config_dir: Directory path for configuration files. 
                        Defaults to data/config in project root.
        """
        if config_dir is None:
            if getattr(sys, 'frozen', False):
                # Running in a bundle
                project_root = sys._MEIPASS
            else:
                # Use absolute path relative to this file
                # .../balise_tester/core/config_manager.py -> .../
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(current_dir))
            self.config_dir = os.path.join(project_root, "data", "config")
        else:
            self.config_dir = config_dir
            
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        self.balise_file = os.path.join(self.config_dir, "balises.json")
        self.balise_csv_file = os.path.join(self.config_dir, "balises.csv")
        self.station_file = os.path.join(self.config_dir, "stations.json")
        self.train_file = os.path.join(self.config_dir, "trains.json")
        self.line_file = os.path.join(self.config_dir, "line_config.json")

    def load_config(self, file_path):
        """
        加载JSON格式的配置文件列表。
        
        Args:
            file_path (str): 配置文件路径。
            
        Returns:
            list: 配置数据列表。如果加载失败或文件不存在，返回空列表。
        """
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def load_config_dict(self, file_path):
        """
        加载JSON格式的配置文件字典。
        
        Args:
            file_path (str): 配置文件路径。
            
        Returns:
            dict: 配置数据字典。如果加载失败或文件不存在，返回空字典。
        """
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_config(self, file_path, data):
        """
        保存数据到JSON配置文件。
        
        Args:
            file_path (str): 保存路径。
            data (list|dict): 要保存的数据。
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def process_balise_groups(balises: List[Dict]):
        """Process balise ID logic (In-place).

        Groups balises by father_balise, assigns missing sub_ids sequentially,
        and calculates n_total and q_link fields.
        """
        # Group balises by father_balise
        groups = {}
        for balise in balises:
            father_id = str(balise.get("father_balise", "")).strip()
            if father_id:
                if father_id not in groups:
                    groups[father_id] = []
                groups[father_id].append(balise)
            else:
                # No father, treat as single
                balise["sub_id"] = "0"
                balise["n_pig"] = "000"
                balise["n_total"] = "1"
                balise["q_link"] = "0"

        # Process groups
        for father_id, group in groups.items():
            count = len(group)
            
            # Sort by explicit sub_id (if numeric) or location to have a consistent order
            # But we must respect existing sub_ids if user set them.
            # Strategy:
            # 1. Identify occupied sub_ids
            used_ids = set()
            for b in group:
                sid = str(b.get("sub_id", "")).strip()
                if sid.isdigit():
                    used_ids.add(int(sid))
            
            # 2. Fill missing sub_ids
            next_id = 0
            for b in group:
                sid = str(b.get("sub_id", "")).strip()
                if not sid or not sid.isdigit():
                    while next_id in used_ids:
                        next_id += 1
                    b["sub_id"] = str(next_id)
                    used_ids.add(next_id)
            
            # 3. Update n_pig, n_total, q_link for ALL in group
            for b in group:
                b["n_total"] = str(count)
                
                # Check sub_id to assume n_pig
                try:
                    s_id = int(b.get("sub_id", 0))
                    # N_PIG is usually 3 bits bin string "000" to "111"
                    b["n_pig"] = f"{s_id:03b}"
                except ValueError:
                    b["n_pig"] = "000"

                if count >= 2:
                    b["q_link"] = "1"
                else:
                    b["q_link"] = "0"

    def load_balises(self):
        """
        加载应答器配置数据。
        优先尝试加载CSV格式，如果不存在则加载JSON格式。
        
        Returns:
            list: 应答器配置列表。
        """
        # Priority: CSV -> JSON
        if os.path.exists(self.balise_csv_file):
            try:
                with open(self.balise_csv_file, 'r', encoding='utf-8-sig', newline='') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    if len(rows) < 3:
                        # Not enough data (Header + Explanation + Data)
                        return []
                    
                    header = rows[0]
                    # Skip explanation row (rows[1])
                    data_rows = rows[2:]
                    
                    result = []
                    for row in data_rows:
                        item = {}
                        for i, value in enumerate(row):
                            if i < len(header):
                                key = header[i]
                                if value.strip():
                                    item[key] = value
                        
                        # Convert types for core fields
                        if "location" in item:
                            try:
                                item["location"] = float(item["location"])
                            except ValueError:
                                item["location"] = 0.0
                        if "type" in item:
                            try:
                                item["type"] = int(item["type"])
                            except ValueError:
                                item["type"] = 0
                                
                        result.append(item)
                    
                    # Process groups logic
                    self.process_balise_groups(result)
                    return result
            except Exception as e:
                print(f"Error loading Balise CSV: {e}")
                return []
        
        return self.load_config(self.balise_file)

    def save_balises(self, data):
        """
        保存应答器配置数据到CSV文件。
        会自动包含标准字段和报文包字段，并添加中文表头说明。
        
        Args:
            data (list): 应答器配置数据列表。
        """
        # Process groups before save
        if data:
            self.process_balise_groups(data)

        # Save to CSV
        if not data:
            with open(self.balise_csv_file, 'w', encoding='utf-8-sig', newline='') as f:
                pass
            return

        # Define standard fields and packet fields
        standard_fields = [
            "name", "location", "type", "father_balise", "sub_id", 
            "q_updown", "m_version", "q_media", "n_pig", "n_total", 
            "m_dup", "m_mcount", "nid_c", "nid_bg", "q_link"
        ]
        
        # Packet fields mapping
        # Updated based on Information Packet MD
        packet_fields = [
            "ETCS-5", "CTCS-1", "ETCS-21", "ETCS-27", "ETCS-41", 
            "ETCS-42", "ETCS-44", "ETCS-46", "ETCS-68", "ETCS-72", 
            "ETCS-79", "ETCS-131", "ETCS-132", "ETCS-137", "ETCS-254",
            "CTCS-2", "CTCS-4", "CTCS-5"
        ]
        
        all_fields = standard_fields + packet_fields
        
        # Explanation row
        explanations = [
            "名称", "位置(km)", "类型(0=无/1=有)", "父应答器名称", "组内编号",
            "信息方向", "版本", "传输媒介", "组内位置", "组内总数",
            "复制关系", "报文计数器", "地区编号", "应答器ID", "链接关系"
        ]
        explanations += ["包信息: " + p for p in packet_fields]
        
        rows = []
        rows.append(all_fields)
        rows.append(explanations)
        
        for item in data:
            row = []
            for field in all_fields:
                row.append(str(item.get(field, "")))
            rows.append(row)
            
        try:
            with open(self.balise_csv_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
        except Exception as e:
            print(f"Error saving Balise CSV: {e}")

    def load_stations(self):
        """
        加载车站配置数据。
        
        Returns:
            list: 车站配置列表。
        """
        return self.load_config(self.station_file)

    def save_stations(self, data):
        """
        保存车站配置数据。
        
        Args:
            data (list): 车站配置列表。
        """
        self.save_config(self.station_file, data)

    def load_trains(self):
        """
        加载列车配置数据。
        
        Returns:
            list: 列车配置列表。
        """
        return self.load_config(self.train_file)

    def save_trains(self, data):
        """
        保存列车配置数据。
        
        Args:
            data (list): 列车配置列表。
        """
        self.save_config(self.train_file, data)

    def load_line_config(self):
        """
        加载线路全局配置数据。
        
        Returns:
            dict: 线路配置字典。
        """
        return self.load_config_dict(self.line_file)

    def save_line_config(self, data):
        """
        保存线路全局配置数据。
        
        Args:
            data (dict): 线路配置字典。
        """
        self.save_config(self.line_file, data)
