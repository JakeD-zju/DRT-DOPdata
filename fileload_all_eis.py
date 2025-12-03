# -*- coding: utf-8 -*-
"""
Created on Mon Jul  7 19:39:00 2025

@author: satellite
"""

import pandas as pd
from pandas import DataFrame
from datetime import datetime
import warnings
import numpy as np
from typing import Union, Optional
from pathlib import Path
import calendar
import time
# import re

class EisDataReader:
    """
    电化学阻抗谱(EIS)数据读取类，支持读取Gamry、Biologic、Zplot、Relaxis和CHI等格式的EIS数据文件
    """
    _known_sources = ['gamry', 'zplot', 'biologic', 'relaxis', 'CHI']
    
    def __init__(self):
        """初始化EIS数据读取器"""
        self.data = None
        self.source = None
        self.timestamp = None
        self.file_path = None
    
    def get_extension(self, file: Union[Path, str]) -> str:
        """获取文件扩展名"""
        file = Path(file)
        return file.name.split('.')[-1].lower()
    
    def get_file_source(self, text: str) -> Optional[str]:
        """确定文件来源"""
        header = text.split('\n')[0]
        
        if header == 'EXPLAIN':
            return 'gamry'
        elif header == 'ZPLOT2 ASCII':
            return 'zplot'
        elif header.startswith('BIO-LOGIC'):
            return 'biologic'
        elif header.split(' ')[0] == 'RelaxIS':
            return 'relaxis'
        elif self._is_chi_header(header):
            return 'CHI'
        else:
            return None
        
    def _is_chi_header(self, header: str) -> bool:
        """检查是否为CHI格式的文件头"""
        try:
            # 尝试解析CHI格式的时间戳
            header = header.replace("May", "May.")
            header = header.replace("June", "Jun.")
            header = header.replace("July", "Jul.")
            header = header.replace("Sept.", "Sep.")
            datetime.strptime(header, "%b. %d, %Y %H:%M:%S")
            return True
        except ValueError:
            return False
    
    def read_txt(self, file: Union[Path, str]) -> str:
        """读取文本文件，处理编码问题"""
        try:
            with open(file, 'r') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file, 'r', encoding='latin1') as f:
                return f.read()
    
    def check_source(self, source: str) -> None:
        """检查数据源是否被识别"""
        if source not in self._known_sources:
            raise ValueError(f'未识别的数据源 {source}。支持的数据源: {", ".join(self._known_sources)}')
    
    def read_with_source(self, file: Union[Path, str], source: Optional[str] = None) -> (str, str):
        """读取文件并确定来源"""
        text = self.read_txt(file)
        
        if source is None:
            source = self.get_file_source(text)
            if source is None:
                # raise ValueError('无法识别文件格式。若要读取此文件，请通过source参数手动指定文件格式。'
                #                 f'支持的数据源: {", ".join(self._known_sources)}')
                return None
        
        self.check_source(source)
        return text, source
    
    def get_custom_file_time(self, file: Union[Path, str]) -> float:
        """从pygamry生成的文件中获取时间戳"""
        txt = self.read_txt(file)

        date_start = txt.find('DATE')
        date_end = txt[date_start:].find('\n') + date_start
        date_line = txt[date_start:date_end]
        date_str = date_line.split('\t')[2]

        time_start = txt.find('TIME')
        time_end = txt[time_start:].find('\n') + time_start
        time_line = txt[time_start:time_end]
        time_str = time_line.split('\t')[2]

        dt_str = date_str + ' ' + time_str
        time_format_code = "%Y/%m/%d %H:%M:%S"    
        
        file_time = time.strptime(dt_str, time_format_code)
        return float(calendar.timegm(file_time))
    
    def read_mpr(self, file: Union[Path, str]):
        """读取Biologic的MPR文件"""
        try:
            from galvani.BioLogic import MPRfile
            file = Path(file)
            return MPRfile(file.__str__())
        except ImportError:
            raise ImportError("无法导入MPRfile类，请确保安装了galvani库")
    
    def get_timestamp(self, file: Union[Path, str], source: Optional[str] = None) -> datetime:
        """从文件中获取实验时间戳"""
        txt, source = self.read_with_source(file, source)
        self.file_path = file
        self.source = source
        
        if source == 'gamry':
            try:
                date_start = txt.find('DATE')
                # print(date_start)
                date_end = txt[date_start:].find('\n') + date_start
                date = txt[date_start:date_end].split('\t')[2]

                time_start = txt.find('TIME')
                time_end = txt[time_start:].find('\n') + time_start
                time_txt = txt[time_start:time_end].split('\t')[2]

                timestr = date + ' ' + time_txt
                dt = datetime.strptime(timestr, "%Y/%m/%d %H:%M:%S")
            except ValueError:
                time_sec = self.get_custom_file_time(file)
                dt = datetime.utcfromtimestamp(time_sec)
            # print(dt)

        elif source == 'zplot':
            date_start = txt.find('Date')
            date_end = txt[date_start:].find('\n') + date_start
            date = txt[date_start:date_end].split()[1]

            time_start = txt.find('Time')
            time_end = txt[time_start:].find('\n') + time_start
            time_txt = txt[time_start:time_end].split()[1]

            timestr = date + ' ' + time_txt
            dt = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
            
        elif source == 'biologic':
            try:
                mpr = self.read_mpr(file)
                dt = mpr.timestamp or mpr.startdate
                print(dt)
                if not dt:
                    raise ValueError("无法从MPR文件中获取时间戳")
            except Exception as e:
                warnings.warn(f"使用MPR解析失败：{e}")
        elif source == 'CHI':
            try:
                # 尝试解析CHI格式的时间戳
                header = txt.split('\n')[0]
                header = header.replace("May", "May.")
                header = header.replace("June", "Jun.")
                header = header.replace("July", "Jul.")
                dt = datetime.strptime(header, "%b. %d, %Y %H:%M:%S")
                # dt = _is_chi_header()
            except ValueError:
                warnings.warn("无法解析CHI格式的时间戳")
                dt = datetime.fromtimestamp(Path(file).stat().st_mtime)
        
        self.timestamp = dt
        return dt

    def _get_read_kwargs(self, text: str, source: str, data_start_str: Optional[str] = None, remove_blank: bool = True):
        """获取读取数据的参数"""
        self.check_source(source)
        
        if source == 'gamry':
            data_index = text.upper().find(data_start_str) + 1
            pretxt = text[:data_index]
            table_text = text[data_index:]
            
            header_start = table_text.find('\n') + 1
            header_end = header_start + table_text[header_start:].find('\n')
            names = table_text[header_start:header_end].split('\t')
            
            unit_end = header_end + 1 + table_text[header_end + 1:].find('\n')
            units = table_text[header_end + 1:unit_end].split('\t')
            
            skiprows = len(pretxt.split('\n')) + 2

            if text.find('EXPERIMENTABORTED') > -1:
                skipfooter = len(text[text.find('EXPERIMENTABORTED'):].split('\n')) - 1
            else:
                skipfooter = 0
                
            kwargs = dict(
                sep='\t', 
                skiprows=skiprows,
                skipfooter=skipfooter,
                header=None, 
                names=names,
                engine='python'
            )
        elif source == 'biologic':
            nh_str = 'Nb header lines :'
            nh_index = text.find(nh_str)
            if nh_index > 0:
                nh = int(text[nh_index + len(nh_str):].split('\n')[0].strip())
            else:
                nh = 0
                
            header_row = text.split('\n')[nh - 1]
            sep = '\t' if len(header_row.split('\t')) > 1 else ','
            
            names = header_row.split(sep)
            
            kwargs = dict(
                sep=sep,
                skiprows=nh,
                names=names,
            )
        elif source == 'zplot':
            data_index = text.find('End Comments')
            pretxt = text[:data_index]
            table_text = text[data_index:]
            
            names = pretxt.split('\n')[-2].strip().split('\t')
            skiprows = len(pretxt.split('\n'))

            kwargs = dict(
                sep='\t', 
                skiprows=skiprows, 
                header=None, 
                names=names
            )
        elif source == 'relaxis':
            header_index = text.find('\nData: ')
            skiprows = len(text[:header_index].split('\n')) + 2
            
            header_line = text[header_index + 1:].split('\n')[0]
            header = [h.replace('Data: ', '') for h in header_line.split('\t')]
            
            kwargs = dict(
                sep='\t', 
                skiprows=skiprows, 
                header=None, 
                names=header
            )
        else:
            sep = '\t' if len(text.split('\t')) > 1 else None
            kwargs = dict(sep=sep)
        
        if 'names' in kwargs:
            names = kwargs['names']
            for i, n in enumerate(names):
                if len(n) == 0:
                    names[i] = f'blank{i}'
            usecols = [n for n in names if n.find('blank') == -1]
            kwargs['names'] = names
            if remove_blank:
                kwargs['usecols'] = usecols
        
        return kwargs
    
    def find_time_column(self, data: DataFrame) -> str:
        """查找时间列"""
        if self.source == 'gamry':        
            return np.intersect1d(['Time', 'T', 'time'], data.columns)[0]
        elif self.source == 'biologic':
            return 'time/s'
        else:
            raise ValueError(f"不支持的数据源 {self.source} 的时间列查找")
    
    def append_timestamp(self, data: DataFrame) -> None:
        """向数据中添加时间戳"""
        if self.timestamp is None:
            warnings.warn(f"无法为文件 {self.file_path} 添加时间戳，因为未设置时间戳")
            return
            
        try:
            # 查找时间列
            time_col_candidates = ['Time', 'T', 'time', 'time/s', 'elapsed']
            time_col = next((col for col in time_col_candidates if col in data.columns), None)
            # print(time_col)
            
            if time_col:
                # 转换为时间增量
                time_deltas = pd.to_timedelta(data[time_col], unit='s')
                # 添加到时间戳
                data['timestamp'] = self.timestamp + time_deltas
            # else:
                # warnings.warn(f"在文件 {self.file_path} 中找不到时间列")
        except Exception as err:
            warnings.warn(f'为文件 {Path(self.file_path).name} 添加时间戳失败: {err}')
    
    def get_eis(self, file: Union[Path, str], min_freq: Optional[float] = None, 
               max_freq: Optional[float] = None) -> DataFrame:
        """
        读取 EIS 数据并返回DataFrame
        
        参数:
        file: 文件路径
        min_freq: 最小频率 (可选)
        max_freq: 最大频率 (可选)
        
        返回:
        DataFrame: 包含所有EIS数据的DataFrame
        """
        file_ext = self.get_extension(file)
        file_path = Path(file)
        
        # 处理MPR文件 (Biologic格式)
        if file_ext == 'mpr':
            try:
                mpr = self.read_mpr(file_path)
                data = pd.DataFrame(mpr.data)
                
                # 标准化列名
                col_map = {
                    'freq/Hz': 'Freq',
                    'Re(Z)/Ohm': 'Zreal',
                    '-Im(Z)/Ohm': 'Zimag',
                    '|Z|/Ohm': 'Zmod',
                    'Phase(Z)/deg': 'Zphz'
                }
                data['-Im(Z)/Ohm'] *= -1
                data = data.rename(col_map, axis=1)
                
                # 应用列名映射
                for orig, new in col_map.items():
                    if orig in data.columns:
                        data.rename(columns={orig: new}, inplace=True)
                
                # 添加时间戳
                self.timestamp = mpr.timestamp or mpr.startdate
                if 'time/s' in data.columns and self.timestamp:
                    data['timestamp'] = self.timestamp + pd.to_timedelta(data['time/s'], unit='s')
                
                return data
            except Exception as e:
                raise RuntimeError(f"读取MPR文件失败: {e}")
        
        # 处理其他文本格式的EIS文件
        text = self.read_txt(file_path)
        # print(text)
        
        # 尝试识别为CHI格式
        if file_ext in ['txt', 'csv'] and ('Freq/Hz' in text):
            try:
                # 定位数据起始位置
                index = text.find('Freq/Hz')
                if index == -1:
                    raise ValueError(f"在文件 {file_path.name} 中找不到 'Freq/Hz' 表头")
                
                pretxt = text[:index]
                header_index = len(pretxt.split('\n')) - 1
                
                # 读取数据
                data = pd.read_csv(
                    file_path, 
                    sep=',', 
                    skiprows=header_index,
                    skip_blank_lines=True
                )
                
                # 清理列名
                data.columns = data.columns.str.strip()
                
                # 重命名列为标准化名称
                column_map = {
                    "Freq/Hz": "Freq",
                    "Z'/ohm": "Zreal",
                    "Z\"/ohm": "Zimag",
                    "Z/ohm": "Zmod",
                    "Phase/deg": "Zphz"
                }
                
                # 应用列名映射
                for orig, new in column_map.items():
                    if orig in data.columns:
                        data.rename(columns={orig: new}, inplace=True)
                
                # 添加计算列
                if "Zreal" in data.columns and "Zimag" in data.columns:
                    if "Zmod" not in data.columns:
                        data["Zmod"] = np.sqrt(data["Zreal"]**2 + data["Zimag"]**2)
                    if "Zphz" not in data.columns:
                        data["Zphz"] = np.arctan2(data["Zimag"], data["Zreal"]) * 180 / np.pi
                
                # 获取并添加时间戳
                self.get_timestamp(file_path, source='CHI')
                if self.timestamp and 'Time' in data.columns:
                    data['timestamp'] = self.timestamp + pd.to_timedelta(data['Time'], unit='s')
                
                return data
            except Exception as e:
                warnings.warn(f"作为CHI格式读取失败，尝试其他格式: {e}")
        
        # 对于其他格式的文件
        try:
            # 确定文件来源
            source = self.get_file_source(text)
            # print(source)
            if not source:
                raise ValueError("无法识别文件格式")
            
            # 设置数据起始标识
            if source == 'gamry':
                data_start_str = '\nZCURVE'
                # print(data_start_str)
            elif source == 'zplot':
                data_start_str = None
            elif source == 'relaxis':
                data_start_str = None
            else:
                data_start_str = None

            # # 获取读取参数
            # kwargs = self._get_read_kwargs(text, source, data_start_str)
            # print(kwargs)
            # # 读取数据
            # data = pd.read_csv(file_path, **kwargs)
            
            read_kw = {
                'encoding': None,
                'encoding_errors': 'ignore',
                'engine': 'python'
            }
            read_kw.update(self._get_read_kwargs(text, source, data_start_str))
            # read_kw.update(kwargs)
            # print(read_kw)
            
            data = pd.read_csv(file, **read_kw)

            
            # 获取并添加时间戳
            self.get_timestamp(file_path, source)
            if self.timestamp:
                self.append_timestamp(data)
            
            # 重命名列为标准化名称
            if source == 'zplot':
                col_map = {"Z'(a)": "Zreal", "Z''(b)": "Zimag", "Freq(Hz)": "Freq"}
                data = data.rename(columns=col_map)
                if "Zreal" in data.columns and "Zimag" in data.columns:
                    data['Zmod'] = np.sqrt(data['Zreal']**2 + data['Zimag']**2)
                    data['Zphz'] = np.arctan2(data['Zimag'], data['Zreal']) * 180 / np.pi
            elif source == 'relaxis':
                col_map = {
                    "Frequency": "Freq", 
                    "Z'": "Zreal", 
                    "Z''": "Zimag", 
                    "|Z|": "Zmod",
                    "Theta (Z)": "Zphz"
                }
                data = data.rename(columns=col_map)
            
            return data
        except Exception as e:
            raise RuntimeError(f"读取文件 {file_path.name} 失败: {e}")

    def get_eis_tuple(self, file: Union[Path, str], min_freq: Optional[float] = None, 
                     max_freq: Optional[float] = None) -> tuple:
        """
        从EIS文件中获取频率和阻抗的元组
        
        参数:
        file: 文件路径
        min_freq: 最小频率 (可选)
        max_freq: 最大频率 (可选)
        
        返回:
        tuple: (频率数组, 复数阻抗数组)
        """
        data = self.get_eis(file)
        # print(data)
        
        # 确保包含必要的列
        if 'Freq' not in data.columns or 'Zreal' not in data.columns or 'Zimag' not in data.columns:
            raise ValueError("数据中缺少必要的列 (Freq, Zreal, Zimag)")
        
        freq = data['Freq'].values.copy()
        z = data['Zreal'].values.copy() + 1j * data['Zimag'].values.copy()

        # 频率过滤
        if min_freq is not None:
            mask = freq >= min_freq
            freq = freq[mask]
            z = z[mask]

        if max_freq is not None:
            mask = freq <= max_freq
            freq = freq[mask]
            z = z[mask]
        # print(z)

        return freq, z
