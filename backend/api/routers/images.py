# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file images.py
@brief 提供内部封面二进制资源端点。
@details 本路由不属于 /api 下的 JSON REST 端点。它仅接受已校验的公开条目 ID，
         从数据库读取封面二进制内容并在识别安全图片格式后原样返回。
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import provide_database_session
from backend.data.queries.images import get_cover_image

router = APIRouter(tags=['images'])

IMAGE_RESPONSE_HEADERS = {
    'Cache-Control': 'public, max-age=3600',
    'X-Content-Type-Options': 'nosniff',
}


@router.get('/images/{bgm_id}', response_class=Response)
async def get_image(
    session: Annotated[AsyncSession, Depends(provide_database_session)],
    bgm_id: Annotated[int, Path(gt=0, description='正整数 Bangumi 条目 ID')],
) -> Response:
    """
    @brief 返回指定条目的已识别封面二进制内容。
    @details 条目不存在、封面为空或二进制格式未知时统一返回无响应体的 404，避免
             JSON 错误细节或未知二进制内容泄露给图片加载请求。
    @param session 当前请求的只读数据库会话。
    @param bgm_id Bangumi 公开条目 ID。
    @return 识别出的图片二进制响应，或无响应体的 404。
    """
    cover_image_row = await get_cover_image(session=session, bgm_id=bgm_id)

    if cover_image_row is None or cover_image_row.cover_image is None:
        return Response(status_code=404)

    media_type = _detect_image_media_type(cover_image_row.cover_image)

    if media_type is None:
        return Response(status_code=404)

    return Response(
        content=cover_image_row.cover_image,
        headers=IMAGE_RESPONSE_HEADERS,
        media_type=media_type,
    )


def _detect_image_media_type(content: bytes) -> str | None:
    """
    @brief 根据安全文件签名识别允许返回的图片媒体类型。
    @param content 数据库中读取的封面二进制内容。
    @return 已识别的 JPEG、PNG、WebP 或 GIF 媒体类型；无法识别时返回 None。
    """
    if content.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'

    if content.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'

    if content.startswith((b'GIF87a', b'GIF89a')):
        return 'image/gif'

    if len(content) >= 12 and content.startswith(b'RIFF') and content[8:12] == b'WEBP':
        return 'image/webp'

    return None


if __name__ == '__main__':
    pass

