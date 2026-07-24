# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file images.py
@brief 执行仅供内部图片端点使用的封面二进制查询。
"""

from sqlalchemy import Select, bindparam, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.data.queries.common import SUBJECTS
from backend.data.rows import CoverImageRow


async def get_cover_image(session: AsyncSession, bgm_id: int) -> CoverImageRow | None:
    """
    @brief 按公开条目 ID 读取封面二进制内容。
    @details 本查询不参与普通 JSON 条目投影，仅供内部图片端点调用。
    @param session 当前请求的只读数据库会话。
    @param bgm_id Bangumi 公开条目 ID。
    @return 条目存在时返回封面二进制行模型，不存在时返回 None。
    """
    result = await session.execute(_build_cover_image_statement(), {'bgm_id': bgm_id})
    record = result.mappings().one_or_none()

    if record is None:
        return None

    cover_image = record['cover_image']

    if cover_image is not None and not isinstance(cover_image, bytes):
        raise TypeError('封面二进制字段必须是 bytes 或 None')

    return CoverImageRow(cover_image=cover_image)


def _build_cover_image_statement() -> Select[tuple[bytes | None]]:
    return select(SUBJECTS.c.cover_image).where(SUBJECTS.c.bgm_id == bindparam('bgm_id'))

if __name__ == '__main__':
    pass
