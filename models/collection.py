from models.book import Book

class BookCollection(Book):
    def __init__(self):
        self.theme = "Без темы"
        self.books = []
        self.total_price = 0

    def get_title(self):
        return f"Подборка: {self.theme}"

    def get_price(self):
        return self.total_price

    def get_info(self):
        info = "Тема подборки: " + self.theme + "\n"
        info += "Общая цена подборки: " + self.total_price + " руб. \n"
        info += "Книги:\n"

        i = 1
        while i <= len(self.books):
            info += " " + str(i) + ". " + self.books[i - 1].get_info() + "\n"
            i += 1
        return info