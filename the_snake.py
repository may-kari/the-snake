import pygame
import random


# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTR_X = GRID_WIDTH // 2 * GRID_SIZE
CENTR_Y = GRID_HEIGHT // 2 * GRID_SIZE
LINE_WIDTH = 1
# Цвета:
BOARD_BACKGROUND_COLOR = (255, 192, 203)
BORDER_COLOR = (219, 112, 147)
APPLE_COLOR = (255, 69, 0)
SNAKE_COLOR = (255, 0, 255)
SNAKE_BORDER_COLOR = (255, 20, 147)
FRUIT_COLOR = (139, 69, 19)
STONE_COLOR = (72, 61, 139)
# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

SPEED = 5


def draw_lines() -> None:
    """Отрисовать сетку поля."""
    for i in range(1, GRID_WIDTH):
        pygame.draw.line(
            screen,
            BORDER_COLOR,
            (i * GRID_SIZE, 0),
            (i * GRID_SIZE, SCREEN_HEIGHT),
            LINE_WIDTH
        )
    for i in range(1, GRID_HEIGHT):
        pygame.draw.line(
            screen,
            BORDER_COLOR,
            (0, i * GRID_SIZE),
            (SCREEN_WIDTH, i * GRID_SIZE),
            LINE_WIDTH
        )


def handle_keys(game_object) -> None:
    """
    Обработка нажатия клавиш,
    сопоставление с направлением движения.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


class GameObject:
    """
    Игровой объект.

    Содержит два метода-заглушки,
    которые будут переопределены в наследниках.
    """

    def __init__(self):
        """
        Инициализация нового игрового объекта.

        position: позиция объекта на поле, заданная x, y координатами.
        body_color: цвет объекта.
        """
        self.position = CENTR_X, CENTR_Y
        self.body_color = None

    def draw(self):
        """
        Отрисовка объекта.

        Метод-заглушка для переопределения в наследниках.
        """
        pass

    def reset(self):
        """
        Удаление объекта.

        Метод-заглушка для переопределения в наследниках.
        """
        pass


class Apple(GameObject):
    """
    Игровой объект - яблоко.

    Дочерний класс, наследуемый от GameObject.
    Переопределены методы draw() и reset().
    Новый метод: определение рандомной позиции объекта.
    Положительно влияет на рост змеи.
    """

    def __init__(self):
        """Инициализация нового игрового объекта."""
        self.body_color = APPLE_COLOR
        self.position = self.randomize_position()

    def draw(self):
        """Отрисовка объекта в форме круга."""
        radius = GRID_SIZE / 2
        x, y = self.position
        x_centr, y_centr = (x + radius), (y + radius)
        pygame.draw.circle(screen, self.body_color, (x_centr, y_centr), radius)

    def randomize_position(self, snake=()):
        """
        Определение позиции объекта на игровом поле.

        Позиция определяется рандомно, учитывается расположение другого
        объекта на поле для исключения перекрывания.

        snake: координаты другого игрового объекта.
        """
        while True:
            position = (
                random.randrange(0, SCREEN_WIDTH, GRID_SIZE),
                random.randrange(0, SCREEN_HEIGHT, GRID_SIZE)
            )
            if position not in snake:
                return position

    def reset(self, snake=()):
        """
        Перерисовка объекта.

        Определение новой позиции на поле.
        """
        self.position = self.randomize_position(snake)


class InedibleFruit(GameObject):
    """
    Игровой объект - несъедобный фрукт.

    Дочерний класс, наследуемый от GameObject.
    Переопределены методы draw() и reset().
    Новый метод: определение рандомной позиции объекта.
    Уменьшает длину змеи при контакте.
    """

    def __init__(self):
        """Инициализация нового игрового объекта."""
        self.body_color = FRUIT_COLOR
        self.position = self.randomize_position()

    def draw(self):
        """Отрисовка объекта в форме круга."""
        radius = GRID_SIZE / 2
        x, y = self.position
        x_centr, y_centr = (x + radius), (y + radius)
        pygame.draw.circle(screen, self.body_color, (x_centr, y_centr), radius)

    def randomize_position(self, snake=(), apple=()):
        """
        Определение позиции объекта на игровом поле.

        Позиция определяется рандомно, учитывается расположение другого
        объекта на поле для исключения перекрывания.

        snake: координаты другого игрового объекта (змеи).
        apple: координаты съедобного для змеи объекта(яблока).
        """
        while True:
            position = (
                random.randrange(0, SCREEN_WIDTH, GRID_SIZE),
                random.randrange(0, SCREEN_HEIGHT, GRID_SIZE)
            )
            if position not in snake and position != apple:
                return position

    def reset(self, snake=(), apple=()):
        """
        Перерисовка объекта.

        Определение новой позиции на поле.
        """
        self.position = self.randomize_position(snake, apple)


class Stone(GameObject):
    """
    Игровой объект - каменная стена.

    Дочерний класс, наследуемый от GameObject.
    Переопределены методы draw() и reset().
    Новый метод: определение рандомной позиции объекта.
    При контакте со змеёй возвращает её к стартовым позициям.
    """

    def __init__(self):
        """Инициализация нового игрового объекта."""
        self.body_color = STONE_COLOR
        self.position, self.size = self.randomize_position()

    def draw(self):
        """Отрисовка объекта в форме прямоугольника в разных направлениях."""
        rect = (pygame.Rect(self.position[0], self.size))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self, snake=(), apple=(), fruit=()):
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
            if apple not in result and fruit not in result:
                if position not in snake and result[1] not in snake:
                    return result, size

    def reset(self, snake=(), apple=(), fruit=()):
        """
        Перерисовка объекта.

        Определение новой позиции на поле.
        """
        self.position, self.size = self.randomize_position(snake, apple, fruit)


class Snake(GameObject):
    """
    Игровой объект - змея.

    Дочерний класс, наследуемый от GameObject.
    Переопределены методы draw() и reset().
    Новые методы: определение позиции головы объекта,
    движение объекта, обновление направления движения.
    """

    def __init__(self):
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
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.length = 1
        self.positions = [(CENTR_X, CENTR_Y)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Определение координат головы змеи."""
        return self.positions[0]

    def reset(self):
        """Сброс змеи до стартовых значений."""
        self.length = 1
        self.direction = RIGHT
        self.positions = [(CENTR_X, CENTR_Y)]
        self.last = None

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
        if new_head_position in self.positions:
            self.reset()
            return True
        else:
            self.positions.insert(0, new_head_position)
            while len(self.positions) > self.length:
                self.last = self.positions.pop()
            return False

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
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, SNAKE_BORDER_COLOR, rect, LINE_WIDTH)

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, SNAKE_BORDER_COLOR, head_rect, LINE_WIDTH)

        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
            pygame.draw.rect(screen, BORDER_COLOR, last_rect, LINE_WIDTH)


def changing(snake, apple, fruit, stones):
    """
    Смена позиций у игровых объектов:

    яблока, несъедобного фрукта, препятствия.
    """
    apple.reset(snake.positions)
    fruit.reset(snake.positions, apple.position)
    for stone in stones:
        stone.reset(snake.positions, apple.position, fruit.position)


def eating(snake, apple, fruit, stones) -> None:
    """
    Реализация поедания съедобного или несъедобного фрукта.

    При поедании съедобного яблока - длина змеи увеличивается на 1 сегмент.
    При поедании несъедобного фрукта - длина змеи уменьшается на 1 сегмент.
    Если змея состоит из 1 сегмента, то при поедании несъедобного фрукта
    змея сбрасывается до стартовых позиций.

    """
    if snake.positions[0] == apple.position:
        snake.length += 1
        changing(snake, apple, fruit, stones)
    elif snake.positions[0] == fruit.position:
        if snake.length > 1:
            snake.length -= 1
            changing(snake, apple, fruit, stones)
        else:
            changing(snake, apple, fruit, stones)
            snake.reset()


def is_clashing(snake, apple, fruit, stones):
    """
    Проверка столкновения змеи с препятствием.

    После столкновения змея возвращается в стартовую точку,
    обновляются позиции всех игровых объектов.
    """
    for stone in stones:
        if snake.positions[0] in stone.position:
            snake.reset()
            changing(snake, apple, fruit, stones)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
clock = pygame.time.Clock()


def main():
    """
    Основа игры.

    Инициализация pygame и создание объектов.
    Основной цикл игры: логика и отрисовка элементов.
    """
    pygame.init()
    pygame.display.set_caption('Змейка')
    snake = Snake()
    apple = Apple()
    fruit = InedibleFruit()
    stones = [Stone() for _ in range(0, 4)]

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        if snake.move():
            changing(snake, apple, fruit, stones)
        is_clashing(snake, apple, fruit, stones)
        eating(snake, apple, fruit, stones)
        screen.fill(BOARD_BACKGROUND_COLOR)
        draw_lines()
        snake.draw()
        apple.draw()
        fruit.draw()
        for stone in stones:
            stone.draw()
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
