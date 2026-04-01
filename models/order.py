class Order:
    def __init__(self, reader_id, items):
        self.ordr_id = reader_id
        self.reader_id = reader_id
        self.items = items
        self.status = 'Оформлен'

    def get_info(self):
        info = "Заказ №" + str(self.ordr_id) + "\n"
        info += "Читатель ID: " + str(self.reader_id) + "\n"
        info += "Статус: " + str(self.status) + "\n"
        info += "Содержимое:\n"

        i = 1
        while i < len(self.items):
            info += " " + str(i) + "." + self.items[i - 1].get.info() + "\n"
            i += 1
        return info