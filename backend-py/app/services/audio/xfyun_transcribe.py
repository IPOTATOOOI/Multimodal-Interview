import os
import time
import hmac
import json
import base64
import hashlib
import requests
import urllib
from typing import Dict, Any

LFASR_HOST = 'https://raasr.xfyun.cn/v2/api'
API_UPLOAD = '/upload'
API_GET_RESULT = '/getResult'

APPID = os.getenv("XUNFEI_LFASR_APP_ID", "")
SECRET_KEY = os.getenv("XUNFEI_LFASR_SECRET_KEY", "")

class XunfeiTranscriber:
    def __init__(self):
        if not APPID or not SECRET_KEY:
            raise RuntimeError("XUNFEI_LFASR_APP_ID and XUNFEI_LFASR_SECRET_KEY must be configured")
        self.appid = APPID
        self.secret_key = SECRET_KEY
        self.ts = str(int(time.time()))
        self.signa = self._get_signa()

    def _get_signa(self) -> str:
        """生成签名"""
        m2 = hashlib.md5()
        m2.update((self.appid + self.ts).encode('utf-8'))
        md5 = m2.hexdigest().encode('utf-8')
        signa = hmac.new(self.secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa).decode('utf-8')
        return signa

    def upload(self, file_path: str) -> Dict[str, Any]:
        """上传音频文件"""
        file_len = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)

        # 根据文件大小估算音频时长（粗略估算）
        # 假设音频文件大小与时长成正比，基于常见的音频格式
        estimated_duration = max(1, min(3600, file_len // 16000))  # 假设16KB/秒，限制在1-3600秒之间
        duration_str = str(estimated_duration)
        
        print(f"估算音频时长: {duration_str}秒 (基于文件大小: {file_len}字节)")

        param_dict = {
            'appId': self.appid,
            'signa': self.signa,
            'ts': self.ts,
            'fileSize': file_len,
            'fileName': file_name,
            'duration': duration_str
        }

        print(f"上传音频文件 - 文件名: {file_name}, 大小: {file_len}字节, 时长: {duration_str}秒")

        with open(file_path, 'rb') as f:
            data = f.read()

        response = requests.post(
            f"{LFASR_HOST}{API_UPLOAD}?{urllib.parse.urlencode(param_dict)}",
            headers={"Content-Type": "application/json"},
            data=data
        )
        result = response.json()

        if result.get('code') != '000000':
            raise RuntimeError(f"上传失败: {result}")

        print(f"音频文件上传成功 - orderId: {result.get('content', {}).get('orderId', 'unknown')}")
        return result

    def get_result(self, order_id: str) -> Dict[str, Any]:
        """获取转写结果"""
        param_dict = {
            'appId': self.appid,
            'signa': self.signa,
            'ts': self.ts,
            'orderId': order_id,
            'resultType': "transfer,predict"
        }

        status = 3
        max_retries = 60  # 最多等待5分钟
        retry_count = 0
        
        while status == 3 and retry_count < max_retries:
            response = requests.post(
                f"{LFASR_HOST}{API_GET_RESULT}?{urllib.parse.urlencode(param_dict)}",
                headers={"Content-Type": "application/json"}
            )
            result = response.json()
            info = result.get('content', {}).get('orderInfo', {})
            status = info.get('status', -1)
            fail_type = info.get('failType', 0)
            
            print(f"转写状态检查 - orderId: {order_id}, status: {status}, failType: {fail_type}")
            
            if status == 4:
                print(f"转写成功完成 - orderId: {order_id}")
                return result
            elif status == -1:
                # 转写失败，检查失败类型
                fail_type_messages = {
                    1: "音频文件格式不支持",
                    2: "音频文件损坏",
                    3: "音频文件过大",
                    4: "音频文件过小",
                    5: "音频文件时长超出限制",
                    6: "音频文件质量太差，无法识别",
                    7: "音频文件包含噪音过大",
                    8: "音频文件采样率不支持",
                    9: "音频文件声道数不支持",
                    10: "音频文件编码格式不支持"
                }
                
                fail_message = fail_type_messages.get(fail_type, f"未知错误类型: {fail_type}")
                print(f"转写失败 - orderId: {order_id}, failType: {fail_type}, 原因: {fail_message}")
                
                # 检查是否包含有效的转写结果（即使失败也可能有部分结果）
                order_result = result.get('content', {}).get('orderResult', '')
                trans_result = result.get('content', {}).get('transResult', '')
                
                if order_result and 'lattice' in order_result:
                    print(f"发现部分转写结果，尝试解析 - orderId: {order_id}")
                    return result
                elif trans_result:
                    print(f"发现转写结果，尝试解析 - orderId: {order_id}")
                    return result
                else:
                    raise RuntimeError(f"转写失败: {fail_message} (failType: {fail_type})")
                
            retry_count += 1
            time.sleep(5)
        
        if retry_count >= max_retries:
            raise RuntimeError(f"转写超时，超过最大重试次数: {max_retries}")
        
        raise RuntimeError(f"意外的转写状态: {status}")

    def transcribe_file(self, file_path: str) -> str:
        """上传并获取转写结果，返回合并后的文本"""
        upload_resp = self.upload(file_path)
        order_id = upload_resp['content']['orderId']
        result = self.get_result(order_id)
        
        # 解析转写结果
        order_result = result.get('content', {}).get('orderResult', '')
        trans_result = result.get('content', {}).get('transResult', '')
        
        if not order_result and not trans_result:
            print(f"警告: 未找到转写结果 - orderId: {order_id}")
            return ""
            
        try:
            # 优先尝试解析 orderResult (详细格式)
            if order_result:
                result_json = json.loads(order_result)
                texts = []
                for item in result_json.get('lattice', []):
                    best = json.loads(item.get('json_1best', '{}'))
                    if 'st' in best and 'rt' in best['st']:
                        for rt in best['st']['rt']:
                            if 'ws' in rt:
                                for ws in rt['ws']:
                                    if 'cw' in ws:
                                        for cw in ws['cw']:
                                            texts.append(cw.get('w', ''))
                if texts:
                    print(f"成功解析详细格式转写结果 - orderId: {order_id}")
                    return ''.join(texts)
            
            # 如果详细格式解析失败，尝试解析 transResult (简单格式)
            if trans_result:
                print(f"使用简单格式转写结果 - orderId: {order_id}")
                return trans_result.strip()
            
            print(f"无法解析转写结果 - orderId: {order_id}")
            return ""
            
        except Exception as e:
            print(f"解析转写结果时出错 - orderId: {order_id}, 错误: {str(e)}")
            # 如果解析失败，尝试直接返回 transResult
            if trans_result:
                return trans_result.strip()
            raise RuntimeError(f"解析转写结果失败: {e}")
