from datetime import date
from typing import Optional

from pydantic import (
    BaseModel,
    PositiveInt,
    NonNegativeFloat,
    NonNegativeInt
)


class MetalRollPostSerializer(BaseModel):
    length: PositiveInt
    weight: PositiveInt


class MetalRollGetSerializer(MetalRollPostSerializer):
    id: NonNegativeInt
    loaded_at: date
    unloaded_at: Optional[date]

    class Config:
        from_attributes = True


class StatsSerializer(BaseModel):
    loaded_in: NonNegativeInt | None
    loaded_out: NonNegativeInt | None
    avg_length: NonNegativeFloat | None
    avg_weight: NonNegativeFloat | None
    max_length: NonNegativeInt | None
    max_weight: NonNegativeInt | None
    min_length: NonNegativeInt | None
    min_weight: NonNegativeInt | None
    summ_weight: NonNegativeInt | None
    max_storage_period: NonNegativeInt | None
    min_storage_period: NonNegativeInt | None
