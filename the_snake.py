import random
import sys

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTR_X = GRID_WIDTH // 2 * GRID_SIZE
CENTR_Y = GRID_HEIGHT // 2 * GRID_SIZE
LINE_WIDTH = 1
START_POSITION = (CENTR_X, CENTR_Y)
# Цвета:
WHITE = (255, 255, 255)
PINK = (255, 192, 203)
PALE_VIOLET_RED = (219, 112, 147)
ORANGE_RED = (255, 69, 0)
FUCHSIA = (255, 0, 255)
DEEP_PINK = (255, 20, 147)
SADDLE_BROWN = (139, 69, 19)
DARK_SLATE_BLUE = (72, 61, 139)
# Цвета игры (оставила, чтобы было понятно,
# что хвост закрашивается цветами поля и сетки):
BOARD_BACKGROUND_COLOR = PINK
BORDER_COLOR = PALE_VIOLET_RED
APPLE_COLOR = ORANGE_RED
SNAKE_COLOR = FUCHSIA
SNAKE_BORDER_COLOR = DEEP_PINK
FRUIT_COLOR = SADDLE_BROWN
STONE_COLOR = DARK_SLATE_BLUE
# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
TURNS = {
    pg.K_UP: (UP, DOWN),
    pg.K_DOWN: (DOWN, UP),
    pg.K_LEFT: (LEFT, RIGHT),
    pg.K_RIGHT: (RIGHT, LEFT)
}

SPEED = 5


def draw_lines() -> None:
    """Отрисовать сетку поля."""
    for i in range(1, GRID_WIDTH):
        pg.draw.line(
            screen,
            BORDER_COLOR,
            (i * GRID_SIZE, 0),
            (i * GRID_SIZE, SCREEN_HEIGHT),
            LINE_WIDTH
        )
    for i in range(1, GRID_HEIGHT):
        pg.draw.line(
            screen,
            BORDER_COLOR,
            (0, i * GRID_SIZE),
            (SCREEN_WIDTH, i * GRID_SIZE),
            LINE_WIDTH
        )


def handle_keys(game_object) -> None:
    """Обработка нажатия клавиш."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            new_direction, opposite = TURNS.get(
                event.key, (game_object.direction, game_object.direction)
            )
            if game_object.direction != opposite:
                game_object.next_direction = new_direction


class GameObject:
    """
    Игровой объект.

    Содержит два метода-заглушки,
    которые будут переопределены в наследниках.
    """

    def __init__(self, position=START_POSITION, body_color=WHITE):
        """
        Инициализация нового игрового объекта.

        position: позиция объекта на поле, заданная x, y координатами.
        body_color: цвет объекта.
        """
        self.position = position
        self.body_color = body_color

    def draw(self):
        """
        Отрисовка объекта.

        Метод-заглушка для переопределения в наследниках.
        """
        raise NotImplementedError(
            f'Метод draw не определен в классе {self.__class__.__name__}'
        )

    def draw_cell(
            self,
            position,
            body_color=BOARD_BACKGROUND_COLOR,
            border_color=BORDER_COLOR,
            size=(GRID_SIZE, GRID_SIZE)
    ):
        """Отрисовка одной ячейки."""
        rect = (pg.Rect(position, size))
        pg.draw.rect(screen, body_color, rect)
        pg.draw.rect(screen, border_color, rect, LINE_WIDTH)


class Apple(GameObject):
    """
    Игровой объект - яблоко.

    Дочерний класс, наследуемый от GameObject.
    Переопределены методы draw() и reset().
    Новый метод: определение рандомной позиции объекта.
    Положительно влияет на рост змеи.
    """

    def __init__(self, body_color=ORANGE_RED, occupied=None):
        """Инициализация нового игрового объекта."""
        super().__init__(body_color=body_color)
        self.occupied = occupied if occupied is not None else []
        self.randomize_position(self.occupied)

    def draw(self):
        """Отрисовка объекта в форме круга."""
        radius = GRID_SIZE / 2
        x, y = self.position
        x_centr, y_centr = (x + radius), (y + radius)
        pg.draw.circle(screen, self.body_color, (x_centr, y_centr), radius)

    def randomize_position(self, occupied):
        """
        Определение позиции объекта на игровом поле.

        Позиция определяется рандомно, учитывается расположение другого
        объекта на поле для исключения перекрывания.

        snake: координаты другого игрового объекта.
        """
        while True:
            self.position = (
                random.randrange(0, SCREEN_WIDTH, GRID_SIZE),
                random.randrange(0, SCREEN_HEIGHT, GRID_SIZE)
            )
            if self.position not in occupied:
                break


class InedibleFruit(Apple):
    """
    Игровой объект - несъедобный фрукт.

    Дочерний класс, наследуемый от Apple.
    Уменьшает длину змеи при контакте.
    """

    def __init__(self, body_color=SADDLE_BROWN, occupied=None):
        """Инициализация нового игрового объекта."""
        super().__init__(body_color=body_color, occupied=occupied)
        self.randomize_position(self.occupied)


class Stone(Apple):
    """
    Игровой объект - каменная стена.

    Дочерний класс, наследуемый от Apple.
    При контакте со змеёй возвращает её к стартовым позициям.
    """

    def __init__(self, body_color=DARK_SLATE_BLUE, occupied=None):
        """Инициализация нового игрового объекта."""
        super().__init__(body_color=body_color, occupied=occupied)
        self.randomize_position(self.occupied)

    def draw(self):
        """Отрисовка объекта в форме прямоугольника."""
        self.draw_cell(
            self.position[0],
            self.body_color,
            BORDER_COLOR,
            self.size
        )

    def randomize_position(self, occupied):
        """
        Определение позиции объекта на игровом поле.

        Позиция определяется рандомно, учитывается расположение другого
        объекта на поле для исключения перекрывания.

        snake: координаты другого игрового объекта (змеи).
        apple: координаты съедобного для змеи объекта(яблока).
        fruit: координаты несъедобного для змеи объекта(фрукта).
        """
        while True:
            size = random.choice([
                (GRID_SIZE * 2, GRID_SIZE),
                (GRID_SIZE, GRID_SIZE * 2)
            ])
            position = (
                random.randrange(0, (SCREEN_WIDTH - GRID_SIZE), GRID_SIZE),
                random.randrange(0, (SCREEN_HEIGHT - GRID_SIZE), GRID_SIZE)
            )
            result = [
                position, tuple(
                    [(x + y - GRID_SIZE) for x, y in zip(position, size)]
                )
            ]
            if all(cell not in occupied for cell in result):
                self.position, self.size = result, size
                break


class Snake(GameObject):
    """
    Игровой объект - змея.

    Дочерний класс, наследуемый от GameObject.
    Переопределены методы draw() и reset().
    Новые методы: определение позиции головы объекта,
    движение объекта, обновление направления движения.
    """

    def __init__(self, body_color=FUCHSIA, border_color=DEEP_PINK):
        """
        Инициализация нового игрового объекта - змеи.

        positions: позиции сегментов объекта на поле,
        заданные x, y координатами,
        body_color: цвет объекта,
        length: длина змеи,
        direction: направление движения змеи,
        next_direction: новое направление движения змеи,
        last: координаты последнего сегмента.
        """
        super().__init__(body_color=body_color)
        self.border_color = border_color
        self.reset()

    def get_head_position(self):
        """Определение координат головы змеи."""
        return self.positions[0]

    def reset(self):
        """Сброс змеи до стартовых значений."""
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.positions = [self.position]
        self.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)
        draw_lines()

    def move(self):
        """
        Движение змеи по игровому полю.

        Учитывает столкновение змеи со своим телом и
        сбрасывает её до стартовых значений.
        Корректирует координаты сегментов змеи.
        """
        self.last = None
        x_head_position, y_head_position = self.get_head_position()
        x, y = self.direction
        new_head_position = (
            ((x_head_position + (x * GRID_SIZE)) % SCREEN_WIDTH),
            ((y_head_position + (y * GRID_SIZE)) % SCREEN_HEIGHT)
        )
        self.positions.insert(0, new_head_position)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def update_direction(self):
        """Обновление направления движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """
        Отрисовка сегментов змеи.

        Затирание хвоста для создания видимости движения змеи.
        """
        for position in self.positions[1:]:
            self.draw_cell(position, self.body_color, self.border_color)

        self.draw_cell(
            self.get_head_position(), self.body_color, self.border_color
        )

        if self.last:
            self.draw_cell(self.last)


def changing(snake, apple, fruit, stones):
    """
    Смена позиций у игровых объектов:

    яблока, несъедобного фрукта, препятствия.
    """
    apple.draw_cell(apple.position)
    fruit.draw_cell(fruit.position)
    for stone in stones:
        stone.draw_cell(stone.position[0])
        stone.draw_cell(stone.position[1])
    apple.randomize_position(snake.positions)
    fruit.randomize_position([*snake.positions, apple.position])
    for stone in stones:
        stone.randomize_position(
            [*snake.positions, apple.position, fruit.position]
        )


def eating(snake, apple, fruit, stones) -> None:
    """
    Реализация поедания съедобного или несъедобного фрукта.

    При поедании съедобного яблока - длина змеи увеличивается на 1 сегмент.
    При поедании несъедобного фрукта - длина змеи уменьшается на 1 сегмент.
    Если змея состоит из 1 сегмента, то при поедании несъедобного фрукта
    змея сбрасывается до стартовых позиций.

    """
    head = snake.get_head_position()
    if head == apple.position:
        snake.length += 1
        changing(snake, apple, fruit, stones)
    elif head == fruit.position:
        if snake.length > 1:
            snake.length -= 1
            snake.draw_cell(snake.positions[-1])
            snake.positions.pop()
            changing(snake, apple, fruit, stones)
        else:
            changing(snake, apple, fruit, stones)
            snake.reset()


def is_clashing(snake, apple, fruit, stones):
    """
    Проверка столкновения змеи.

    После столкновения змея возвращается в стартовую точку,
    обновляются позиции всех игровых объектов.
    """
    if snake.get_head_position() in snake.positions[1:]:
        changing(snake, apple, fruit, stones)
        snake.reset()
    for stone in stones:
        if snake.get_head_position() in stone.position:
            snake.reset()
            changing(snake, apple, fruit, stones)


screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
clock = pg.time.Clock()


def main():
    """
    Основа игры.

    Инициализация pygame и создание объектов.
    Основной цикл игры: логика и отрисовка элементов.
    """
    pg.init()
    pg.display.set_caption('Змейка')
    snake = Snake()
    apple = Apple(occupied=snake.positions)
    fruit = InedibleFruit(occupied=[*snake.positions, apple.position])
    stones = [Stone(
        occupied=[*snake.positions, apple.position, fruit.position]
    ) for _ in range(4)]
    screen.fill(BOARD_BACKGROUND_COLOR)
    draw_lines()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        is_clashing(snake, apple, fruit, stones)
        eating(snake, apple, fruit, stones)
        snake.draw()
        apple.draw()
        fruit.draw()
        for stone in stones:
            stone.draw()
        pg.display.update()

    pg.quit()


if __name__ == '__main__':
    main()
