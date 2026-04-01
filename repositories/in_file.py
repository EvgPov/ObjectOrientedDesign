from repositories.base import OrderRepository

class FileRepository(OrderRepository):
    def __init__(self):
        self.filename = "orders.txt"

    def add(self, order):
        order.order_id = self.get_next_id()
        with open(self.filename, "a", encoding="utf-8") as file:
            file.write(f"Заказ №{order.ordr_id}\n")
            file.write(order.get_info() + "\n\n")
        print(f"Заказ №{order.ordr_id} сохранен в файл orders.txt")

    def get_next_id(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                content = file.read()
            return content.count("Заказ") + 1
        except:
            return 1

    def get_all(self):
        print("История из файла (упрощённо)")
        return []

    def get_by_id(self, order_id):
        print("Поиск по ID в файле не реализован в упрощённой версии")
        return None
