# NanoBanana Pro 使用示例

## 示例 1：纯文本生成图像（文生图）

最简单的使用方式，只需要提示词：

```
节点配置：
- API Key: sk-your-api-key
- Prompt: 一只可爱的小猫坐在花园里，油画风格，高清，细节丰富
- Model: gemini-3.1-flash-image-preview
- Aspect Ratio: 16:9
- Resolution: 2K
- Thinking Level: none
- Seed: 0
- Image: (不连接)
```

> `Seed: 0` 表示每次生成不同结果。固定为一个数字可复现相同图像。

## 示例 2：使用参考图像（图生图）

基于某张图像生成新图像：

```
工作流：
LoadImage -> NanoBanana Pro Image Generator -> SaveImage

节点配置：
- API Key: sk-your-api-key
- Prompt: 将这张图片转换为水彩画风格，保持主体不变
- Model: gemini-3.1-flash-image-preview
- Aspect Ratio: 1:1
- Resolution: 2K
- Image: (连接 LoadImage 的输出)
```

## 示例 3：深度推理模式（精确文字/复杂构图）

需要精确文字渲染或复杂构图时，使用 thinking 模式：

```
节点配置：
- Prompt: 一张海报，标题写着 "Hello World"，背景是星空，赛博朋克字体
- Model: gemini-3-pro-image-preview
- Thinking Level: high
- Include Thoughts: true
- Aspect Ratio: 9:16
- Resolution: 2K

说明：
- high thinking level 适合需要精确文字或多元素的场景
- 开启 include_thoughts 可以在 info 输出中查看 AI 的推理过程
- 复杂任务建议使用 Pro 模型
```

## 示例 4：高分辨率生成

需要高质量图像时：

```
节点配置：
- Prompt: 未来城市景观，赛博朋克风格，霓虹灯，夜景，超高清
- Model: gemini-3-pro-image-preview
- Aspect Ratio: 21:9
- Resolution: 4K

注意：4K 分辨率生成时间较长（30-90秒），进度条会实时显示进度
```

## 示例 5：竖屏图像（手机壁纸/海报）

适合手机壁纸或海报：

```
节点配置：
- Prompt: 梦幻森林，阳光透过树叶，唯美，竖版构图
- Model: gemini-3.1-flash-image-preview
- Aspect Ratio: 9:16
- Resolution: 2K
```

## 示例 6：全景图/长图（v2.0.0 新增）

利用 v2.0.0 新增的极端宽高比：

```
# 全景横图
- Aspect Ratio: 8:1
- Prompt: 连绵的山水画卷，水墨画风格
- Resolution: 2K

# 竖版长图（适合信息图或手机长壁纸）
- Aspect Ratio: 1:4
- Prompt: 梦幻森林小径，阳光透过树叶，童话风格
- Resolution: 2K

# 超宽电影感
- Aspect Ratio: 4:1
- Prompt: 赛博朋克城市天际线，霓虹灯海
- Resolution: 4K

# 超长竖图（适合信息流内容）
- Aspect Ratio: 1:8
- Prompt: 一棵巨大的古树，从根部到树冠，细节丰富
- Resolution: 2K
```

## 示例 7：多图像风格迁移

```
工作流：
LoadImage (原始照片) ──┐
LoadImage (油画风格) ──┼─→ Batch Images → NanoBanana Pro → SaveImage

节点配置：
- Prompt: 将第一张照片转换为第二张图片的油画风格
- Model: gemini-3-pro-image-preview
- Thinking Level: minimal
- Aspect Ratio: auto（自动匹配第一张图比例）
```

## 模型选择指南

| 场景 | 推荐模型 | 推荐配置 |
|------|----------|----------|
| 日常生图 / 快速预览 | Flash | none thinking, 1K/2K |
| 风格迁移 / 图生图 | Flash | minimal thinking, 2K |
| 精确文字渲染 | Pro | high thinking, 2K |
| 复杂多元素构图 | Pro | high thinking, 2K |
| 高质量最终输出 | Pro | minimal thinking, 4K |
| 全景图 / 长图 | Flash | none thinking, 2K |

## 思维推理（Thinking）使用指南

### none — 无推理（默认）
适合简单提示词、快速生成、日常使用。
```
Prompt: 一只猫坐在窗台上
Thinking: none
```

### minimal — 快速推理
适合需要一定理解但不需要深度思考的场景，如风格迁移、图生图。
```
Prompt: 保持人物特征，转换为水彩画风格
Thinking: minimal
Image: (连接参考图)
```

### high — 深度推理
适合复杂场景：精确文字、多元素协调、复杂构图、专业级输出。
```
Prompt: 一张电影海报，标题 "星际迷航"，包含飞船、星球、星云，科幻字体
Thinking: high
Include Thoughts: true
```

## 提示词技巧

### 好的提示词示例：

1. **详细描述**
   ```
   一只橘色的小猫，坐在木质窗台上，阳光从窗户照进来，
   背景是模糊的花园，油画风格，暖色调，高清细节
   ```

2. **风格指定**
   ```
   赛博朋克城市街道，霓虹灯招牌，雨后湿润的地面，
   未来感，电影级画质，超现实主义
   ```

3. **情绪氛围**
   ```
   宁静的湖边小屋，日落时分，金色的光线，
   温馨氛围，治愈系，水彩画风格
   ```

4. **精确文字渲染（需 high thinking）**
   ```
   一张唱片封面，中央用金色艺术字体写着 "Dreamscape"，
   背景是渐变的紫色和蓝色星空
   ```

### 提示词要素：

- **主体**：描述主要对象
- **环境**：背景和场景
- **风格**：艺术风格或画风
- **光线**：光照效果
- **质量**：高清、细节等
- **情绪**：想要表达的感觉
- **文字**：如需文字，明确写出内容（配合 high thinking）

## 常见问题

**Q: 生成速度慢怎么办？**
A: 选择较低的分辨率（1K 或 2K），使用 Flash 模型代替 Pro 模型，thinking 设为 none。

**Q: 如何获得更好的效果？**
A:
1. 使用详细的提示词
2. 指定艺术风格
3. 提供参考图像
4. 复杂场景使用 high thinking level
5. 使用 2K 或 4K 分辨率

**Q: Flash 和 Pro 模型怎么选？**
A: Flash 更快更便宜，适合日常使用和快速预览。Pro 质量更高，适合最终输出和复杂任务。

**Q: 什么是思维推理（thinking）？**
A: AI 在生成前先"思考"一下，有助于处理复杂构图、精确文字渲染、多元素协调。越高的级别思考越深但耗时也越长。

**Q: 可以生成什么比例的图像？**
A: 支持 14 种比例：
- 方形：1:1
- 横屏：16:9, 4:3, 3:2, 21:9, 5:4
- 竖屏：9:16, 3:4, 2:3, 4:5
- 极端比例（v2.0.0 新增）：4:1, 1:4, 8:1, 1:8
- 自动匹配：auto

**Q: API 密钥保存在哪里？**
A: 保存在节点目录的 `api_key.txt` 文件中，可以手动编辑。此文件已被 .gitignore 排除。

## 工作流示例

### 基础文生图工作流
```
NanoBanana Pro Image Generator -> SaveImage
```

### 图生图工作流
```
LoadImage -> NanoBanana Pro Image Generator -> SaveImage
```

### 多图风格迁移工作流
```
LoadImage (原图) ──┐
LoadImage (风格) ──┼─→ Batch Images -> NanoBanana Pro -> SaveImage
```

### 高质量输出工作流
```
NanoBanana Pro (Pro, 4K, minimal thinking) -> SaveImage
```

### 后处理工作流
```
NanoBanana Pro Image Generator -> Upscale -> SaveImage
```

## 性能建议

1. **快速预览**：1K + Flash + none thinking
2. **日常使用**：2K + Flash + none thinking（推荐）
3. **风格迁移**：2K + Flash + minimal thinking
4. **复杂场景**：2K + Pro + high thinking
5. **最终输出**：4K + Pro + minimal/high thinking
