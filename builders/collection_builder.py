from models.collection import BookCollection

class BookCollectionBuilder:
    def __init__(self):
        self._theme = "Без темы"
        self._books = []
        self._custom_price = None

    def set_theme(self, theme):
        self._theme = theme
        return self

    def add_book(self, book):
        self._books.append(book)
        return self

    def set_price(self, price):
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")
        self._custom_price = price
        return self

    def build(self):
        if not self._books:
            raise ValueError('Подборка должна содержать хотя бы одну книгу')
        return BookCollection.create_with_books(
            theme=self._theme,
            books=self._books,
            custom_price=self._custom_price
        )