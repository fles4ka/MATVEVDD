
import logging

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Настройка роутера
router = APIRouter(
    prefix="/items",
    tags=["items"]
)


# Тестовая база данных
fake_db = {
    1: {"name": "Foo", "price": 50.2},
    2: {"name": "Book", "price": 30.0}
}


# Модель товара
class Item(BaseModel):
    name: str = Field(
        ...,
        title="Название",
        examples=["Телефон"]
    )

    price: float = Field(
        ...,
        gt=0,
        title="Цена",
        examples=[199.99]
    )

    is_offer: bool | None = Field(
        None,
        title="Акционный товар"
    )


# Получение товара по ID
@router.get(
    "/{item_id}",
    summary="Получить товар по ID",
    description="Поиск товара в тестовой базе данных",
    responses={
        404: {"description": "Item not found"}
    }
)
def read_item(
    item_id: int = Path(
        ...,
        title="ID товара",
        ge=1
    ),
    q: str | None = Query(
        None,
        title="Поисковый запрос",
        max_length=50
    )
):
    logger.info(f"Запрошен товар с ID {item_id}")

    if item_id not in fake_db:
        logger.warning(f"Товар с ID {item_id} не найден")
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    logger.info(f"Товар с ID {item_id} успешно найден")

    return {
        "item_id": item_id,
        "item": fake_db[item_id],
        "q": q
    }


# Создание товара
@router.post(
    "/",
    response_model=Item,
    summary="Создать товар",
    description="Принимает данные нового товара"
)
def create_item(item: Item):
    logger.info(f"Создание нового товара: {item.name}")
    return item


# Обновление товара
@router.put(
    "/{item_id}",
    summary="Обновить товар",
    description="Обновление существующего товара",
    responses={
        404: {"description": "Item not found"},
        409: {"description": "Item name already exists"}
    }
)
def update_item(
    item_id: int = Path(..., title="ID товара", ge=1),
    item: Item = ...
):
    logger.info(f"Попытка обновить товар с ID {item_id}")

    # Проверка существования товара
    if item_id not in fake_db:
        logger.warning(
            f"Попытка обновить несуществующий товар ID {item_id}"
        )
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    # Проверка уникальности названия
    for existing_id, existing_item in fake_db.items():
        if (
            existing_id != item_id
            and existing_item["name"].casefold()
            == item.name.strip().casefold()
        ):
            logger.warning(
                f"Название '{item.name}' уже используется "
                f"товаром ID {existing_id}"
            )
            raise HTTPException(
                status_code=409,
                detail="Item name already exists"
            )

    # Обновление товара
    fake_db[item_id] = {
        "name": item.name.strip(),
        "price": item.price,
        "is_offer": item.is_offer
    }

    logger.info(f"Товар с ID {item_id} успешно обновлён")

    return {
        "item_id": item_id,
        "item": fake_db[item_id]
    }
