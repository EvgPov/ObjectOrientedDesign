class OrderService:
    def __init__(self, repository):
        self.repository = repository

    def add(self, order):
        self.repository.add(order)

    def get_all(self):
        return self.repository.get_all()

    def get_by_id(self, order_id):
        return self.repository.get_by_id(order_id)

    def change_status(self, order_id, new_status):
        order = self.get_by_id(order_id)
        if order is not None:
            order.change_status(new_status)
            print(f"Статус заказа №{order_id} изменен на {new_status}")