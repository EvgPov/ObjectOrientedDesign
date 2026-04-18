from models.book import Book

class BookCollection(Book):
    # def __init__(self, theme =  "Без темы", books = None, custom_price = None):
    #     self._theme = theme
    #     self._books = list(books) if books is not None else []
    #     self._custom_price = custom_price
    def __init__(self, theme: str = "Без темы"):
        self._theme = theme
        self._books = []
        self._custom_price = None

    # Альтернативный конструктор для восстановления
    @classmethod
    def create_with_books(cls, theme: str, books: list, custom_price=None):
        collection = cls(theme)
        collection._books = list(books)  # важно: копия списка
        collection._custom_price = custom_price
        return collection

    def get_title(self):
        return self._theme

    def get_books(self):
        return self._books.copy()

    def get_author(self):
        if not self._books:
            return "Нет авторов"
        all_authors = []

        for book in self._books:
            author_str = book.get_author().strip()
            authors_list = [a.strip() for a in author_str.split(',')]
            all_authors.extend(authors_list)

        unique_authors = sorted(set(all_authors))
        return ", ".join(unique_authors)

    def get_price(self):
        if self._custom_price is not None:
            return self._custom_price
        return sum(book.get_price() for book in self._books)

    def to_dict(self):
        return {
            "type": "collection",
            "theme": self._theme,
            "custom_price": self._custom_price,
            "books": [
                {
                    "class": book.__class__.__name__,
                    "title": book.get_title(),
                    "author": book.get_author(),
                    "price": book.get_price()
                }
                for book in self._books
            ]
        }

    @staticmethod
    def from_dict(data: dict, factory, book_classes=None):
        if book_classes is None:
            book_classes = {}

        theme = data.get("theme", "Без темы")
        custom_price = data.get("custom_price")

        books = []
        for b in data.get("books", []):
            cls_name = b.get("class")
            cls = book_classes.get(cls_name)
            if cls:
                try:
                    book = factory.create_book(cls, b["title"], b["author"], b["price"])
                    books.append(book)
                except Exception as e:
                    print(f"Не удалось создать книгу {b.get('title')}: {e}")
            else:
                print(f"Класс {cls_name} не найден")

        return BookCollection.create_with_books(theme, books, custom_price)


    def get_info(self):
        info = f"Тема сборника: {self.get_title()}\n"
        info += f"Авторы: {self.get_author()}\n"
        info += f"Общая цена сборника: {self.get_price()} руб.\n"

        if self._custom_price is not None:
            info += "(цена установлена вручную)\n"

        info += "Книги:\n"

        i = 1
        for book in self._books:
            info += f"  {str(i)}. {book.get_info()}\n"
            i += 1
        return info