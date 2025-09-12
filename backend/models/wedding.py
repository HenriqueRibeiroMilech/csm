from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import GiftStatus, RsvpStatus, table_registry

if TYPE_CHECKING:  # pragma: no cover
    from .user import User


@table_registry.mapped_as_dataclass
class WeddingList:
    __tablename__ = 'wedding_lists'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    message: Mapped[str | None]
    event_date: Mapped[date | None]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    shareable_link: Mapped[str] = mapped_column(unique=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    owner: Mapped['User'] = relationship(
        init=False, back_populates='wedding_lists'
    )

    # default/optional fields must come after non-default ones for dataclasses
    delivery_info: Mapped[str | None] = mapped_column(default=None)

    items: Mapped[list['GiftItem']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
        back_populates='wedding_list',
    )
    rsvps: Mapped[list['Rsvp']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
        back_populates='wedding_list',
    )


@table_registry.mapped_as_dataclass
class GiftItem:
    __tablename__ = 'gift_items'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]
    wedding_list_id: Mapped[int] = mapped_column(
        ForeignKey('wedding_lists.id')
    )
    wedding_list: Mapped['WeddingList'] = relationship(
        init=False, back_populates='items'
    )
    status: Mapped[GiftStatus] = mapped_column(default=GiftStatus.available)

    reserved_by_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id'), default=None
    )
    reserved_by: Mapped['User | None'] = relationship(init=False)


@table_registry.mapped_as_dataclass
class Rsvp:
    __tablename__ = 'rsvps'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    wedding_list_id: Mapped[int] = mapped_column(
        ForeignKey('wedding_lists.id')
    )
    guest_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    status: Mapped[RsvpStatus] = mapped_column(default=RsvpStatus.pending)
    additional_guests: Mapped[str | None] = mapped_column(default=None)

    wedding_list: Mapped['WeddingList'] = relationship(
        init=False, back_populates='rsvps'
    )
    guest: Mapped['User'] = relationship(init=False, back_populates='rsvps')


@table_registry.mapped_as_dataclass
class Reservation:
    __tablename__ = 'reservations'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    gift_item_id: Mapped[int] = mapped_column(ForeignKey('gift_items.id'))
    guest_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    # Relationships (not strictly needed right now for queries, kept simple)


@table_registry.mapped_as_dataclass
class Category:
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    template_items: Mapped[list['TemplateGiftItem']] = relationship(
        init=False, cascade='all, delete-orphan', back_populates='category', lazy='selectin'
    )


@table_registry.mapped_as_dataclass
class TemplateGiftItem:
    __tablename__ = 'template_gift_items'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    category: Mapped['Category'] = relationship(init=False, back_populates='template_items')
