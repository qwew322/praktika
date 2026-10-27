from database import get_connection


def _row_to_dict(row):
    return dict(row) if row is not None else None


def get_categories(category_id=None):
    with get_connection() as connection:
        if category_id is None:
            rows = connection.execute(
                "SELECT id, name, parent_id FROM categories ORDER BY id"
            ).fetchall()
            return [dict(row) for row in rows]

        row = connection.execute(
            "SELECT id, name, parent_id FROM categories WHERE id = ?",
            (category_id,)
        ).fetchone()
        return _row_to_dict(row)


def create_category(name: str, parent_id : int = None):
    if parent_id is None:
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO categories (name) VALUES (?)",
                (name,)
            )
            return get_categories(cursor.lastrowid)

    else:
        print("fsdfdsf", parent_id)
        parent = get_categories(parent_id)
        print("sfsdfsdf", parent)
        if parent is None: 
            raise ValueError(f"{parent_id} is not include in database")
        else:
            with get_connection() as connection:
                        cursor = connection.execute(
                            "INSERT INTO categories (name, parent_id) VALUES (?, ?)",
                            (name, parent_id,)
                        )
                        return get_categories(cursor.lastrowid)




def update_category(category_id, name, parent_id):
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE categories SET name = ?, parent_id = ? WHERE id = ?",
            (name, parent_id, category_id)
        )
        if cursor.rowcount == 0:
            return None
    return get_categories(category_id)


def delete_category(category_id):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM categories WHERE id = ?",
            (category_id,)
        )
        return cursor.rowcount > 0


def get_articles(article_id=None, category_id=None):
    query = """
        SELECT
            articles.id,
            articles.title,
            articles.content,
            articles.category_id,
            categories.name AS category_name
        FROM articles
        LEFT JOIN categories ON categories.id = articles.category_id
    """
    params = []

    if article_id is not None:
        query += " WHERE articles.id = ?"
        params.append(article_id)
    elif category_id is not None:
        query += " WHERE articles.category_id = ?"
        params.append(category_id)

    query += " ORDER BY articles.id"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    if article_id is not None:
        return _row_to_dict(rows[0]) if rows else None
    return [dict(row) for row in rows]


def create_article(title, content, category_id):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO articles (title, content, category_id)
            VALUES (?, ?, ?)
            """,
            (title, content, category_id)
        )
        article_id = cursor.lastrowid
    return get_articles(article_id=article_id)


def update_article(article_id, title, content, category_id):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE articles
            SET title = ?, content = ?, category_id = ?
            WHERE id = ?
            """,
            (title, content, category_id, article_id)
        )
        if cursor.rowcount == 0:
            return None
    return get_articles(article_id=article_id)


def delete_article(article_id):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM articles WHERE id = ?",
            (article_id,)
        )
        return cursor.rowcount > 0
