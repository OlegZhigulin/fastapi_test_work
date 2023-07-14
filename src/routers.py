from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, status, HTTPException
import asyncpg

from src.dependences import get_connection
from src.schemas import (DatabaseEntityModel,
                         DatabaseEntityResponseModel,
                         DatabaseListEntitiesResponseModel
                         )


api_router_v1 = APIRouter(
    tags=['api'],
    prefix='/api/v1'
)


@api_router_v1.get('/{entity_id}',
                   summary='Получение одной записи',
                   description='Получение одной записи по id',
                   status_code=status.HTTP_200_OK,
                   response_model=DatabaseEntityResponseModel,
                   )
async def read_item(entity_id: int,
                    connection=Depends(get_connection)
                    ) -> dict:
    sql_raw_query = """SELECT * FROM items WHERE id = $1"""
    response = await connection.fetchrow(sql_raw_query, entity_id)
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Запись не найдена',
        )
    return dict(response)


@api_router_v1.get('/read_all_items/',
                   summary='Получение всех записей',
                   description='Получение всех записей в виде списка',
                   status_code=status.HTTP_200_OK,
                   response_model=DatabaseListEntitiesResponseModel
                   )
async def read_all_items(connection=Depends(get_connection)):
    sql_raw_query = """SELECT * FROM items"""
    records_list = await connection.fetch(sql_raw_query)
    response = ([dict(row) for row in records_list])
    return {'data': response}


@api_router_v1.post('/',
                    summary='Создание записи',
                    description='''Для создания записи,
                                   необходимо чтобы "name" было уникальным,
                                   длина "name" должна быть от 2 до 150,
                                   а "value" вида jsonb
                                ''',
                    status_code=status.HTTP_201_CREATED,
                    response_model=DatabaseEntityResponseModel
                    )
async def create_item(item: DatabaseEntityModel,
                      connection=Depends(get_connection)
                      ) -> dict:
    sql_raw_query = """INSERT INTO items(name, value)
                    VALUES($1, $2)
                    RETURNING *
                    """
    # костыль со строкой-скобочки, пока не знаю как преобразовать
    # бд ожидает строку, а на вход подаем json
    new_value_like_str = f'"{item.value}"'
    try:
        async with connection.transaction():
            response = await connection.fetchrow(sql_raw_query,
                                                 item.name,
                                                 new_value_like_str
                                                 )
    except asyncpg.UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Это имя не уникально, попробуйте другое',
        )
    return dict(response)


@api_router_v1.put('/{entity_id}/',
                   summary='Редактирование одной записи',
                   description='''Редактирование одной записи по id,
                                устанавливается время изменения
                                ''',
                   response_model=DatabaseEntityResponseModel
                   )
async def update_item(entity_id: int,
                      item: DatabaseEntityModel,
                      connection=Depends(get_connection)
                      ) -> dict:
    moscow_dt = datetime.now(tz=ZoneInfo('Europe/Moscow'))
    # костыль со строкой-скобочки, пока не знаю как преобразовать
    new_value_like_str = f'"{item.value}"'
    sql_raw_query = """UPDATE items
                    SET name = $1,
                    value = $2,
                    date_update = $3
                    WHERE id = $4
                    RETURNING *
                    """
    try:
        async with connection.transaction():
            response = await connection.fetchrow(
                sql_raw_query,
                item.name,
                new_value_like_str,
                moscow_dt,
                entity_id
            )
    except asyncpg.UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Это имя не уникально, попробуйте другое',
        )
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Запись не найдена',
        )
    return dict(response)


@api_router_v1.delete('/{entity_id}/',
                      summary='Удаление записи',
                      description='Удаление записи по id',
                      status_code=status.HTTP_204_NO_CONTENT
                      )
async def delete_item(entity_id: int,
                      connection=Depends(get_connection)
                      ):
    sql_raw_query = """DELETE FROM items WHERE id = $1"""
    await connection.execute(sql_raw_query, entity_id)
