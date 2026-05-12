# sensenova-imggen

商汤日日新 (SenseNova) 图片生成插件 for Hermes Agent

## 功能特性

- 支持 **SenseNova U1 Fast** 模型
- 支持 **11 种尺寸比例**: 16:9, 9:16, 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 21:9, 9:21
- 支持通过环境变量配置 API 凭据
- 支持官方 API 和本地 Proxy 两种模式

## 安装

```bash
hermes plugins install https://github.com/你的用户名/sensenova-imggen.git --enable
```

## 配置

### 1. 设置环境变量

```bash
# 必需
export SENSENOVA_API_KEY="your-api-key-here"

# 可选 - 使用本地 Proxy
export SENSENOVA_API_BASE_URL="http://127.0.0.1:8317/v1"
```

### 2. 在 config.yaml 中启用

```yaml
plugins:
  enabled:
    - sensenova-imggen

image_gen:
  provider: sensenova
  sensenova:
    model: sensenova-u1-fast
```

### 3. 重启 Hermes

```bash
exit
hermes
```

## 使用

```bash
# 生成宽屏图片 (16:9)
/image 生成一张信息图 --aspect 16:9

# 生成手机壁纸 (9:16)
/image 生成手机壁纸 --aspect portrait

# 生成正方形图标 (1:1)
/image 生成正方形图标 --aspect square

# 使用自定义比例
/image 生成海报 --aspect 2:3
```

## 支持的尺寸

| Aspect Ratio | 分辨率 | 别名 |
|-------------|--------|------|
| 16:9 | 2752×1536 | landscape (默认) |
| 9:16 | 1536×2752 | portrait |
| 1:1 | 2048×2048 | square |
| 2:3 | 1664×2496 | - |
| 3:2 | 2496×1664 | - |
| 3:4 | 1760×2368 | - |
| 4:3 | 2368×1760 | - |
| 4:5 | 1824×2272 | - |
| 5:4 | 2272×1824 | - |
| 21:9 | 3072×1376 | - |
| 9:21 | 1344×3136 | - |

## 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `SENSENOVA_API_KEY` | ✅ | - | 商汤 API Key |
| `SENSENOVA_API_BASE_URL` | ❌ | `https://token.sensenova.cn/v1` | API 基础 URL |

## 开发

```bash
# 本地开发
git clone https://github.com/你的用户名/sensenova-imggen.git
cd sensenova-imggen

# 测试安装
hermes plugins install . --enable
```

## 参考文档

- [商汤官方文档](https://platform.sensenova.cn/product/APIService/document/96)
- [Hermes 插件开发指南](https://hermes-agent.nousresearch.com/docs/developer-guide/image-gen-provider-plugin)

## 许可证

MIT License
