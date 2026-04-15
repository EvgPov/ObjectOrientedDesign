from builders.collection_builder import BookCollectionBuilder
from factories.book_factory import BookFactory
from models.book import FantasyBook, ScienceBook, ArtBook, ChildrenBook, DetectiveBook,  ProgrammingBook
from models.order import Order
from repositories.db import DBRepository
from repositories.in_file import FileRepository
from repositories.in_memory import InMemoryOrderRepository
from services.order_service import OrderService


def main():
    choice = input("Выберите тип хранилища:\n1. В памяти\n2. В файле\n3. В базе данных\nВаш выбор: ")

    match choice:
        case "1":
            repository = InMemoryOrderRepository()
        case "2":
            repository = FileRepository()
        case "3":
            repository = DBRepository()

    service = OrderService(repository)
    factory = BookFactory()
    builder = BookCollectionBuilder()

    # Создаем книги через фабрику
    book1 = factory.create_book(FantasyBook, "Дюна", "Фрэнк Герберт", 450)
    book2 = factory.create_book(FantasyBook, "451 градус по Фаренгейту", "Рэй Брэдбери", 380)
    book3 = factory.create_book(ScienceBook, "Краткая история времени", "Стивен Хокинг", 520)
    book4 = factory.create_book(ArtBook, "Искусство войны", "Сунь-цзы", 300)

    book5 = factory.create_book(ProgrammingBook, "Компьютерные сети", "Эндрю Таненбаум, Дэвид Уэзеролл", 2300)
    book6 = factory.create_book(ProgrammingBook, "Архитектура компьютера", "Эндрю Таненбаум, Тодд Остин", 1200)
    book7 = factory.create_book(ProgrammingBook, "Структуры данных и алгоритмы Java", "Роберт Лафоре", 3000)


    print("\nКниги созданы:")
    print('\n'.join(f"\n{i}. {book.get_info()}" for i, book in enumerate([book1,
    book2, book3, book4, book5, book6, book7], 1)))

    # Создаем подборку фантастики через строитель
    builder1 = BookCollectionBuilder()
    collection_fantasy = builder1.set_theme("Лучшая фантастика") \
        .add_book(book1) \
        .add_book(book2) \
        .build()

    # Создаем подборку книг по программированию через строитель
    builder2 = BookCollectionBuilder()
    collection_programming = builder2.set_theme("IT для начинающих") \
        .add_book(book5) \
        .add_book(book6) \
        .add_book(book7) \
        .set_price(10000) \
        .build()

    print("\nПодборка фантастики создана:")
    print(collection_fantasy.get_info())

    print("\nПодборка по программированию создана:")
    print(collection_programming.get_info())

    # Создаем заказы
    order1 = Order(101, [book3, book4, collection_fantasy])
    order2 = Order(102, [collection_programming])

    # Сохраняем заказы
    service.add(order1)
    service.add(order2)

    # Показываем все заказы
    print("\n=== Все заказы ===")
    all_orders = service.get_all()
    i = 0
    while i < len(all_orders):
        print(all_orders[i].get_info())
        print("-------------------")
        i +=  1

    # Меняем статус
    service.change_status(1, "ready")

if __name__ == "__main__":
    main()