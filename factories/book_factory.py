from models.book import Book
from typing import Type

class BookFactory:

    @staticmethod
    def create_book(book_type: Type[Book], title: str, author:str, price: int):
       if not issubclass(book_type, Book):
           raise ValueError("book_type должен быть наследником класса Book")
       return book_type(title, author, price)