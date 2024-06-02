from datetime import date

from sqlalchemy import select, and_, or_, Integer
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from database import MetalRoll


class Queries:
    @classmethod
    async def add_roll(
        cls,
        data: dict,
        session: AsyncSession
    ) -> MetalRoll:
        roll = MetalRoll(**data)
        session.add(roll)
        await session.commit()
        return roll

    @classmethod
    async def list_rolls(
        cls,
        rolls_filter,
        session: AsyncSession
    ) -> list[MetalRoll]:
        query = select(MetalRoll).order_by(MetalRoll.loaded_at)
        if rolls_filter:
            query = rolls_filter.filter(query)
        execution = await session.execute(query)
        return execution.scalars().all()

    @classmethod
    async def patch_rolls(
        cls,
        id: int,
        session: AsyncSession
    ) -> MetalRoll:
        roll = await session.get(MetalRoll, id)
        if not roll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Объект с id "{id}" не найден'
            )
        if roll.unloaded_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Этот объект уже был отгружен'
            )
        roll.unloaded_at = date.today()
        await session.commit()
        return roll

    @classmethod
    async def get_stats(
        cls,
        from_date: date,
        to_date: date,
        session: AsyncSession
    ) -> dict:
        subq_load = select(func.count(MetalRoll.id))
        loaded_in = subq_load.filter(and_(
            from_date <= MetalRoll.loaded_at,
            MetalRoll.loaded_at <= to_date
        ))
        loaded_out = subq_load.filter(and_(
            from_date <= MetalRoll.unloaded_at,
            MetalRoll.unloaded_at <= to_date
        ))

        subq_active = select(MetalRoll).filter(and_(
            or_(
                MetalRoll.unloaded_at >= from_date,
                MetalRoll.unloaded_at is None
            ),
            MetalRoll.loaded_at <= to_date
            )).subquery('subq')

        length = select(
            func.avg(subq_active.c.length).cast(Integer),
            func.min(subq_active.c.length),
            func.max(subq_active.c.length)
        )

        weight = select(
            func.avg(subq_active.c.weight).cast(Integer),
            func.min(subq_active.c.weight),
            func.max(subq_active.c.weight)
        )

        summ_weight = select(
            func.sum(subq_active.c.weight)
        )

        lifespan = select(
            func.max(
                subq_active.c.unloaded_at - subq_active.c.loaded_at
            ),
            func.min(
                subq_active.c.unloaded_at - subq_active.c.loaded_at
            )
        )

        loaded_in = await session.execute(loaded_in)
        loaded_out = await session.execute(loaded_out)
        length = await session.execute(length)
        weight = await session.execute(weight)
        summ_weight = await session.execute(summ_weight)
        lifespan = await session.execute(lifespan)

        result = {}
        result['loaded_in'] = loaded_in.scalar_one()
        result['loaded_out'] = loaded_out.scalar_one()
        result['avg_length'], \
            result['min_length'], \
            result['max_length'] = length.first()
        result['avg_weight'], \
            result['min_weight'], \
            result['max_weight'] = weight.first()
        result['summ_weight'] = summ_weight.scalar_one()
        result['max_storage_period'], \
            result['min_storage_period'] = (
                td.days if td else None for td in lifespan.first()
            )
        return result
