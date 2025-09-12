from http import HTTPStatus
from typing import Annotated
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from backend.models import (
    GiftItem,
    User,
    UserRole,
    WeddingList,
    Rsvp,
)
from backend.schemas import (
    GiftItemCreate,
    GiftItemPublic,
    GiftItemUpdate,
    Message,
    TrackingResponse,
    WeddingListCreate,
    WeddingListList,
    WeddingListPublic,
    WeddingListUpdate,
)
from backend.security import get_current_user

router = APIRouter(prefix='/lists', tags=['lists'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def _ensure_casal(user: User):
    if user.role != UserRole.CASAL:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Only CASAL users can manage lists',
        )


def _ensure_owner(user: User, wedding_list: WeddingList):
    if wedding_list.owner_id != user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )


@router.post(
    '/', response_model=WeddingListPublic, status_code=HTTPStatus.CREATED
)
async def create_wedding_list(
    data: WeddingListCreate, session: Session, user: CurrentUser
):
    _ensure_casal(user)
    # short random shareable link (16 hex chars)
    shareable_link = secrets.token_urlsafe(8)
    wl = WeddingList(
        title=data.title,
        message=data.message,
        event_date=data.event_date,
    delivery_info=data.delivery_info,
        owner_id=user.id,
        shareable_link=shareable_link,
    )
    session.add(wl)
    await session.commit()
    await session.refresh(wl)
    return wl


@router.get('/my-lists', response_model=WeddingListList)
async def get_my_lists(session: Session, user: CurrentUser):
    _ensure_casal(user)
    lists = await session.scalars(
        select(WeddingList).where(WeddingList.owner_id == user.id)
    )
    return {'lists': lists.all()}


@router.put('/{list_id}', response_model=WeddingListPublic)
async def update_list(
    list_id: int, data: WeddingListUpdate, session: Session, user: CurrentUser
):
    _ensure_casal(user)
    wl = await session.scalar(
        select(WeddingList).where(
            WeddingList.id == list_id, WeddingList.owner_id == user.id
        )
    )
    if not wl:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='List not found'
        )

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(wl, key, value)

    session.add(wl)
    await session.commit()
    await session.refresh(wl)
    return wl


@router.post('/{list_id}/generate-link', response_model=WeddingListPublic)
async def generate_shareable_link(list_id: int, session: Session, user: CurrentUser):
    """Generate (or rotate) a shareable link for a wedding list the couple owns.

    This helps populate links for older lists created before the field existed
    or to rotate a compromised link.
    """
    _ensure_casal(user)
    wl = await session.scalar(
        select(WeddingList).where(
            WeddingList.id == list_id, WeddingList.owner_id == user.id
        )
    )
    if not wl:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='List not found')
    # Always rotate (cheap + allows regeneration if leaked)
    wl.shareable_link = secrets.token_urlsafe(8)
    session.add(wl)
    await session.commit()
    await session.refresh(wl)
    return wl


@router.delete('/{list_id}', response_model=Message)
async def delete_list(list_id: int, session: Session, user: CurrentUser):
    _ensure_casal(user)
    wl = await session.scalar(
        select(WeddingList).where(
            WeddingList.id == list_id, WeddingList.owner_id == user.id
        )
    )
    if not wl:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='List not found'
        )
    await session.delete(wl)
    await session.commit()
    return {'message': 'List deleted'}


# Gift items endpoints
@router.post(
    '/{list_id}/items',
    response_model=GiftItemPublic,
    status_code=HTTPStatus.CREATED,
)
async def create_gift_item(
    list_id: int, data: GiftItemCreate, session: Session, user: CurrentUser
):
    wl = await session.scalar(
        select(WeddingList).where(
            WeddingList.id == list_id, WeddingList.owner_id == user.id
        )
    )
    if not wl:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='List not found'
        )
    item = GiftItem(
        name=data.name,
        description=data.description,
        wedding_list_id=wl.id,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.put('/{list_id}/items/{item_id}', response_model=GiftItemPublic)
async def update_gift_item(
    list_id: int,
    item_id: int,
    data: GiftItemUpdate,
    session: Session,
    user: CurrentUser,
):
    wl = await session.scalar(
        select(WeddingList).where(
            WeddingList.id == list_id, WeddingList.owner_id == user.id
        )
    )
    if not wl:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='List not found'
        )
    item = await session.scalar(
        select(GiftItem).where(
            GiftItem.id == item_id, GiftItem.wedding_list_id == wl.id
        )
    )
    if not item:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Item not found'
        )
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.delete('/{list_id}/items/{item_id}', response_model=Message)
async def delete_gift_item(
    list_id: int, item_id: int, session: Session, user: CurrentUser
):
    wl = await session.scalar(
        select(WeddingList).where(
            WeddingList.id == list_id, WeddingList.owner_id == user.id
        )
    )
    if not wl:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='List not found'
        )
    item = await session.scalar(
        select(GiftItem).where(
            GiftItem.id == item_id, GiftItem.wedding_list_id == wl.id
        )
    )
    if not item:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Item not found'
        )
    await session.delete(item)
    await session.commit()
    return {'message': 'Item deleted'}


@router.get('/{list_id}/tracking', response_model=TrackingResponse)
async def tracking(list_id: int, session: Session, user: CurrentUser):
    # Load list with items (and reserved_by) + rsvps (and guest)
    wl = await session.scalar(
        select(WeddingList)
        .options(
            selectinload(WeddingList.items).selectinload(GiftItem.reserved_by),
            selectinload(WeddingList.rsvps).selectinload(Rsvp.guest),
        )
        .where(WeddingList.id == list_id, WeddingList.owner_id == user.id)
    )
    if not wl:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='List not found'
        )

    gifts = []
    for gi in wl.items:
        if gi.reserved_by_id:  # only show reserved gifts
            gifts.append(
                {
                    'gift': gi,
                    'reserved_by_id': gi.reserved_by_id,
                    'reserved_by_name': getattr(gi.reserved_by, 'username', None),
                }
            )

    rsvps = []
    for r in wl.rsvps:
        base = {
            'id': r.id,
            'guest_id': r.guest_id,
            'guest_name': getattr(r.guest, 'username', None),
            'status': r.status,
            'additional_guests': r.additional_guests,
        }
        rsvps.append(base)
        # expand companions
        if r.additional_guests:
            for idx, name in enumerate(
                [n.strip() for n in r.additional_guests.split(',') if n.strip()]
            ):
                rsvps.append(
                    {
                        'id': int(f"{r.id}000{idx}"),  # synthetic id
                        'guest_id': r.guest_id,
                        'guest_name': name,
                        'status': r.status,
                        'additional_guests': None,
                    }
                )

    return {
        'list_id': wl.id,
        'gifts': gifts,
        'rsvps': rsvps,
    }
