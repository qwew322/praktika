import sqlite3
import repository


def _positive_int(value, field_name):
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be an integer")

    if value <= 0:
        raise ValueError(f"{field_name} must be greater than 0")
    return value


def get_categories(params):
    category_id = params.get("id", [None])[0]
    if category_id is None:
        return 200, {"categories": repository.get_categories()}

    category_id = _positive_int(category_id, "id")
    category = repository.get_categories(category_id)
    if category is None:
        return 404, {"error": "Category not found"}
    return 200, category


def post_category(data: dict):
    name = str(data.get("name", "")).strip()

    if not name:
        return 400, {"error": "Field 'name' is required"}
    parent_id = data.get("parent_id")
    try:
        category = repository.create_category(name, parent_id)
    except sqlite3.IntegrityError:
        return 409, {"error": "Category with this name already exists"}

    return 201, category


def put_category(data):
    if "id" not in data:
        return 400, {"error": "Field 'id' is required"}

    category_id = _positive_int(data["id"], "id")
    name = str(data.get("name", "")).strip()
    if not name:
        return 400, {"error": "Field 'name' is required"}

    try:
        category = repository.update_category(category_id, name)
    except sqlite3.IntegrityError:
        return 409, {"error": "Category with this name already exists"}

    if category is None:
        return 404, {"error": "Category not found"}
    return 200, category


def delete_category(params):
    category_id = params.get("id", [None])[0]
    if category_id is None:
        return 400, {"error": "Query parameter 'id' is required"}

    category_id = _positive_int(category_id, "id")
    if not repository.delete_category(category_id):
        return 404, {"error": "Category not found"}
    return 200, {"message": "Category deleted", "id": category_id}


def get_articles(params):
    article_id = params.get("id", [None])[0]
    category_id = params.get("category_id", [None])[0]

    if article_id is not None:
        article_id = _positive_int(article_id, "id")
        article = repository.get_articles(article_id=article_id)
        if article is None:
            return 404, {"error": "Article not found"}
        return 200, article

    if category_id is not None:
        category_id = _positive_int(category_id, "category_id")

    return 200, {
        "articles": repository.get_articles(category_id=category_id)
    }


def _article_fields(data):
    title = str(data.get("title", "")).strip()
    if not title:
        raise ValueError("Field 'title' is required")

    content = str(data.get("content", "")).strip()
    category_id = data.get("category_id")

    if category_id is not None:
        category_id = _positive_int(category_id, "category_id")
        if repository.get_categories(category_id) is None:
            raise LookupError("Category not found")

    return title, content, category_id


def post_article(data):
    title, content, category_id = _article_fields(data)
    article = repository.create_article(title, content, category_id)
    return 201, article


def put_article(data):
    if "id" not in data:
        return 400, {"error": "Field 'id' is required"}

    article_id = _positive_int(data["id"], "id")
    if repository.get_articles(article_id=article_id) is None:
        return 404, {"error": "Article not found"}

    title, content, category_id = _article_fields(data)
    article = repository.update_article(
        article_id, title, content, category_id
    )
    return 200, article


def delete_article(params):
    article_id = params.get("id", [None])[0]
    if article_id is None:
        return 400, {"error": "Query parameter 'id' is required"}

    article_id = _positive_int(article_id, "id")
    if not repository.delete_article(article_id):
        return 404, {"error": "Article not found"}
    return 200, {"message": "Article deleted", "id": article_id}
