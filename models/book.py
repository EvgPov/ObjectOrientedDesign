from abc import ABC, abstractmethod

class Book(ABC):
    @abstractmethod
    def get_title(self):
        pass

    @abstractmethod
    def get_author(self):
        pass

    @abstractmethod
    def get_price(self):
        pass

    def get_type(self):
        return "Книга"

    def get_info(self):
        return (f'Тип: {self.get_type()}\n'
                f'Автор: {self.get_author()}\n'
                f'Название: "{self.get_title()}"\n'
                f'Цена: {self.get_price()} руб.')

class FantasyBook(Book):
    def __init__(self, title: str, author: str, price: int):
        self.__title = title
        self.__author = author
        self.__price = price

    def get_title(self):
        return self.__title

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price

    def get_type(self):
        return "Фантастика"

class ScienceBook(Book):
    def __init__(self, title: str, author: str, price: int):
        self.__title = title
        self.__author = author
        self.__price = price

    def get_title(self):
        return self.__title

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price

    def get_type(self):
        return "Научная литература"

class ArtBook(Book):
    def __init__(self, title: str, author: str, price: int):
        self.__title = title
        self.__author = author
        self.__price = price

    def get_title(self):
        return self.__title

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price

    def get_type(self):
        return "Искусство"

class DetectiveBook(Book):
    def __init__(self, title: str, author: str, price: int):
        self.__title = title
        self.__author = author
        self.__price = price

    def get_title(self):
        return self.__title

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price

    def get_type(self):
        return "Детектив"

class ChildrenBook(Book):
    def __init__(self, title: str, author: str, price: int):
        self.__title = title
        self.__author = author
        self.__price = price

    def get_title(self):
        return self.__title

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price

    def get_type(self):
        return "Детская литература"

class ProgrammingBook(Book):
    def __init__(self, title: str, author: str, price: int):
        self.__title = title
        self.__author = author
        self.__price = price

    def get_title(self):
        return self.__title

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price

    def get_type(self):
        return "Программирование"