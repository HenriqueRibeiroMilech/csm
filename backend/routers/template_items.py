from http import HTTPStatus
import sys, asyncio
from typing import Annotated, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from backend.models import TemplateGiftItem, Category, User, UserRole
from backend.schemas import (
    TemplateGiftItemListResponse,
    TemplateGiftItemPublic,
    CategoryPublic,
)
from backend.security import get_current_user

router = APIRouter(prefix='/template-items', tags=['template-items'])

if sys.platform == 'win32':  # pragma: no cover
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:  # pragma: no cover
        pass

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('', response_model=TemplateGiftItemListResponse)
async def list_template_items(session: Session, user: CurrentUser):
    if user.role != UserRole.CASAL:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Only CASAL users can access template items')

    # Preload categories with joinedload to avoid MissingGreenlet due to lazy access
    stmt = select(TemplateGiftItem).options(joinedload(TemplateGiftItem.category))
    items = await session.scalars(stmt)
    grouped: Dict[int, List[TemplateGiftItem]] = {}
    category_map: Dict[int, Category] = {}
    for item in items.all():
        cid = item.category_id
        grouped.setdefault(cid, []).append(item)
        if cid not in category_map:
            category_map[cid] = item.category

    groups = []
    for cid, its in grouped.items():
        groups.append(
            {
                'category': category_map[cid],
                'items': its,
            }
        )

    # Sort groups by category name for consistency
    groups.sort(key=lambda g: g['category'].name.lower())
    return {'groups': groups}
