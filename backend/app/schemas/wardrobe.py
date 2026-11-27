
from pydantic import BaseModel, ConfigDict, Field


class WardrobeItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    category: str | None = Field(default=None, max_length=100)
    color: str | None = Field(default=None, max_length=50)
    image_reference: str | None = Field(default=None, max_length=500)
    user_id: int


class WardrobeItemResponse(BaseModel):
    id: int
    name: str
    category: str | None = None
    color: str | None = None
    image_reference: str | None = None
    user_id: int

    model_config = ConfigDict(from_attributes=True)
