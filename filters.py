from datetime import date
from typing import Optional
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field, NonNegativeInt

from database import MetalRoll


class RollsFilter(Filter):
    length__gte: Optional[NonNegativeInt] = Field(default=None,
                                                  alias='longer_than')
    length__lte: Optional[NonNegativeInt] = Field(default=None,
                                                  alias='shorter_than')
    weight__gte: Optional[NonNegativeInt] = Field(default=None,
                                                  alias='heavier_than')
    weight__lte: Optional[NonNegativeInt] = Field(default=None,
                                                  alias='lighter_than')
    loaded_at__gte: Optional[date] = Field(default=None,
                                           alias='loaded_after')
    loaded_at__lte: Optional[date] = Field(default=None,
                                           alias='loaded_before')
    unloaded_at__gte: Optional[date] = Field(default=None,
                                             alias='unloaded_after')
    unloaded_at__lte: Optional[date] = Field(default=None,
                                             alias='unloaded_before')
    # формат ввода даты нужно в будущем оптимизировать

    class Constants(Filter.Constants):
        model = MetalRoll

    class Config:
        populate_by_name = True
