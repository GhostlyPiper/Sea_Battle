import time
from random import randint, choice

# Последовательность букв латинского алфавита для координат оси x.
L_R = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Color:
    """
    Класс Color просто задаёт цвет.
    """
    reset = '\033[0m'
    yellow = '\033[1;93m'
    red = '\033[1;91m'
    red_1 = '\033[1;31m'
    turq = '\033[3;36m'
    green = '\033[1;32m'
    blue = '\033[1;34m'
    violet = '\033[1;35m'


# функция, которая окрашивает объект в заданный цвет.
def set_color(obj, color):
    return color + obj + Color.reset


# Создадим собственный класс исключений.
class BoardException(Exception):
    pass


# Далее уже от собственного класса создаём остальные.
class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    """
    Класс Dot используется для описания точек на игровом поле.

    Attributes
    ----------
    x : int
        координата по оси х
    y : int
        координата по оси Y.

    Methods
    -------
    __eq__()
        Сравнивает объекты класса Dot,
        выводит булевое значение равенства.

    __repr__()
        Выводит в консоль информацию об объекте класса Dot
        в виде кода создания этого объекта.
    """

    def __init__(self, x, y):
        """
        Устанавливает все необходимые атрибуты для объекта Dot.

        :param x: (int) координата по оси х
        :param y: (int) координата по оси Y
        """

        self.x = x
        self.y = y

    def __eq__(self, other):
        """
        Сравнивает объекты класса Dot
        (точки с одинаковыми координатами будут равны).

        :param other: объект класса Dot

        :return: bool значение равенства объектов
        """

        return self.x == other.x and self.y == other.y

    def __repr__(self):
        """
        Выводит в консоль информацию об объекте класса Dot
        в виде кода создания этого объекта.

        :return: str "Dot(x, y)"
        """

        return f"Dot({self.x}, {self.y})"


class Ship:
    """
    Класс Ship используется для описания корабля на игровом поле.

    Attributes
    ----------
    bow : class Dot
        Точка на игровом поле, где размещён нос корабля.

    len_ : int
        Размер корабля (его длина в точках игрового поля).

    ori : int
        Направление ориентации корабля (вертикальное: 0 - вверх, 1 = вниз;
        горизонтальное: 2 - вправо, 3 - влево).

    lives : int
        Количество жизней (сколько точек корабля ещё не подбито).

    Methods
    -------
    dots()
        Создаёт описание корабля в виде списка точек игрового поля
        на которых расположен корабль

    hits()
        Делает проверку есть ли попадание выстрела по кораблю.
    """

    def __init__(self, bow, len_, ori):
        """
        Устанавливает все необходимые атрибуты для объекта Ship.

        :param bow: class Dot Точка на игровом поле, где размещён нос корабля.

        :param len_: int Размер корабля (его длина в точках игрового поля).

        :param ori: int Направление ориентации корабля (вертикальное: 0 - вверх,
                    1 = вниз; горизонтальное: 2 - вправо, 3 - влево).

        Так же инициируем параметр lives: int изначально равный len_ - количество жизней
        (сколько точек корабля ещё не подбито).

        """

        self.bow = bow
        self.len_ = len_
        self.ori = ori
        self.lives = len_

    @property
    def dots(self):
        """
        Создаёт описание корабля в виде списка точек игрового поля
        на которых расположен корабль, по сути является свойством
        поэтому декорируется <@property>.

        :return: list[Dot(x, y), ..., Dot(xi, yi)]
        """

        ship_dots = []

        for i in range(self.len_):

            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.ori == 0:
                cur_x += i

            if self.ori == 1:
                cur_x -= i

            if self.ori == 2:
                cur_y += i

            if self.ori == 3:
                cur_y -= i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def hits(self, shot):
        """
        Делает проверку есть ли попадание выстрела по кораблю.

        :param shot: Dot Точка с координатами выстрела.
        :return: bool Булевое значение принадлежности точки выстрела
                 списку точек корабля.
        """

        return shot in self.dots


class Board:
    """
    Класс игровая доска.

    Attributes
    ----------
    hid : bool
        Определяет нужно ли скрывать корабли на игровом поле
        (при отображении поля противника корабли скрыты).

    size : int
        Размер игрового поля.

    count : int
        Счётчик поражённых кораблей.

    field : list
        Сетка игрового поля, в которой хранится состояние всех клеток.

    busy : list
        Список всех занятых точек: корабли, клетки по которым были произведены
        выстрелы.

    ships : list
        Список кораблей игрового поля.

    Methods
    -------
    add_ship()
        Добавляет корабли на игровое поле.

    contour()
        Создаёт список точек вокруг корабля - его контур.

    __str__()
        Служит для вывода игрового поля в консоль.

    out()
        Делает проверку выходит ли точка d за пределы игрового поля.

    shot()
        Выстрел по кораблю. Если точка выстрела вне пределов игрового поля
        или по ней уже был произведён выстрел, то вызывает исключения.
        Иначе определяет статус выстрела: попадание или промах, попутно
        делается проверка на уничтожение корабля полностью.

    defeat()
        Сравнивает количество подбитых кораблей с общим количеством.

    begin()
        Обнуляет список занятых клеток игрового поля.

    not_aim()
        Создаёт список валидных точек - координат для неприцельных выстрелов.

    aim()
        Создаёт список валидных точек - координат для прицельных выстрелов
        по вероятным клеткам расположения подбитого корабля.

    """

    def __init__(self, hid=False, size=10):
        """
        Устанавливает все необходимые атрибуты для объекта Board.

        :param hid: bool Определяет нужно ли скрывать корабли на игровом поле.
        :param size: int Размер сетки игрового поля.

        count : int Счётчик поражённых кораблей.

        field : list Сетка игрового поля, в которой хранится состояние всех клеток.

        busy : list Список всех занятых точек: корабли, клетки по которым были
                    произведены выстрелы.

        ships : list Список кораблей игрового поля.

        """

        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [["0"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def not_aim(self):
        """
        Создаёт список валидных точек - координат клеток игрового поля
        по которым можно производить выстрел. Занятые промахом
        и контуром убитых кораблей точки удаляются из списка.

        :return: list[Dot(x0, y0), ...., Dot(xi, yj)]
        """

        res = []
        for i, row in enumerate(self.field):
            x = i
            for j, val in enumerate(row):
                y = j
                d = Dot(x, y)
                res.append(d)
        for d in self.busy:
            res.remove(d)

        return res

    def aim(self):
        """
        Создаёт список валидных точек - координат клеток игрового поля
        где вероятнее всего располагаются следующие клетки подбитого, но
        не уничтоженного полностью корабля.
        :return: list[Dot(x0, y0), ...., Dot(xi, yj)]
        """

        near_1 = [(-1, 0), (1, 0)]
        near_2 = [(0, -1), (0, 1)]
        near_3 = [(-1, 0), (0, -1), (0, 1), (1, 0)]

        res = []
        for d in self.busy:
            for ship in self.ships:
                if d in ship.dots and ship.lives != 0:

                    for dx, dy in near_3:
                        aim = Dot(d.x + dx, d.y + dy)
                        if not (self.out(aim)) and aim not in self.busy:
                            res.append(aim)

                    if (Dot(d.x + 1, d.y) in self.busy and Dot(d.x + 1, d.y) in ship.dots)\
                            or Dot(d.x - 1, d.y) in self.busy and Dot(d.x - 1, d.y) in ship.dots:
                        res.clear()
                        for dx, dy in near_1:
                            aim = Dot(d.x + dx, d.y + dy)
                            if not (self.out(aim)) and aim not in self.busy:
                                res.append(aim)

                    if Dot(d.x, d.y + 1) in self.busy and Dot(d.x, d.y + 1) in ship.dots\
                            or Dot(d.x, d.y - 1) in self.busy and Dot(d.x, d.y - 1) in ship.dots:
                        res.clear()
                        for dx, dy in near_2:
                            aim = Dot(d.x + dx, d.y + dy)
                            if not (self.out(aim)) and aim not in self.busy:
                                res.append(aim)

        return res

    def add_ship(self, ship):
        """
        Добавляет корабли на игровое поле. Если точки корабля выходят за игровое
        поле или являются занятыми, то вызывает исключение BoardWrongShipException().

        """

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()

        for d in ship.dots:
            self.field[d.x][d.y] = set_color("■", Color.yellow)
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        """
        Создаёт список точек вокруг корабля - его контур,
        если корабль уничтожен выводит контур на игровое поле.

        :param ship: Объект класса Ship - корабль.
        :param verb: bool Статус корабля (True если корабль уничтожен)

        """

        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        """
        Служит для вывода игрового поля в консоль. При истинности
        переменной hid скрывает корабли на игровом поле.

        """

        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10|"

        for i, row in enumerate(self.field):
            res += f"\n{L_R[i + 1]} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", set_color("0", Color.reset))

        return res

    def out(self, d):
        """
        Делает проверку выходит ли точка d за пределы игрового поля.

        :param d: объект класса Dot
        :return: bool значение принадлежности точки игровому полю

        """

        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        """
        Делает выстрел по кораблю. Если точка выстрела вне пределов игрового поля
        вызывает исключение BoardOutException(), если по ней уже был произведён
        выстрел, то вызывает исключение BoardOutException().
        Иначе определяет статус выстрела: попадание или промах, попутно делается
        проверка на уничтожение корабля полностью.

        :param d: объект класса Dot.
        :return: bool возвращает True если попали по кораблю и False при промахе.

        """

        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardOutException()

        self.busy.append(d)

        for ship in self.ships:

            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = set_color("X", Color.red)

                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print(set_color("Корабль уничтожен!", Color.red_1))

                    return True

                else:
                    print(set_color("Корабль ранен!", Color.turq))

                    return True

        self.field[d.x][d.y] = "."
        print(set_color("Мимо!", Color.violet))

        return False

    def defeat(self):
        """
        Сравнивает количество подбитых кораблей с общим количеством.

        :return: bool значение сравнения

        """
        return self.count == len(self.ships)

    def begin(self):
        """
        Обнуляет список занятых клеток игрового поля.

        :return: list Пустой список занятых клеток.

        """

        self.busy = []


class Player:
    """
    Основной класс игроков.

    Attributes
    ----------
    board : класс Board
        Игровая доска - поле пользователя.

    enemy : класс Board
        Игровая доска - поле противника.

    Methods
    -------
    ask()
        Данный метод будет определён в наследственных классах игроков.

    move()
        Данный метод в бесконечном цикле пытается сделать выстрел.
        Если выстрел прошёл хорошо, то возвращается к условию нужно
        ли делать следующий выстрел. При возникновении исключений
        печатает соответствующее исключение.

    """

    def __init__(self, board, enemy):
        """
        Устанавливает все необходимые атрибуты для объекта Board.

        :param board: класс Board Игровая доска - поле пользователя.
        :param enemy: класс Board Игровая доска - поле противника.
        """
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        """
        Данный метод в бесконечном цикле пытается сделать выстрел.
        Если выстрел прошёл хорошо, то возвращается к условию нужно
        ли делать следующий выстрел. При возникновении исключений
        печатает соответствующее исключение.
        :return: bool значение результата выстрела (True при попадании).
        """

        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    """
    Класс игрока - компьютера (AI).

    Methods
    -------
    ask()
        Данный метод выбирает точку выстрела из списка неприцельных
        выстрелов, если список прицельных выстрелов пуст.

    """

    def ask(self):
        """
        Данный метод выбирает точку выстрела из списка неприцельных
        выстрелов, если список прицельных выстрелов пуст.

        :return: Dot(x, y) координаты выстрела.
        """

        if self.enemy.aim():
            d = choice(self.enemy.aim())
        else:
            d = choice(self.enemy.not_aim())

        print(f"Ход компьютера: {L_R[d.x + 1]} {d.y + 1}")
        return d


class User(Player):
    """
    Класс игрока - пользователя.

    Methods
    -------
    ask()
        Данный метод запрашивает у пользователя координаты выстрела,
        попутно делая проверки на корректность вводимых данных.

    """

    def ask(self):
        """
        Данный метод запрашивает у пользователя координаты выстрела,
        попутно делая проверки на корректность вводимых данных.

        :return: Dot(x, y) координаты выстрела.
        """

        while True:

            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords
            x = x.upper()

            # проверка: является ли x буквой, только одна буква, буква из латинского алфавита.
            if not x.isalpha() or len(x) > 1 or x not in L_R:
                print(" Первой координатой введите \n соответствующую латинскую букву! ")
                continue

            if not (y.isdigit()):
                print(" Второй координатой введите цифру! ")
                continue

            x = L_R.index(x)
            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    """
    Класс самой игры Крестики - Нолики.

    Attributes
    ----------
    size : int
        Размер игрового поля

    lens : list
        Список с размерами кораблей - длина в клетках.

    pl : Board
        Игровая доска - поле пользователя.

    co : Board
        Игровая доска - поле компьютера (AI).

    ai : Класс AI
        Игрок искусственный интеллект.

    pl : Класс User
        Игрок пользователь.

    Methods
    -------
    random_board()
        Создаёт случайную игровую доску.

    random_place()
        В цикле до 2000 раз пытается расставить корабли на игровой доске
        в случайном порядке, после 2000 неудачных попыток вызывает исключение.

    print_board()
        Метод служит для вывода в консоль игровых полей.

    greet()
        Приветственное сообщение игроку с объяснением правил
        ввода координат хода.

    loop()
        Игровой цикл.

    start()
        Метод запуска игры.

    """

    def __init__(self, size=10):
        """
        Устанавливает все необходимые атрибуты для объекта Game.

        :param size: int Размер игрового поля

        lens : list Список с размерами кораблей - длина в клетках.

        pl : Board Игровая доска - поле пользователя.

        co : Board Игровая доска - поле компьютера (AI).

        ai : Класс AI Игрок искусственный интеллект.

        pl : Класс User Игрок пользователь.

        """

        self.lens = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        """
        Создаёт игровую доску со случайным расположением кораблей.

        :return: Board возвращает случайную игровую доску.
        """

        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        """
        В цикле до 2000 раз пытается расставить корабли на игровой доске
        в случайном порядке, после 2000 неудачных попыток вызывает исключение.

        :return: Board С кораблями расставленными в случайном порядке.

        """

        board = Board(size=self.size)
        attempts = 0
        for len_ in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), len_, randint(0, 3))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def print_board(self):
        """
        Метод служит для вывода в консоль игровых полей.
        """

        pl = self.us.board.__str__().splitlines()
        ai = self.ai.board.__str__().splitlines()
        pl_inf = 'Доска пользователя:'
        ai_inf = 'Доска компьютера:'
        width = len(pl[0])
        pl.insert(0, pl_inf.ljust(width))
        ai.insert(0, ai_inf.ljust(width))
        print('-' * 95)
        for i in range(len(pl)):
            print(pl[i] + '    *    ' + ai[i])

    @staticmethod
    def greet():
        """
        Приветственное сообщение игроку с объяснением правил
        ввода координат хода.
        """

        print("|*****************************************|")
        print("|           Приветствуем Вас              |")
        print("|               в игре                    |")
        print("|             морской бой                 |")
        print("|-----------------------------------------|")
        print("|           формат ввода: x y             |")
        print("|        x - латинская буква строки       |")
        print("|        y - номер столбца                |")
        print("|*****************************************|")
        time.sleep(2)

    def loop(self):
        """
        Игровой цикл.
        """
        num = 0
        while True:
            self.print_board()

            if num % 2 == 0:
                print(set_color("Ходит пользователь!", Color.green))
                repeat = self.us.move()
            else:
                print(set_color("Ходит компьютер!", Color.blue))
                time.sleep(1)
                repeat = self.ai.move()
                time.sleep(1)
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_board()
                print(set_color("Пользователь выиграл!!!", Color.green))
                break

            if self.us.board.defeat():
                self.print_board()
                print(set_color("Компьютер выиграл!!!", Color.red_1))
                break
            num += 1

    def start(self):
        """
        Метод запуска игры.
        """
        self.greet()
        self.loop()


g = Game()
g.start()
