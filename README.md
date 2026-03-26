# ComfyUI NanoBanana Pro Image Generator

针对 [Apiyi](https://api.apiyi.com/) 代理端点开发的 ComfyUI 自定义节点，通过 Gemini 3 系列图像模型实现文本生图和图生图功能。

基于 Google Gemini 3 Pro Image / Gemini 3.1 Flash Image 模型，通过 apiyi.com 代理 API 调用。

## 功能特点

- 文本生图（text-to-image）
- 图生图（image-to-image）— 支持单张或多张参考图像
- 多图像输入自动权重分配（基础图 / 主参考 / 次参考 / 辅助参考）
- 模型切换：Gemini 3.1 Flash（快速） / Gemini 3 Pro（高质）
- AI 思维推理（thinking）：none / minimal / high
- 14 种宽高比预设 + auto 自动匹配
- 3 档分辨率：1K / 2K / 4K
- API 密钥自动持久化（本地 `api_key.txt`，已加入 .gitignore）
- 实时进度条（基于 ComfyUI ProgressBar）
- Seed 控制：seed=0 每次随机生成，固定 seed 可复现
- 详细的日志输出和推理过程展示

## 安装

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/yitao2020/comfyui_Nano_banana_pro_apiyi.git
cd comfyui_Nano_banana_pro_apiyi
pip install -r requirements.txt
```

重启 ComfyUI，在节点列表的 **NanoBanana Pro** 分类下找到 `NanoBanana Pro Image Generator`。

## 使用方法

1. 添加节点到工作流
2. 在 `api_key` 字段填入你的 apiyi.com API 密钥（格式 `sk-...`），密钥会自动保存到本地
3. 输入提示词（支持中文 / 英文）
4. 选择模型、宽高比、分辨率、思维级别
5. （可选）连接参考图像
6. 运行

### 参数说明

| 参数 | 说明 |
|------|------|
| `api_key` | apiyi.com 的 API 密钥，`sk-` 格式 |
| `prompt` | 图像描述提示词 |
| `model` | `gemini-3.1-flash-image-preview`（快速便宜）/ `gemini-3-pro-image-preview`（高质量） |
| `aspect_ratio` | 宽高比：auto / 1:1 / 16:9 / 9:16 / 4:3 / 3:4 / 3:2 / 2:3 / 21:9 / 5:4 / 4:5 / 4:1 / 1:4 / 8:1 / 1:8 |
| `resolution` | 1K / 2K / 4K |
| `thinking_level` | `none`（无推理）/ `minimal`（快速推理）/ `high`（深度推理，适合复杂构图和精确文字） |
| `include_thoughts` | 是否在输出中展示 AI 的推理过程 |
| `seed` | 随机种子，设为 0 则每次生成不同结果 |
| `image`（可选） | 参考图像输入，支持 batch 多张 |

### 输出

- `image` — 生成的图像（IMAGE 类型）
- `info` — 生成日志和可选的 AI 推理过程（STRING 类型）

### 多图像权重说明

通过 Batch Images 节点输入多张图像时，自动按顺序分配角色：

| 顺序 | 角色 | 权重 |
|------|------|------|
| 第 1 张 | 基础图（要修改的目标图） | — |
| 第 2 张 | 主要风格参考 | 最高 |
| 第 3 张 | 次要参考 | 中等 |
| 第 4+ 张 | 辅助参考 | 最低 |

建议 2-3 张图像，太多可能导致效果混乱。详见 [MULTI_IMAGE_GUIDE.md](MULTI_IMAGE_GUIDE.md)。

### 预计生成时间

| 分辨率 | 预计时间 | 超时上限 |
|--------|----------|----------|
| 1K | 10-30 秒 | 180 秒 |
| 2K | 20-60 秒 | 300 秒 |
| 4K | 30-90 秒 | 360 秒 |

## API 密钥获取

前往 [apiyi.com](https://api.apiyi.com/) 注册并获取 API 密钥（`sk-` 格式）。

密钥保存在节点目录的 `api_key.txt` 中（已在 `.gitignore` 中排除，不会被提交）。

## 项目结构

```
comfyui_Nano_banana_pro_apiyi/
├── __init__.py                  # ComfyUI 节点注册入口
├── nanobanana_pro_node.py       # 核心节点逻辑
├── requirements.txt             # Python 依赖
├── .gitignore                   # 排除 api_key.txt 等
├── README.md                    # 本文件
├── MULTI_IMAGE_GUIDE.md         # 多图像输入详细指南
└── USAGE_EXAMPLE.md             # 使用示例和提示词技巧
```

## 迭代日志

### v2.0.0 — 当前版本

**新增功能：**
- 模型选择：支持 Gemini 3.1 Flash Image Preview 和 Gemini 3 Pro Image Preview 切换
- AI 思维推理（thinking）：none / minimal / high 三档，适用于复杂构图、精确文字渲染、多元素场景
- 推理过程输出：可选择在 info 输出中展示 AI 的完整思考链
- 实时进度条：使用 ComfyUI ProgressBar + 后台线程，生成过程中有实时进度反馈
- API URL 模板化：支持通过 `{model}` 占位符动态切换模型端点

**改进：**
- 宽高比扩展：新增 4:1 / 1:4 / 8:1 / 1:8 四种极端比例（全景图、长图等场景）
- Auto 宽高比匹配范围扩大：新增四种比例的标准值匹配
- 代码清理：移除了 `estimated_time` 冗余显示参数（信息已内置于进度条和日志）

**安全：**
- 添加 `.gitignore`，排除 `api_key.txt` 和其他敏感/缓存文件
- 确保 API 密钥不会出现在代码或版本控制历史中

### v1.1.0

- 多张图像输入支持
- 自动权重优先级（基础图 / 主参考 / 次参考 / 辅助参考）
- 详细的图像处理日志

### v1.0.0

- 初始版本
- 文本生图 + 图生图
- 10 种宽高比 + 3 档分辨率
- API 密钥自动保存

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 节点无法加载 | 安装依赖 `pip install -r requirements.txt`，重启 ComfyUI |
| API 请求失败 | 检查密钥格式（`sk-...`）、网络连接、apiyi.com 账户余额 |
| 生成空白图像 | 查看日志输出，确认 API 配额充足，尝试简化提示词 |
| 请求超时 | 降低分辨率（1K 或 2K），简化提示词，检查网络 |
| 模型切换后报错 | 确认 apiyi.com 代理端点支持目标模型 |

## 许可证

MIT License
