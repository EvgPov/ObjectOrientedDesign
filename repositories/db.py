import psycopg2
import config

from psycopg2.extras import  RealDictCursor
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
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
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
            # Заказы
            cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                reader_id INTEGER NOT NULL,
                status VARCHAR(50) CHECK(status IN ('created', 'in progress', 'ready', 'closed')) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            )''')
            # Книги
            cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                book_id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255),
                price NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
                book_class VARCHAR(50) NOT NULL DEFAULT 'Book',
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                UNIQUE(title, author)
            )''')
            # Коллекции
            cursor.execute('''CREATE TABLE IF NOT EXISTS book_collections (
                collection_id SERIAL PRIMARY KEY,
                theme VARCHAR(255) NOT NULL,
                custom_price NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            )''')
            # Связь коллекций с книгами
            cursor.execute('''CREATE TABLE IF NOT EXISTS collection_books (
                collection_id INTEGER REFERENCES book_collections(collection_id) ON DELETE CASCADE,
                book_id  INTEGER REFERENCES books(book_id) ON DELETE CASCADE,
                PRIMARY KEY (collection_id, book_id),
                FOREIGN KEY (collection_id) REFERENCES book_collections(collection_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
            )''')
            # связь заказов с книгами
            cursor.execute('''CREATE TABLE IF NOT EXISTS order_books (
                order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
                book_id INTEGER NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
                quantity INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (order_id, book_id),
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
            )''')

            # связь заказов с коллекциями
            cursor.execute('''CREATE TABLE IF NOT EXISTS order_collections (
                order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
                collection_id INTEGER NOT NULL REFERENCES book_collections(collection_id) ON DELETE CASCADE,
                quantity INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (order_id, collection_id),
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY (collection_id) REFERENCES book_collections(collection_id) ON DELETE CASCADE
            )''')
            self.connection.commit()

    # Добавление книги в базу, если ее еще нет
    def add_book(self, book: Book):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO books (title, author, price, book_class)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (title, author) DO NOTHING
                RETURNING book_id
            ''', (book.get_title(), book.get_author(), book.get_price(), book.__class__.__name__))

            result = cursor.fetchone()

            if result:
                book_id = result[0]
                print(f"Книга '{book.get_title()}' добавлена (ID: {book_id})")
            else:
                # если книга уже существует в базе
                cursor.execute('''
                    SELECT book_id 
                    FROM books 
                    WHERE title = %s AND author = %s
                    ORDER BY book_id DESC 
                    LIMIT 1
                ''', (book.get_title(), book.get_author()))
                book_id = cursor.fetchone()[0]
                print(f"Книга '{book.get_title()}' уже существует в базе (ID: {book_id})")

            self.connection.commit()

    # Добавление коллекций
    def add_collection(self, collection: BookCollection):
        with self.connection.cursor() as cursor:
            cursor.execute('''
            INSERT INTO book_collections (theme, custom_price)
            VALUES (%s, %s)
            RETURNING collection_id
            ''', (collection.get_title(), collection.get_price()))
            self.connection.commit()

            collection_id = cursor.fetchone()[0]

            for book in collection.get_books():
                cursor.execute('''
                    SELECT book_id 
                    FROM books
                    WHERE title = %s AND author = %s
                    ORDER BY book_id DESC
                    LIMIT 1
                    ''', (book.get_title(), book.get_author()))
                result = cursor.fetchone()
                if result:
                    book_id = result[0]

                    cursor.execute('''
                        INSERT INTO collection_books (collection_id, book_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    ''', (collection_id, book_id))
                else:
                    print(f"Книга {book.get_title()} не найдена в базе")
            self.connection.commit()
            print(f"Коллекция '{collection.get_title()}' добавлена (ID: {collection_id})")

    # добавление заказа
    def add(self, order: Order):
        with self.connection.cursor() as cursor:
            # 1. Добавляем заказ
            cursor.execute('''INSERT INTO orders (reader_id, status) 
                              VALUES (%s, %s) RETURNING order_id''',
                           (order.get_reader_id(), order.get_status()))

            order_id = cursor.fetchone()[0]

            # books_values = []
            # order_book_values = []

            # 2. Обрабатываем все элементы заказа
            for item in order.get_items():
                if isinstance(item, BookCollection):
                    # находим collection_id по теме (предполагается, что тем уникатьна)
                    cursor.execute('''
                        SELECT collection_id
                        FROM book_collections
                        WHERE theme=%s
                        ORDER BY collection_id DESC
                        LIMIT 1
                    ''', (item.get_title(),))

                    result = cursor.fetchone()
                    if result:
                        collection_id = result[0]
                        cursor.execute('''
                            INSERT INTO order_collections (order_id, collection_id, quantity)
                            VALUES (%s, %s, %s)
                        ''', (order_id, collection_id, 1))
                elif isinstance(item, Book):
                    # находим book_id
                    cursor.execute('''
                        SELECT book_id
                        FROM books
                        WHERE title=%s AND author=%s
                        ORDER BY book_id DESC
                        LIMIT 1
                    ''', (item.get_title(), item.get_author()))
                    result = cursor.fetchone()
                    if result:
                        book_id = result[0]
                        cursor.execute('''
                            INSERT INTO order_books (order_id, book_id, quantity)
                            VALUES (%s, %s, %s)
                            ''', (order_id, book_id, 1))

            self.connection.commit()
            print(f"Заказ №{order_id} успешно добавлен в базу")
    # получение всех заказов
    def get_all(self) -> List[Order]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Загружаем обычные книги
            cursor.execute('''
                SELECT 
                    o.order_id, o.reader_id, o.status, o.created_at,
                    b.book_id, b.title, b.author, b.price, b.book_class
                FROM orders o
                JOIN order_books ob ON o.order_id = ob.order_id
                JOIN books b ON ob.book_id = b.book_id
                ORDER BY o.order_id, b.book_id
            ''')
            book_rows = cursor.fetchall()

            # Загружаем коллекции
            cursor.execute('''
                SELECT 
                    o.order_id, o.reader_id, o.status, o.created_at,
                    bc.collection_id, bc.theme, bc.custom_price
                FROM orders o
                JOIN order_collections oc ON o.order_id = oc.order_id
                JOIN book_collections bc ON oc.collection_id = bc.collection_id
                ORDER BY o.order_id
            ''')
            collection_rows = cursor.fetchall()

        orders_dict = {}

        # Книги
        for row in book_rows:
            oid = row['order_id']
            if oid not in orders_dict:
                orders_dict[oid] = {
                    'order_id': oid,
                    'reader_id': row['reader_id'],
                    'status': row['status'],
                    'created_at': row['created_at'],
                    'items': []
                }

            try:
                book_class = self._book_classes.get(row['book_class'], Book)
                book = self._factory.create_book(
                    book_class=book_class,
                    title=row['title'],
                    author=row.get('author') or "",
                    price=float(row['price']) if row['price'] is not None else 0.0
                )
                orders_dict[oid]['items'].append(book)
            except Exception as e:
                print(f"Ошибка создания книги '{row.get('title')}': {e}")

        # Коллекции
        for row in collection_rows:
            oid = row['order_id']
            if oid not in orders_dict:
                orders_dict[oid] = {
                    'order_id': oid,
                    'reader_id': row['reader_id'],
                    'status': row['status'],
                    'created_at': row['created_at'],
                    'items': []
                }

            try:
                collection = self._load_collection(row['collection_id'])
                if collection:
                    orders_dict[oid]['items'].append(collection)
            except Exception as e:
                print(f"Ошибка загрузки коллекции ID {row.get('collection_id')}: {e}")

        sorted_orders = sorted(orders_dict.values(), key=lambda x: x['order_id'])

        # Создаём список объектов Order
        order_objects = []
        for data in sorted_orders:
            order = Order(
                reader_id=data['reader_id'],
                items=data['items']
            )
            order.set_order_id(data['order_id'])
            order.change_status(data['status'])

            order_objects.append(order)

        return order_objects

    # загрузка коллекций с книгами
    def _load_collection(self, collection_id: int) -> Optional[BookCollection]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
                SELECT theme, custom_price 
                FROM book_collections 
                WHERE collection_id = %s
            ''', (collection_id,))
            coll = cursor.fetchone()
            if not coll:
                return None
            cursor.execute('''
                SELECT b.book_id, b.title, b.author, b.price, b.book_class
                FROM collection_books cb
                JOIN books b ON cb.book_id = b.book_id
                WHERE cb.collection_id = %s
                ORDER BY b.book_id
            ''', (collection_id,))

            books = []
            for row in cursor.fetchall():
                try:
                    book_class = self._book_classes.get(row['book_class'], Book)
                    book = self._factory.create_book(
                        book_class=book_class,
                        title=row['title'],
                        author=row.get('author') or "",
                        price=float(row['price']) if row['price'] is not None else 0.0
                    )
                    books.append(book)
                except Exception as e:
                    print(f"Ошибка создания книги в коллекции: {e}")

            return BookCollection.create_with_books(
                theme=coll['theme'],
                books=books,
                custom_price=coll['custom_price']
            )
    # получение заказа по id
    def get_by_id(self, order_id: int) -> Optional[Order]:
        """Загружает один заказ с полноценной поддержкой книг и коллекций"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # 1. Загружаем обычные книги в заказе
            cursor.execute('''
                SELECT 
                    o.order_id, o.reader_id, o.status, o.created_at,
                    b.book_id, b.title, b.author, b.price, b.book_class
                FROM orders o
                JOIN order_books ob ON o.order_id = ob.order_id
                JOIN books b ON ob.book_id = b.book_id
                WHERE o.order_id = %s
                ORDER BY b.book_id
            ''', (order_id,))
            book_rows = cursor.fetchall()

            # 2. Загружаем коллекции в заказе
            cursor.execute('''
                SELECT 
                    o.order_id, o.reader_id, o.status, o.created_at,
                    bc.collection_id, bc.theme, bc.custom_price
                FROM orders o
                JOIN order_collections oc ON o.order_id = oc.order_id
                JOIN book_collections bc ON oc.collection_id = bc.collection_id
                WHERE o.order_id = %s
            ''', (order_id,))
            collection_rows = cursor.fetchall()

        if not book_rows and not collection_rows:
            return None
        first_row = book_rows[0] if book_rows else collection_rows[0]

        items = []
        # Добавляем обычные книги
        for row in book_rows:
            try:
                book_class = self._book_classes.get(row['book_class'], Book)
                book = self._factory.create_book(
                    book_class=book_class,
                    title=row['title'],
                    author=row.get('author') or "",
                    price=float(row['price']) if row['price'] is not None else 0.0
                )
                items.append(book)
            except Exception as e:
                print(f"Ошибка создания книги '{row.get('title')}': {e}")

        # Добавляем коллекции
        for row in collection_rows:
            try:
                collection = self._load_collection(row['collection_id'])
                if collection:
                    items.append(collection)
            except Exception as e:
                print(f"Ошибка загрузки коллекции ID {row.get('collection_id')}: {e}")

        # Создаём объект заказа
        order = Order(
            reader_id=first_row['reader_id'],
            items=items
        )
        order.set_order_id(first_row['order_id'])
        order.change_status(first_row['status'])

        return order