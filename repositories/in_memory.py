from repositories.base import OrderRepository

class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self.orders = []
        self.index_id = 1

    def add(self, order):
        order.order_id = self.index_id
        self.orders.append(order)
        self.index_id += 1
        print(f"Заказ №{order.ordr_id} сохранен в память")

    def get_all(self):
        return self.orders

    def get_by_id(self, order_id):
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None