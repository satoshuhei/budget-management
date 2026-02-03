from app.application.dto import CategoryCreate, CategoryUpdate, SubcategoryCreate, SubcategoryUpdate
from app.application.usecases import (
    create_category,
    create_subcategory,
    delete_category,
    delete_subcategory,
    update_category,
    update_subcategory,
)


def test_category_update_delete(uow_sqlite):
    category = create_category(uow_sqlite, CategoryCreate(name="IT"))
    updated = update_category(uow_sqlite, category.id, CategoryUpdate(name="IT-Infra"))
    assert updated is True

    deleted = delete_category(uow_sqlite, category.id)
    assert deleted is True


def test_subcategory_update_delete(uow_sqlite):
    category = create_category(uow_sqlite, CategoryCreate(name="IT"))
    sub = create_subcategory(uow_sqlite, SubcategoryCreate(category_id=category.id, name="SaaS"))

    updated = update_subcategory(uow_sqlite, sub.id, SubcategoryUpdate(category_id=category.id, name="Cloud"))
    assert updated is True

    deleted = delete_subcategory(uow_sqlite, sub.id)
    assert deleted is True
