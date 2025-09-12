from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from backend.models import (
    GiftItem,
    GiftStatus,
    Reservation,
    Rsvp,
    RsvpStatus,
    User,
    UserRole,
    WeddingList,
)
from backend.schemas import (
    GuestDetails,
    Message,
    ReservationPublic,
    RsvpPublic,
    WeddingListPublicGuest,
    WeddingListSummary,
)
from backend.security import get_current_user

router = APIRouter(prefix='/guest', tags=['guest'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/lists/{shareable_link}', response_model=WeddingListPublicGuest)
async def public_list(shareable_link: str, session: Session, user: CurrentUser):
    if user.role != UserRole.CONVIDADO:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Only CONVIDADO can view lists')
    wl = await session.scalar(
        select(WeddingList).where(WeddingList.shareable_link == shareable_link)
    )
    if not wl:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='List not found')
    # Map reservations by gift for this user
    res_rows = await session.scalars(
        select(Reservation).where(Reservation.gift_item_id.in_([g.id for g in wl.items]), Reservation.guest_id == user.id)
    )
    by_gift = {r.gift_item_id: r for r in res_rows.all()}
    # Mutate item dataclasses copy for serialization
    for gi in wl.items:
        setattr(gi, 'my_reservation_id', by_gift.get(gi.id).id if gi.id in by_gift else None)
    return wl


@router.post('/items/{item_id}/reserve', response_model=ReservationPublic, status_code=HTTPStatus.CREATED)
async def reserve_item(item_id: int, session: Session, user: CurrentUser):
    if user.role != UserRole.CONVIDADO:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Only CONVIDADO can reserve items')
    item = await session.scalar(select(GiftItem).where(GiftItem.id == item_id))
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Item not found')
    if item.status != GiftStatus.available:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Item not available')
    item.status = GiftStatus.reserved
    item.reserved_by_id = user.id
    reservation = Reservation(gift_item_id=item.id, guest_id=user.id)
    session.add(reservation)
    session.add(item)
    await session.commit()
    await session.refresh(reservation)
    return reservation


@router.delete('/reservations/{reservation_id}', response_model=Message)
async def cancel_reservation(reservation_id: int, session: Session, user: CurrentUser):
    reservation = await session.scalar(select(Reservation).where(Reservation.id == reservation_id))
    if not reservation:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Reservation not found')
    if reservation.guest_id != user.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not your reservation')
    item = await session.scalar(select(GiftItem).where(GiftItem.id == reservation.gift_item_id))
    if item:
        item.status = GiftStatus.available
        item.reserved_by_id = None
        session.add(item)
    await session.delete(reservation)
    await session.commit()
    return {'message': 'Reservation cancelled'}


@router.post('/lists/{list_id}/rsvp', response_model=RsvpPublic, status_code=HTTPStatus.CREATED)
async def send_rsvp(
    list_id: int,
    session: Session,
    user: CurrentUser,
    status: str | None = Query(None),
    payload: dict | None = Body(None),
):
    if user.role != UserRole.CONVIDADO:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Only CONVIDADO can RSVP')
    wl = await session.scalar(select(WeddingList).where(WeddingList.id == list_id))
    if not wl:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='List not found')
    status_value = (payload or {}).get('status') if payload else status
    additional_guests = (payload or {}).get('additional_guests') if payload else None
    if status_value not in [s.value for s in RsvpStatus]:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Invalid status')
    status = RsvpStatus(status_value)
    existing = await session.scalar(
        select(Rsvp).where(Rsvp.wedding_list_id == list_id, Rsvp.guest_id == user.id)
    )
    if existing:
        existing.status = status
        existing.additional_guests = additional_guests
        session.add(existing)
        await session.commit()
        await session.refresh(existing)
        return existing
    rsvp = Rsvp(wedding_list_id=list_id, guest_id=user.id, status=status, additional_guests=additional_guests)
    session.add(rsvp)
    await session.commit()
    await session.refresh(rsvp)
    return rsvp


@router.get('/me/details', response_model=GuestDetails)
async def my_details(session: Session, user: CurrentUser):
    if user.role != UserRole.CONVIDADO:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Only CONVIDADO can view guest details')
    rsvp_rows = await session.scalars(select(Rsvp).where(Rsvp.guest_id == user.id))
    rsvps_list = rsvp_rows.all()
    wl_ids = {r.wedding_list_id for r in rsvps_list}
    if wl_ids:
        wl_rows = await session.scalars(select(WeddingList).where(WeddingList.id.in_(wl_ids)))
        wl_map = {wl.id: wl for wl in wl_rows.all()}
    else:
        wl_map = {}
    events = []
    for r in rsvps_list:
        wl = wl_map.get(r.wedding_list_id)
        if not wl:
            continue
        events.append({'rsvp': r, 'wedding_list': wl})
    return {'user_id': user.id, 'events': events}
