# sensenova-imggen

商汤日日新 (SenseNova) 文生图模型插件，支持 11 种尺寸比例。

## 安装

```bash
hermes plugins install https://github.com/你的用户名/sensenova-imggen-plugin.git
```

## 启用

```bash
hermes plugins enable sensenova-imggen
```

## 配置

运行以下命令进入交互式配置界面：

```bash
hermes tools
```

选择 `image_gen` 工具，设置提供商为 `sensenova`，按提示输入 SenseNova API Key。

## 使用

在 Hermes 会话中调用图片生成工具：

```
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

## 管理

```bash
hermes plugins list        # 查看插件
hermes plugins disable sensenova-imggen   # 禁用插件
hermes plugins enable sensenova-imggen    # 启用插件
hermes plugins remove sensenova-imggen    # 卸载插件

hermes tools list          # 查看工具状态
hermes tools disable image_gen   # 禁用图片生成工具
hermes tools enable image_gen    # 启用图片生成工具
```

## 获取 API Key

https://platform.sensenova.cn/