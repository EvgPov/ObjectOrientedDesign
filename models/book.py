from abc import ABC, abstractmethod

class Book(ABC):
    def __init__(self, author, title, price):
        self.__author = author
        self.__title = title
        self.__price = price

    @abstractmethod
    def get_title(self):
        pass

    @abstractmethod
    def get_author(self):
        pass

    @abstractmethod
    def get_price(self):
        pass

    def get_info(self):
        return f"Автор: {self.get_author()}\nНазвание: {self.get_title()}\nЦена:({self.get_price()} руб.)"

class FantasyBook(Book):
    def __init__(self, author, title, price):
        super().__init__(author, title, price)

    def get_title(self):
        return f"Fantasy book {self.__title}"

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price


class ScienceBook(Book):
    def __init__(self, author, title, price):
        super().__init__(author, title, price)

    def get_title(self):
        return f"Fantasy book '{self.__title}'"

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price

class ArtBook(Book):
    def __init__(self, author, title, price):
        super().__init__(author, title, price)

    def get_title(self):
        return f"Art book '{self.__title}'"

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price

class DetectiveBook(Book):
    def __init__(self, author, title, price):
        super().__init__(author, title, price)

    def get_title(self):
        return f"Detective book '{self.__title}'"

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price

class ChildrenBook(Book):
    def __init__(self, author, title, price):
        super().__init__(author, title, price)

    def get_title(self):
        return f"Children book '{self.__title}'"

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price

class ProgrammingBook(Book):
    def __init__(self, author, title, price):
        super().__init__(author, title, price)

    def get_title(self):
        return f"Programming book '{self.__title}'"

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price