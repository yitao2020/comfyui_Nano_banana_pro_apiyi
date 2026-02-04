import os
import base64
import io
import json
import torch
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import traceback

class NanoBananaProImageGenerator:
    """NanoBanana Pro 图像生成节点 - 支持文本和图像输入"""
    
    # 支持的宽高比
    ASPECT_RATIOS = ["auto", "1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "21:9", "5:4", "4:5"]
    
    # 支持的分辨率
    RESOLUTIONS = ["1K", "2K", "4K"]
    
    # 超时配置（秒）
    TIMEOUT_MAP = {"1K": 180, "2K": 300, "4K": 360}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {
                    "default": "", 
                    "multiline": False,
                    "placeholder": "sk-your-api-key"
                }),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "一只可爱的小猫坐在花园里，油画风格，高清，细节丰富"
                }),
                "aspect_ratio": (cls.ASPECT_RATIOS, {"default": "auto"}),
                "resolution": (cls.RESOLUTIONS, {"default": "2K"}),
                "estimated_time": ("STRING", {
                    "default": "⏱️ 预计时间: 2K约20-60秒 | 1K约10-30秒 | 4K约30-90秒",
                    "multiline": False,
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff,
                    "step": 1,
                    "display": "number"
                }),
            },
            "optional": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    FUNCTION = "generate_image"
    CATEGORY = "NanoBanana Pro"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """当 seed 为 0 时，每次都生成新的随机值，强制重新执行"""
        seed = kwargs.get('seed', 0)
        if seed == 0:
            # 返回随机值，强制每次都重新执行
            import random
            return random.random()
        # 否则返回 seed 值，相同 seed 会使用缓存
        return seed
    
    def __init__(self):
        """初始化节点"""
        self.log_messages = []
        # 获取节点所在目录
        self.node_dir = os.path.dirname(os.path.abspath(__file__))
        self.key_file = os.path.join(self.node_dir, "api_key.txt")
        self.api_url = "https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent"
    
    def log(self, message):
        """记录日志信息"""
        print(f"[NanoBanana Pro] {message}")
        if hasattr(self, 'log_messages'):
            self.log_messages.append(message)
        return message
    
    def calculate_aspect_ratio(self, width, height):
        """根据图像尺寸计算最接近的标准宽高比"""
        if width == 0 or height == 0:
            return "1:1"
        
        # 计算实际比例
        actual_ratio = width / height
        
        # 定义标准宽高比及其数值
        standard_ratios = {
            "1:1": 1.0,
            "5:4": 1.25,
            "4:3": 1.333,
            "3:2": 1.5,
            "16:9": 1.778,
            "21:9": 2.333,
            "4:5": 0.8,
            "3:4": 0.75,
            "2:3": 0.667,
            "9:16": 0.5625,
        }
        
        # 找到最接近的标准比例
        closest_ratio = "1:1"
        min_difference = float('inf')
        
        for ratio_name, ratio_value in standard_ratios.items():
            difference = abs(actual_ratio - ratio_value)
            if difference < min_difference:
                min_difference = difference
                closest_ratio = ratio_name
        
        self.log(f"图像尺寸 {width}x{height}，实际比例 {actual_ratio:.3f}，匹配到标准比例: {closest_ratio}")
        return closest_ratio
    
    def get_api_key(self, user_input_key):
        """获取API密钥，优先使用用户输入的密钥"""
        # 如果用户输入了有效的密钥，使用并保存
        if user_input_key and len(user_input_key) > 10:
            self.log("使用用户输入的API密钥")
            # 保存到文件中
            try:
                with open(self.key_file, "w", encoding="utf-8") as f:
                    f.write(user_input_key)
                self.log("已保存API密钥到节点目录")
            except Exception as e:
                self.log(f"保存API密钥失败: {e}")
            return user_input_key
            
        # 如果用户没有输入，尝试从文件读取
        if os.path.exists(self.key_file):
            try:
                with open(self.key_file, "r", encoding="utf-8") as f:
                    saved_key = f.read().strip()
                if saved_key and len(saved_key) > 10:
                    self.log("使用已保存的API密钥")
                    return saved_key
            except Exception as e:
                self.log(f"读取保存的API密钥失败: {e}")
                
        # 如果都没有，返回空字符串
        self.log("警告: 未提供有效的API密钥")
        return ""
    
    def generate_empty_image(self, width=512, height=512):
        """生成空白图像张量"""
        empty_image = np.ones((height, width, 3), dtype=np.float32) * 0.2
        tensor = torch.from_numpy(empty_image).unsqueeze(0)  # [1, H, W, 3]
        self.log(f"创建空白图像: 形状={tensor.shape}")
        return tensor
    
    def image_to_base64(self, image_tensor, max_size=1024, jpeg_quality=90):
        """将ComfyUI图像张量转换为base64字符串，自动压缩大图"""
        try:
            # 从张量获取第一张图像 [B, H, W, C] -> [H, W, C]
            img_array = image_tensor[0].cpu().numpy()
            
            # 转换为0-255范围
            img_array = (img_array * 255).astype(np.uint8)
            
            # 转换为PIL图像
            pil_image = Image.fromarray(img_array)
            
            original_size = (pil_image.width, pil_image.height)
            self.log(f"原始图像尺寸: {pil_image.width}x{pil_image.height}")
            
            # 如果图像太大，按比例缩小到最大边不超过 max_size
            if pil_image.width > max_size or pil_image.height > max_size:
                # 计算缩放比例
                ratio = min(max_size / pil_image.width, max_size / pil_image.height)
                new_width = int(pil_image.width * ratio)
                new_height = int(pil_image.height * ratio)
                
                # 使用高质量的 LANCZOS 重采样
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.log(f"图像已压缩: {original_size[0]}x{original_size[1]} -> {new_width}x{new_height}")
            
            # 转换为base64，使用JPEG格式减小文件大小
            buffered = BytesIO()
            pil_image.save(buffered, format="JPEG", quality=jpeg_quality, optimize=True)
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # 计算压缩后的大小
            compressed_size_kb = len(buffered.getvalue()) / 1024
            self.log(f"图像转换为base64成功，最终尺寸: {pil_image.width}x{pil_image.height}, 大小: {compressed_size_kb:.1f}KB")
            
            return img_base64
        except Exception as e:
            self.log(f"图像转换base64失败: {e}")
            return None
    
    def base64_to_image(self, base64_str):
        """将base64字符串转换为ComfyUI图像张量"""
        try:
            # 解码base64
            image_bytes = base64.b64decode(base64_str)
            
            # 转换为PIL图像
            pil_image = Image.open(BytesIO(image_bytes))
            
            # 确保是RGB模式
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # 转换为numpy数组并归一化到0-1
            img_array = np.array(pil_image).astype(np.float32) / 255.0
            
            # 转换为torch张量 [H, W, C] -> [1, H, W, C]
            img_tensor = torch.from_numpy(img_array).unsqueeze(0)
            
            self.log(f"base64转换为图像成功，形状: {img_tensor.shape}")
            return img_tensor
        except Exception as e:
            self.log(f"base64转换图像失败: {e}")
            traceback.print_exc()
            return None
    
    def generate_image(self, api_key, prompt, aspect_ratio, resolution, estimated_time, seed, image=None):
        """生成图像的主函数"""
        # estimated_time 参数仅用于显示，不参与实际处理
        # seed 参数用于避免缓存，每次改变 seed 会强制重新生成
        
        # 重置日志
        self.log_messages = []
        
        try:
            # 获取API密钥
            actual_api_key = self.get_api_key(api_key)
            
            if not actual_api_key:
                error_message = "错误: 未提供有效的API密钥。请在节点中输入API密钥。"
                self.log(error_message)
                full_text = "## 错误\n" + error_message + "\n\n## 使用说明\n1. 在节点中输入您的API密钥\n2. 密钥将自动保存到节点目录"
                return (self.generate_empty_image(), full_text)
            
            self.log(f"开始生成图像... (Seed: {seed})")
            self.log(f"提示词: {prompt[:100]}..." if len(prompt) > 100 else f"提示词: {prompt}")
            
            # 处理 auto 模式的宽高比
            final_aspect_ratio = aspect_ratio
            if aspect_ratio == "auto":
                if image is not None:
                    # 从输入图像获取尺寸
                    img_height, img_width = image.shape[1], image.shape[2]
                    final_aspect_ratio = self.calculate_aspect_ratio(img_width, img_height)
                    self.log(f"Auto 模式: 根据输入图像自动选择宽高比 {final_aspect_ratio}")
                else:
                    # 没有输入图像时，默认使用 1:1
                    final_aspect_ratio = "1:1"
                    self.log(f"Auto 模式: 未提供输入图像，使用默认宽高比 1:1")
            
            self.log(f"最终宽高比: {final_aspect_ratio}")
            self.log(f"分辨率: {resolution}")
            
            # 构建请求内容
            parts = [{"text": prompt}]
            
            # 如果提供了图像输入，添加到请求中（支持多张图像）
            if image is not None:
                batch_size = image.shape[0]
                self.log(f"检测到 {batch_size} 张输入图像")
                
                # 处理每张图像，并添加权重说明
                for i in range(batch_size):
                    self.log(f"正在处理第 {i+1}/{batch_size} 张图像...")
                    
                    # 获取单张图像
                    single_image = image[i:i+1]
                    
                    # 转换为base64
                    img_base64 = self.image_to_base64(single_image, max_size=1024, jpeg_quality=90)
                    
                    if img_base64:
                        # 根据图像顺序设置权重提示
                        if i == 0:
                            # 第一张图像 - 要修改的基础图
                            weight_text = "This is the BASE image to be modified. Keep its main subject and structure, but apply the style and elements from the reference images."
                            self.log(f"图像 {i+1}: 基础图（要修改的目标图）")
                        elif i == 1:
                            # 第二张图像 - 主要参考（最高权重）
                            weight_text = "This is the PRIMARY STYLE REFERENCE with HIGHEST importance. Apply its artistic style, color palette, and visual characteristics strongly to the base image."
                            self.log(f"图像 {i+1}: 主要参考图（最高权重）")
                        elif i == 2:
                            # 第三张图像 - 次要参考
                            weight_text = "This is a SECONDARY reference with MODERATE importance. Use its elements as additional inspiration and subtle influence."
                            self.log(f"图像 {i+1}: 次要参考图（中等权重）")
                        else:
                            # 第四张及以后 - 辅助参考
                            weight_text = f"This is an AUXILIARY reference #{i+1} with MINIMAL importance. Use it only as subtle inspiration."
                            self.log(f"图像 {i+1}: 辅助参考图（最低权重）")
                        
                        # 添加权重说明文本
                        parts.append({"text": weight_text})
                        
                        # 添加图像数据
                        parts.append({
                            "inlineData": {
                                "mimeType": "image/jpeg",
                                "data": img_base64
                            }
                        })
                
                self.log(f"✅ 成功添加 {batch_size} 张图像到请求中（已设置权重优先级）")
            
            # 构建请求payload
            payload = {
                "contents": [{
                    "parts": parts
                }],
                "generationConfig": {
                    "responseModalities": ["IMAGE"],
                    "imageConfig": {
                        "aspectRatio": final_aspect_ratio,
                        "imageSize": resolution
                    }
                }
            }
            
            # 设置请求头
            headers = {
                "Authorization": f"Bearer {actual_api_key}",
                "Content-Type": "application/json"
            }
            
            # 获取超时时间
            timeout = self.TIMEOUT_MAP.get(resolution, 300)
            
            # 根据分辨率显示预计时间
            estimated_times = {
                "1K": "10-30秒",
                "2K": "20-60秒", 
                "4K": "30-90秒"
            }
            estimated = estimated_times.get(resolution, "未知")
            
            self.log(f"⏱️  预计生成时间: {estimated}")
            self.log(f"⏳ 发送API请求，最大超时时间: {timeout}秒")
            self.log("请耐心等待...")
            
            # 记录开始时间
            import time
            start_time = time.time()
            
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            # 计算实际用时
            elapsed_time = time.time() - start_time
            self.log(f"✅ API响应完成，实际用时: {elapsed_time:.1f}秒")
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"API请求失败，状态码: {response.status_code}"
                self.log(error_msg)
                try:
                    error_detail = response.json()
                    error_msg += f"\n错误详情: {json.dumps(error_detail, indent=2, ensure_ascii=False)}"
                except:
                    error_msg += f"\n响应内容: {response.text[:500]}"
                
                full_text = "## 错误\n" + error_msg + "\n\n## 日志\n" + "\n".join(self.log_messages)
                return (self.generate_empty_image(), full_text)
            
            self.log("API请求成功，正在解析响应...")
            
            # 解析响应
            result = response.json()
            
            # 提取图像数据
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    for part in parts:
                        if "inlineData" in part and "data" in part["inlineData"]:
                            img_base64 = part["inlineData"]["data"]
                            self.log("成功提取图像数据")
                            
                            # 转换为图像张量
                            img_tensor = self.base64_to_image(img_base64)
                            
                            if img_tensor is not None:
                                full_text = "## 生成成功\n" + "\n".join(self.log_messages)
                                return (img_tensor, full_text)
                            else:
                                error_msg = "图像数据转换失败"
                                self.log(error_msg)
                                full_text = "## 错误\n" + error_msg + "\n\n## 日志\n" + "\n".join(self.log_messages)
                                return (self.generate_empty_image(), full_text)
            
            # 如果没有找到图像数据
            error_msg = "API响应中未找到图像数据"
            self.log(error_msg)
            self.log(f"完整响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
            full_text = "## 错误\n" + error_msg + "\n\n## 日志\n" + "\n".join(self.log_messages)
            return (self.generate_empty_image(), full_text)
            
        except requests.Timeout:
            error_msg = f"请求超时（超过 {timeout} 秒）"
            self.log(error_msg)
            full_text = "## 错误\n" + error_msg + "\n\n## 建议\n尝试使用更低的分辨率（1K 或 2K）\n\n## 日志\n" + "\n".join(self.log_messages)
            return (self.generate_empty_image(), full_text)
        except Exception as e:
            error_msg = f"生成图像时出错: {str(e)}"
            self.log(error_msg)
            traceback.print_exc()
            full_text = "## 错误\n" + error_msg + "\n\n## 日志\n" + "\n".join(self.log_messages)
            return (self.generate_empty_image(), full_text)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "NanoBananaPro": NanoBananaProImageGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NanoBananaPro": "NanoBanana Pro Image Generator"
}
