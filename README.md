# SenseNova ImgGen Plugin

Hermes Agent 图片生成插件 - 商汤日日新 (SenseNova) U1 Fast 模型

## 特性

- ✅ 支持 11 种尺寸比例 (16:9, 9:16, 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 21:9, 9:21)
- ✅ 交互式配置 - 启用后首次使用提示输入 API Key
- ✅ 支持官方 API 和本地 Proxy 两种模式
- ✅ 自动下载图片并保存为本地文件

## 安装

### 方式 A: 从 GitHub 安装 (推荐)

```bash
hermes plugins install https://github.com/你的用户名/sensenova-imggen-plugin.git --enable
```

### 方式 B: 本地安装

```bash
hermes plugins install /path/to/sensenova-imggen-plugin --enable
```

## 配置

### 第一步: 启用插件

```bash
hermes plugins enable sensenova-imggen
```

### 第二步: 配置 API Key

**方式 1: 交互式配置 (推荐)**

启用插件后首次使用 `image_generate` 工具时，Hermes 会提示你输入 API Key。

**方式 2: 环境变量**

```bash
# 设置 API Key (必填)
export SENSENOVA_API_KEY="your-api-key"

# 可选: 使用本地 Proxy
export SENSENOVA_API_BASE_URL="http://127.0.0.1:8317/v1"
```

**方式 3: config.yaml**

```yaml
env_vars:
  SENSENOVA_API_KEY: "your-api-key"
  SENSENOVA_API_BASE_URL: "http://127.0.0.1:8317/v1"  # 可选
```

### 第三步: 选择 Provider

在 `config.yaml` 中配置:

```yaml
image_gen:
  provider: sensenova
```

## 使用

```bash
# 在 Hermes 交互会话中
/image 生成一张信息图 --aspect 16:9
/image 生成手机壁纸 --aspect portrait
/image 生成正方形图标 --aspect square
```

## 支持的尺寸

| Aspect Ratio | 分辨率 | 别名 |
|-------------|--------|------|
| 16:9 | 2752×1536 | landscape |
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

## 管理插件

```bash
# 查看插件列表
hermes plugins list

# 更新插件
hermes plugins update sensenova-imggen

# 禁用插件
hermes plugins disable sensenova-imggen

# 启用插件
hermes plugins enable sensenova-imggen

# 卸载插件
hermes plugins remove sensenova-imggen
```

## API 文档

- 商汤官方文档: https://platform.sensenova.cn/product/APIService/document/96
- Hermes 插件开发指南: https://hermes-agent.nousresearch.com/docs/developer-guide/image-gen-provider-plugin

## 许可证

MIT
