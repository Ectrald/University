from utils import *


def menu():
    match int(input("1. Расчет времени подбора пароля\n 2.График зависимости среднего времени подбора пароля от его длины\n "
                    "3.Рекомендации\n"
                    "Выберите одну опцию: ")):
        case 1:
            calc_time_graph()
        case 2:
            graph_of_avg_cracking_time()
        case 3:
            recommendation()
        case default:
            print("Неверный выбор")

menu()


