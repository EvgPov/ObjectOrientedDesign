from models.collection import BookCollection

class BookCollectionBuilder:
    def __init__(self):
        self.collection = BookCollection()

    def set_theme(self, theme):
        self.collection.theme = theme
        return self

    def add_book(self, book):
        self.collection.books.append(book)
        self.collection.total_price += book.get_price()
        return self

    def set_price(self, price):
        self.collection.total_price = price
        return self

    def build(self):
        return self.collection