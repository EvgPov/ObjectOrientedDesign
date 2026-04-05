import json
import os
from datetime import datetime

from repositories.base import OrderRepository
from models.order import Order
from models.book import Book, FantasyBook, ScienceBook, ArtBook, DetectiveBook, ChildrenBook, ProgrammingBook
from models.collection import BookCollection
from factories.book_factory import BookFactory


class FileRepository(OrderRepository):
    """Репозиторий с полным восстановлением заказов"""

    def __init__(self, filename="orders.json"):
        self.filename = filename
        self._ensure_file_exists()
        self._factory = BookFactory()

        # Словарь всех доступных классов книг
        self._book_classes = {
            "FantasyBook": FantasyBook,
            "ScienceBook": ScienceBook,
            "ArtBook": ArtBook,
            "DetectiveBook": DetectiveBook,
            "ChildrenBook": ChildrenBook,
            "ProgrammingBook": ProgrammingBook,
        }

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _load_orders(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except:
            self._ensure_file_exists()
            return []

    def _save_orders(self, orders_data):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(orders_data, f, ensure_ascii=False, indent=2)

    def add(self, order):
        orders_data = self._load_orders()

        order_id = len(orders_data) + 1
        order.set_order_id(order_id)

        items_data = []
        for item in order.get_items():
            if isinstance(item, BookCollection):
                items_data.append(item.to_dict())
            elif isinstance(item, Book):
                items_data.append({
                    "type": "book",
                    "class": item.__class__.__name__,
                    "title": item.get_title(),
                    "author": item.get_author(),
                    "price": item.get_price()
                })

        order_dict = {
            "order_id": order.get_order_id(),
            "reader_id": order.get_reader_id(),
            "date": order.get_date().isoformat(),
            "status": order.get_status(),
            "items": items_data
        }

        orders_data.append(order_dict)
        self._save_orders(orders_data)

        print(f"Заказ №{order_id} сохранён в файл.")

    def get_all(self):
        data = self._load_orders()
        orders = []

        for d in data:
            items = []
            for it in d.get('items', []):
                if it.get("type") == "collection":
                    collection = BookCollection.from_dict(it, self._factory, self._book_classes)
                    items.append(collection)

                elif it.get("type") == "book":
                    cls_name = it.get("class")
                    cls = self._book_classes.get(cls_name)
                    if cls:
                        book = self._factory.create_book(
                            cls,
                            it.get("title", ""),
                            it.get("author", ""),
                            it.get("price", 0)
                        )
                        items.append(book)
                    else:
                        print(f"Класс {cls_name} не найден")

            order = Order(reader_id=d.get('reader_id', 0), items=items)
            order.set_order_id(d.get('order_id', 0))
            order.change_status(d.get('status', 'Оформлен'))

            if 'date' in d:
                try:
                    order._Order__date = datetime.fromisoformat(d['date'])
                except:
                    pass

            orders.append(order)

        return orders

    def get_by_id(self, order_id: int):
        orders = self.get_all()
        for order in orders:
            if order.get_order_id() == order_id:
                return order
        return None