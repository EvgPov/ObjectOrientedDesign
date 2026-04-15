import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from typing import List, Optional
from collections import defaultdict

from repositories.base import OrderRepository
from models.order import Order
from models.book import (
    Book, FantasyBook, ScienceBook, ArtBook,
    DetectiveBook, ChildrenBook, ProgrammingBook
)
from factories.book_factory import BookFactory
from models.collection import BookCollection


class DBRepository(OrderRepository):
    """Репозиторий для PostgreSQL, аналогичный FileRepository"""

    def __init__(self):
        self.connection = psycopg2.connect(
            host='localhost',
            port='5432',
            database='library',
            user='pvlevg',
            password=''
        )
        self._factory = BookFactory()

        # Словарь классов книг — как в FileRepository
        self._book_classes = {
            "FantasyBook": FantasyBook,
            "ScienceBook": ScienceBook,
            "ArtBook": ArtBook,
            "DetectiveBook": DetectiveBook,
            "ChildrenBook": ChildrenBook,
            "ProgrammingBook": ProgrammingBook,
            "Book": Book  # ← добавили fallback
        }

        self.create_table()

    def __del__(self):
        self.connection.close()

    def create_table(self):
        with self.connection.cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                reader_id INTEGER NOT NULL,
                status VARCHAR(50) CHECK(status IN ('created', 'in progress', 'ready', 'closed')) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                book_id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255),
                price NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
                order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
                book_class VARCHAR(50) NOT NULL DEFAULT 'Book'
            )''')

            self.connection.commit()

    def add(self, order: Order):
        with self.connection.cursor() as cursor:
            # 1. Добавляем заказ
            cursor.execute('''INSERT INTO orders (reader_id, status) 
                              VALUES (%s, %s) RETURNING order_id''',
                           (order.get_reader_id(), order.get_status()))

            order_id = cursor.fetchone()[0]

            books_items = []

            # 2. Обрабатываем все элементы заказа
            for item in order.get_items():
                if isinstance(item, BookCollection):
                    # Для коллекции добавляем все книги из неё
                    for book in item._books:  # ← используем _books напрямую
                        if isinstance(book, Book):
                            books_items.append((
                                book.get_title(),
                                book.get_author(),
                                book.get_price(),
                                order_id,
                                book.__class__.__name__
                            ))
                elif isinstance(item, Book):
                    # Обычная книга
                    books_items.append((
                        item.get_title(),
                        item.get_author(),
                        item.get_price(),
                        order_id,
                        item.__class__.__name__
                    ))

            # 3. Массово вставляем все книги
            if books_items:
                execute_values(cursor, '''
                    INSERT INTO books (title, author, price, order_id, book_class)
                    VALUES %s
                ''', books_items)

            self.connection.commit()
            print(f"Заказ №{order_id} успешно добавлен в базу (книг: {len(books_items)})")

    def get_all(self) -> List[Order]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
                SELECT 
                    o.order_id, 
                    o.reader_id, 
                    o.status, 
                    o.created_at,
                    b.title, 
                    b.author, 
                    b.price,
                    b.book_class
                FROM orders o 
                LEFT JOIN books b ON o.order_id = b.order_id
                ORDER BY o.order_id, b.book_id
            ''')
            rows = cursor.fetchall()

        if not rows:
            return []

        orders_dict = defaultdict(lambda: {
            'order_id': None,
            'reader_id': None,
            'status': None,
            'created_at': None,
            'items': []
        })

        for row in rows:
            oid = row['order_id']

            if orders_dict[oid]['order_id'] is None:
                orders_dict[oid].update({
                    'order_id': oid,
                    'reader_id': row['reader_id'],
                    'status': row['status'],
                    'created_at': row['created_at']
                })

            if row.get('title'):
                cls_name = row.get('book_class', 'Book')
                book_class = self._book_classes.get(cls_name, Book)

                try:
                    book = self._factory.create_book(
                        book_class=book_class,
                        title=row['title'],
                        author=row.get('author') or "",
                        price=float(row['price']) if row['price'] is not None else 0
                    )
                    orders_dict[oid]['items'].append(book)
                except TypeError:
                    # Если класс не принимает аргументы (абстрактный Book)
                    print(f"Предупреждение: Не удалось создать книгу класса {cls_name}")
                    continue

        # Создаём объекты Order
        order_objects = []
        for data in orders_dict.values():
            order = Order(
                reader_id=data['reader_id'],
                items=data['items']
            )
            order.set_order_id(data['order_id'])
            order.change_status(data['status'])
            order_objects.append(order)

        return order_objects

    def get_by_id(self, order_id: int) -> Optional[Order]:
        orders = self.get_all()
        for order in orders:
            if order.get_order_id() == order_id:
                return order
        return None