from datetime import date
from sys import stdout

from fastapi import (
    FastAPI,
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request
)
from fastapi.responses import JSONResponse
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import (
    MetalRollGetSerializer,
    MetalRollPostSerializer,
    StatsSerializer
)
from filters import RollsFilter
from queries import Queries as Q
from database import get_async_session, DB_Error

app = FastAPI(title='Metal rolls')

router = APIRouter(
    prefix='/metalrolls',
    tags=['metalrolls']
)


@router.post('')
async def post_roll(
    data: MetalRollPostSerializer,
    session: AsyncSession = Depends(get_async_session)
) -> MetalRollGetSerializer:
    validated_data = data.model_dump()
    roll = await Q.add_roll(validated_data, session)
    response = MetalRollGetSerializer.model_validate(roll)
    return response


@router.get('')
async def get_rolls(
    filter: RollsFilter = FilterDepends(RollsFilter),
    session: AsyncSession = Depends(get_async_session)
) -> list[MetalRollGetSerializer]:
    rolls = await Q.list_rolls(filter, session)
    response = [
        MetalRollGetSerializer.model_validate(item)
        for item in rolls
    ]
    return response


@router.patch('/{id}')
async def ship_rolls(
    id: int,
    session: AsyncSession = Depends(get_async_session)
) -> MetalRollGetSerializer:
    roll = await Q.patch_rolls(id, session)
    response = MetalRollGetSerializer.model_validate(roll)
    return response


@router.get('/stats')
async def show_stats(
    from_date: date,
    to_date: date,
    session: AsyncSession = Depends(get_async_session)
) -> StatsSerializer:
    validate_time_range(from_date, to_date)
    stats = await Q.get_stats(from_date, to_date, session)
    response = StatsSerializer.model_validate(stats)
    return response


def validate_time_range(from_date: date,
                        to_date: date):
    today = date.today()
    if from_date > to_date or from_date > today or to_date > today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверно указана дата'
        )


@app.exception_handler(DB_Error)
async def db_exception_handler(request: Request, exc: DB_Error):
    stdout.write(f'Ошибка подключения к базе данных: {exc.args}\n')
    # Потом можно переделать в логгирование
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content='Ошибка подключения к базе данных'
    )

app.include_router(router)
