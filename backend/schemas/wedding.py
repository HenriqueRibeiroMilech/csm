from datetime import date

from pydantic import BaseModel, ConfigDict

from backend.models import GiftStatus, RsvpStatus


class WeddingListCreate(BaseModel):
    title: str
    message: str | None = None
    event_date: date | None = None
    delivery_info: str | None = None


class WeddingListUpdate(BaseModel):
    title: str | None = None
    message: str | None = None
    event_date: date | None = None
    delivery_info: str | None = None


class GiftItemCreate(BaseModel):
    name: str
    description: str | None = None


class GiftItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: GiftStatus | None = None


class GiftItemPublic(BaseModel):
    id: int
    name: str
    description: str | None
    status: GiftStatus
    reserved_by_id: int | None
    my_reservation_id: int | None = None
    model_config = ConfigDict(from_attributes=True)


class WeddingListPublic(BaseModel):
    id: int
    title: str
    message: str | None
    event_date: date | None
    delivery_info: str | None = None
    items: list[GiftItemPublic] = []
    shareable_link: str | None = None
    model_config = ConfigDict(from_attributes=True)


class WeddingListPublicGuest(WeddingListPublic):
    pass


class WeddingListList(BaseModel):
    lists: list[WeddingListPublic]


class WeddingListSummary(BaseModel):
    id: int
    title: str
    shareable_link: str | None = None
    model_config = ConfigDict(from_attributes=True)


class RsvpPublic(BaseModel):
    id: int
    guest_id: int
    guest_name: str | None = None
    status: RsvpStatus
    additional_guests: str | None = None
    model_config = ConfigDict(from_attributes=True)


class TrackingEntry(BaseModel):
    gift: GiftItemPublic
    reserved_by_id: int | None
    reserved_by_name: str | None = None


class TrackingResponse(BaseModel):
    list_id: int
    gifts: list[TrackingEntry]
    rsvps: list[RsvpPublic]


class ReservationPublic(BaseModel):
    id: int
    gift_item_id: int
    guest_id: int
    gift_name: str | None = None
    model_config = ConfigDict(from_attributes=True)


class GuestEventRsvp(BaseModel):
    rsvp: RsvpPublic
    wedding_list: WeddingListSummary


class GuestDetails(BaseModel):
    user_id: int
    events: list[GuestEventRsvp]


class CategoryPublic(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class TemplateGiftItemPublic(BaseModel):
    id: int
    name: str
    description: str | None
    category: CategoryPublic
    model_config = ConfigDict(from_attributes=True)


class TemplateGiftItemsGrouped(BaseModel):
    category: CategoryPublic
    items: list[TemplateGiftItemPublic]


class TemplateGiftItemListResponse(BaseModel):
    groups: list[TemplateGiftItemsGrouped]
