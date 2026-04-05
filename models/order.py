from datetime import datetime

class Order:
    def __init__(self, reader_id, items):
        self.__order_id = 0
        self.__reader_id = reader_id
        self.__items = items
        self.__date = datetime.now()
        self.__status = 'Оформлен'

    def get_order_id(self):
        return self.__order_id

    def get_reader_id(self):
        return self.__reader_id

    def get_items(self):
        return self.__items.copy()

    def get_date(self):
        return self.__date

    def get_status(self):
        return self.__status

    def set_order_id(self, order_id):
        self.__order_id = order_id

    def change_status(self, status):
        self.__status = status

    def get_info(self):
        info = "Заказ №" + str(self.__order_id) + "\n"
        info += "Читатель ID: " + str(self.__reader_id) + "\n"
        info += f"Дата: {self.__date.strftime('%Y-%m-%d %H:%M')}\n"
        info += "Статус: " + str(self.__status) + "\n"
        info += "Содержимое:\n"

        i = 1
        for item in self.__items:
            info += f"  {i}. {item.get_info()}\n"
            i += 1

        return info