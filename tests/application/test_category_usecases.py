from app.application.dto import CategoryCreate, SubcategoryCreate
from app.application.usecases import create_category, create_subcategory, list_categories, list_subcategories


def test_category_and_subcategory(uow_sqlite):
    category = create_category(uow_sqlite, CategoryCreate(name="IT"))
    sub = create_subcategory(uow_sqlite, SubcategoryCreate(category_id=category.id, name="SaaS"))

    categories = list_categories(uow_sqlite)
    subs = list_subcategories(uow_sqlite, category_id=category.id)

    assert categories[0].name == "IT"
    assert subs[0].name == "SaaS"
