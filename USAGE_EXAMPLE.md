# NanoBanana Pro 使用示例

## 示例 1：纯文本生成图像

最简单的使用方式，只需要提示词：

```
节点配置：
- API Key: sk-your-api-key
- Prompt: 一只可爱的小猫坐在花园里，油画风格，高清，细节丰富
- Aspect Ratio: 16:9
- Resolution: 2K
- Image: (不连接)
```

## 示例 2：使用参考图像

如果你想基于某张图像生成新图像：

```
工作流：
LoadImage -> NanoBanana Pro Image Generator -> SaveImage

节点配置：
- API Key: sk-your-api-key
- Prompt: 将这张图片转换为水彩画风格，保持主体不变
- Aspect Ratio: 1:1
- Resolution: 2K
- Image: (连接 LoadImage 的输出)
```

## 示例 3：高分辨率生成

需要高质量图像时：

```
节点配置：
- API Key: sk-your-api-key
- Prompt: 未来城市景观，赛博朋克风格，霓虹灯，夜景，超高清
- Aspect Ratio: 21:9
- Resolution: 4K
- Image: (不连接)

注意：4K 分辨率生成时间较长（30-90秒），请耐心等待
```

## 示例 4：竖屏图像生成

适合手机壁纸或海报：

```
节点配置：
- API Key: sk-your-api-key
- Prompt: 梦幻森林，阳光透过树叶，唯美，竖版构图
- Aspect Ratio: 9:16
- Resolution: 2K
- Image: (不连接)
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
   未来感，电影级画质，8K，超现实主义
   ```

3. **情绪氛围**
   ```
   宁静的湖边小屋，日落时分，金色的光线，
   温馨氛围，治愈系，水彩画风格
   ```

### 提示词要素：

- 主体：描述主要对象
- 环境：背景和场景
- 风格：艺术风格或画风
- 光线：光照效果
- 质量：高清、细节等
- 情绪：想要表达的感觉

## 常见问题

**Q: 生成速度慢怎么办？**
A: 选择较低的分辨率（1K 或 2K），4K 需要更长时间。

**Q: 如何获得更好的效果？**
A: 
1. 使用详细的提示词
2. 指定艺术风格
3. 提供参考图像
4. 使用 2K 或 4K 分辨率

**Q: 可以生成什么比例的图像？**
A: 支持 10 种比例：
- 方形：1:1
- 横屏：16:9, 4:3, 3:2, 21:9, 5:4
- 竖屏：9:16, 3:4, 2:3, 4:5

**Q: API 密钥保存在哪里？**
A: 保存在节点目录的 `api_key.txt` 文件中，可以手动编辑。

## 工作流示例

### 基础文生图工作流
```
NanoBanana Pro Image Generator -> SaveImage
```

### 图生图工作流
```
LoadImage -> NanoBanana Pro Image Generator -> SaveImage
```

### 批量生成工作流
```
TextInput (多个) -> NanoBanana Pro Image Generator -> SaveImage
```

### 后处理工作流
```
NanoBanana Pro Image Generator -> Upscale -> SaveImage
```

## 性能建议

1. **快速预览**：使用 1K 分辨率
2. **日常使用**：使用 2K 分辨率（推荐）
3. **最终输出**：使用 4K 分辨率

## 更新日志

### v1.0.0
- 初始版本
- 支持文本生图
- 支持图生图
- 支持自定义宽高比和分辨率
- API 密钥自动保存
