from models.book import Book
from typing import Type

class BookFactory:
    @staticmethod
    def create_book(book_class: Type[Book], title: str, author: str, price: int) -> Book:
        if not issubclass(book_class, Book):
            raise ValueError("book_type должен быть наследником Book")
        return book_class(title, author, price) # type: ignore[call-arg]

