"""商汤日日新(SenseNova) 图片生成后端插件。

使用 SenseNova U1 Fast 模型，通过官方图片生成 API：
    POST https://token.sensenova.cn/v1/images/generations

配置方式：
    1. 启用插件后，首次使用会提示输入 API Key
    2. 或在终端设置环境变量: export SENSENOVA_API_KEY="your-api-key"

## 支持的尺寸 (11 种 aspect ratio)

| Aspect Ratio | 分辨率 (width x height) | 常用名称 |
|-------------|------------------------|---------|
| 2:3 | 1664×2496 | 竖版小图 |
| 3:2 | 2496×1664 | 横版小图 |
| 3:4 | 1760×2368 | 竖版中图 |
| 4:3 | 2368×1760 | 横版中图 |
| 4:5 | 1824×2272 | 竖版大图 |
| 5:4 | 2272×1824 | 横版大图 |
| 1:1 | 2048×2048 | 正方形 |
| 16:9 | 2752×1536 | 宽屏 (默认) |
| 9:16 | 1536×2752 | 竖屏 |
| 21:9 | 3072×1376 | 超宽屏 |
| 9:21 | 1344×3136 | 超长竖屏 |

## 使用示例

```
/image 生成一张信息图 --aspect 16:9
/image 生成手机壁纸 --aspect portrait
/image 生成正方形图标 --aspect square
```
"""

from __future__ import annotations

import base64
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from agent.image_gen_provider import (
    DEFAULT_ASPECT_RATIO,
    ImageGenProvider,
    error_response,
    resolve_aspect_ratio,
    save_b64_image,
    success_response,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 配置 (从环境变量读取)
# ---------------------------------------------------------------------------

# 默认使用官方 API
API_BASE_URL = os.environ.get("SENSENOVA_API_BASE_URL", "https://token.sensenova.cn/v1")


# ---------------------------------------------------------------------------
# 模型目录
# ---------------------------------------------------------------------------

_MODELS: Dict[str, Dict[str, Any]] = {
    "sensenova-u1-fast": {
        "display": "SenseNova U1 Fast",
        "speed": "~5-10s",
        "strengths": "信息图生成，快速迭代",
        "price": "按张计费",
    },
}

DEFAULT_MODEL = "sensenova-u1-fast"

# SenseNova U1 Fast 支持的尺寸映射 (11 种)
_SIZES = {
    # 默认尺寸 (16:9)
    "landscape": "2752x1536",    # 16:9
    "square": "2048x2048",       # 1:1
    "portrait": "1536x2752",     # 9:16
    
    # 额外支持的尺寸
    "2:3": "1664x2496",
    "3:2": "2496x1664",
    "3:4": "1760x2368",
    "4:3": "2368x1760",
    "4:5": "1824x2272",
    "5:4": "2272x1824",
    "21:9": "3072x1376",
    "9:21": "1344x3136",
}

# 尺寸别名映射 (方便用户输入)
_SIZE_ALIASES = {
    "16:9": "16:9",
    "9:16": "9:16",
    "1:1": "square",
    "2:3": "2:3",
    "3:2": "3:2",
    "3:4": "3:4",
    "4:3": "4:3",
    "4:5": "4:5",
    "5:4": "5:4",
    "21:9": "21:9",
    "9:21": "9:21",
    "landscape": "landscape",
    "portrait": "portrait",
    "square": "square",
}


def _resolve_model() -> Tuple[str, Dict[str, Any]]:
    """解析模型选择。"""
    return DEFAULT_MODEL, _MODELS[DEFAULT_MODEL]


def _resolve_size(aspect_ratio: str) -> str:
    """解析尺寸参数，支持多种输入格式。
    
    支持格式:
        - "landscape" / "square" / "portrait" (标准别名)
        - "16:9" / "9:16" / "1:1" 等比例字符串
        - 直接尺寸 "2752x1536"
    """
    # 直接返回 (已经是尺寸格式)
    if "x" in aspect_ratio:
        return aspect_ratio
    
    # 检查比例字符串
    if aspect_ratio in _SIZES:
        return _SIZES[aspect_ratio]
    
    # 检查别名
    if aspect_ratio in _SIZE_ALIASES:
        resolved = _SIZE_ALIASES[aspect_ratio]
        return _SIZES.get(resolved, _SIZES["landscape"])
    
    # 默认
    return _SIZES["landscape"]


# ---------------------------------------------------------------------------
# HTTP 请求工具
# ---------------------------------------------------------------------------

def _http_post(url: str, headers: Dict[str, str], body: Dict[str, Any]) -> Dict[str, Any]:
    """发送 POST 请求并返回 JSON 响应。"""
    data = json.dumps(body).encode("utf-8")
    req = Request(
        url,
        data=data,
        headers=headers,
        method="POST",
    )

    try:
        with urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        try:
            error_body = e.read().decode("utf-8")
            error_data = json.loads(error_body)
            error_msg = error_data.get("error", {}).get("message", str(e))
        except:
            error_msg = str(e)
        raise RuntimeError(f"HTTP {e.code}: {error_msg}")
    except URLError as exc:
        raise RuntimeError(f"HTTP request failed: {exc.reason}")
    except Exception as exc:
        raise RuntimeError(f"HTTP request failed: {exc}")


# ---------------------------------------------------------------------------
# Provider 实现
# ---------------------------------------------------------------------------


class SenseNovaImageGenProvider(ImageGenProvider):
    """商汤日日新(SenseNova) 图片生成后端 - SenseNova U1 Fast。
    
    支持 11 种尺寸比例:
        16:9, 9:16, 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 21:9, 9:21
    
    配置方式:
        1. 启用插件后首次使用会提示输入 API Key
        2. 或在终端设置: export SENSENOVA_API_KEY="your-api-key"
    """

    @property
    def name(self) -> str:
        return "sensenova"

    @property
    def display_name(self) -> str:
        return "SenseNova (商汤日日新)"

    def is_available(self) -> bool:
        """检查配置是否可用。
        
        如果 API Key 未设置，返回 False 并提示用户配置。
        """
        api_key = os.environ.get("SENSENOVA_API_KEY", "")
        return bool(api_key)

    def list_models(self) -> List[Dict[str, Any]]:
        """返回可用模型目录。"""
        return [
            {
                "id": model_id,
                "display": meta["display"],
                "speed": meta["speed"],
                "strengths": meta["strengths"],
                "price": meta["price"],
            }
            for model_id, meta in _MODELS.items()
        ]

    def default_model(self) -> Optional[str]:
        return DEFAULT_MODEL

    def get_setup_schema(self) -> Dict[str, Any]:
        """返回插件配置信息，用于交互式配置提示。
        
        Hermes 会显示此 schema 引导用户完成配置。
        """
        return {
            "name": "SenseNova (商汤日日新)",
            "badge": "community",
            "tag": "SenseNova U1 Fast - 11 种尺寸比例",
            "env_vars": [
                {"key": "SENSENOVA_API_KEY", "description": "SenseNova API Key"}
            ],
            "extra_info": {
                "supported_sizes": [
                    {"ratio": "16:9", "resolution": "2752×1536", "alias": "landscape"},
                    {"ratio": "9:16", "resolution": "1536×2752", "alias": "portrait"},
                    {"ratio": "1:1", "resolution": "2048×2048", "alias": "square"},
                    {"ratio": "2:3", "resolution": "1664×2496", "alias": None},
                    {"ratio": "3:2", "resolution": "2496×1664", "alias": None},
                    {"ratio": "3:4", "resolution": "1760×2368", "alias": None},
                    {"ratio": "4:3", "resolution": "2368×1760", "alias": None},
                    {"ratio": "4:5", "resolution": "1824×2272", "alias": None},
                    {"ratio": "5:4", "resolution": "2272×1824", "alias": None},
                    {"ratio": "21:9", "resolution": "3072×1376", "alias": None},
                    {"ratio": "9:21", "resolution": "1344×3136", "alias": None},
                ],
                "usage": "支持 --aspect 参数指定比例，如: /image prompt --aspect 16:9",
                "setup_instructions": [
                    "启用插件后首次使用会提示输入 API Key"
                ],
                "api_endpoint": "POST https://token.sensenova.cn/v1/images/generations",
            }
        }

    def generate(
        self,
        prompt: str,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """生成图片。

        SenseNova U1 Fast API:
            POST https://token.sensenova.cn/v1/images/generations

        请求格式:
        {
            "model": "sensenova-u1-fast",
            "prompt": "图像描述",
            "size": "2752x1536",
            "n": 1
        }

        响应格式:
        {
            "created": 1713167890,
            "data": [{"url": "..."}]
        }
        """
        # 检查 API Key 是否已设置
        api_key = os.environ.get("SENSENOVA_API_KEY", "")
        if not api_key:
            return error_response(
                error="SENSENOVA_API_KEY 环境变量未设置。请先配置 API Key 再使用。",
                error_type="config_required",
                provider="sensenova",
                aspect_ratio=aspect_ratio,
                extra={
                    "setup_instructions": [
                        "方式 1: 在终端设置环境变量",
                        '  export SENSENOVA_API_KEY="your-api-key"',
                        "",
                        "方式 2: 在 config.yaml 中添加",
                        "  env_vars:",
                        '    SENSENOVA_API_KEY: "your-api-key"',
                        "",
                        "获取 API Key: https://platform.sensenova.cn/",
                    ]
                },
            )

        prompt = (prompt or "").strip()
        aspect = resolve_aspect_ratio(aspect_ratio)

        if not prompt:
            return error_response(
                error="Prompt is required and must be a non-empty string",
                error_type="invalid_argument",
                provider="sensenova",
                aspect_ratio=aspect,
            )

        # 解析模型
        model_id, meta = _resolve_model()

        # 解析尺寸 (支持多种格式)
        size_str = _resolve_size(aspect)

        # 构建请求
        gen_url = f"{API_BASE_URL}/images/generations"

        gen_payload = {
            "model": model_id,
            "prompt": prompt,
            "size": size_str,
            "n": kwargs.get("n", 1),
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        logger.info(f"Generating image with SenseNova U1 Fast: size={size_str}")

        try:
            response = _http_post(gen_url, headers, gen_payload)
        except Exception as exc:
            return error_response(
                error=f"SenseNova API request failed: {exc}",
                error_type="api_error",
                provider="sensenova",
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect,
            )

        # 检查响应
        if "error" in response:
            return error_response(
                error=f"SenseNova API error: {response['error'].get('message', response['error'])}",
                error_type="api_error",
                provider="sensenova",
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect,
            )

        # 解析图片数据
        data = response.get("data", [])
        if not data:
            return error_response(
                error="No image data returned from SenseNova API",
                error_type="api_error",
                provider="sensenova",
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect,
            )

        # SenseNova 返回 URL，需要下载
        image_url = data[0].get("url")
        if not image_url:
            return error_response(
                error="Response contains no image URL",
                error_type="api_error",
                provider="sensenova",
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect,
            )

        # 下载图片
        try:
            image_data = _download_image(image_url)
            saved_path = save_b64_image(
                image_data,
                prefix=f"sensenova_{model_id}",
                extension="png",
            )
            image_ref = str(saved_path)
        except Exception as exc:
            return error_response(
                error=f"Failed to download image: {exc}",
                error_type="io_error",
                provider="sensenova",
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect,
            )

        extra: Dict[str, Any] = {"size": size_str, "image_url": image_url}
        if created := response.get("created"):
            extra["created"] = created

        return success_response(
            image=image_ref,
            model=model_id,
            prompt=prompt,
            aspect_ratio=aspect,
            provider="sensenova",
            extra=extra,
        )


def _download_image(url: str) -> str:
    """下载图片并返回 base64 编码。"""
    import urllib.request

    with urllib.request.urlopen(url, timeout=60) as response:
        image_data = response.read()
    return base64.b64encode(image_data).decode("utf-8")


# ---------------------------------------------------------------------------
# 插件入口点
# ---------------------------------------------------------------------------


def register(ctx) -> None:
    """插件入口点。"""
    ctx.register_image_gen_provider(SenseNovaImageGenProvider())
