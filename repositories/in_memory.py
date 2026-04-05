from repositories.base import OrderRepository

class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self.__orders = []
        self._index_id = 1

    def add(self, order):
        order.set_order_id(self._index_id)
        self.__orders.append(order)
        self._index_id += 1

    def get_all(self):
        return self.__orders.copy()

    def get_by_id(self, order_id):
        for order in self.__orders:
            if order.get_order_id() == order_id:
                return order
        return None