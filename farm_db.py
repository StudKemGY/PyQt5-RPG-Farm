import sqlite3
from pathlib import Path

# Файл базы данных будет создан автоматически в папке проекта
DB_PATH = str(Path(__file__).parent.absolute() / "rpg_farm.db")

class FarmRPG_DB:
    """Управление базой данных игры (2 связанные таблицы по ТЗ)."""
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.init_world()

    def create_tables(self):
        """Создает таблицы для характеристик игрока и карты мира."""
        # Таблица 1: Характеристики фермера и его координаты (X, Y)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_hero (
                id INTEGER PRIMARY KEY,
                money INTEGER,
                energy INTEGER,
                day INTEGER,
                pos_x INTEGER,
                pos_y INTEGER
            )
        """)
        # Таблица 2: Карта мира (100 ячеек для сетки 10х10)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS world_map (
                cell_id INTEGER PRIMARY KEY,
                tile_type TEXT,
                growth_stage INTEGER,
                watered INTEGER
            )
        """)
        self.conn.commit()

    def init_world(self):
        """Генерирует начальный мир, если база данных пустая."""
        self.cursor.execute("SELECT COUNT(*) FROM player_hero")
        if self.cursor.fetchone()[0] == 0:
            # Стартовые параметры: 100 монет, 100 энергии, День 1, координаты игрока (5, 5)
            self.cursor.execute("INSERT INTO player_hero VALUES (1, 100, 100, 1, 5, 5)")
            
            # Заполняем карту 10х10 (всего 100 ячеек) статическими зонами
            for row in range(10):
                for col in range(10):
                    cell_id = row * 10 + col
                    tile = "Трава"
                    
                    # Расставляем кубики объектов по координатам
                    if row == 2 and col == 2:
                        tile = "Дом"
                    elif row == 2 and col == 7:
                        tile = "Магазин"
                    elif row == 7 and col == 4:
                        tile = "Загон"
                    elif (row == 5 or row == 6) and (col == 2 or col == 3):
                        tile = "Грядка_Пустая"
                    
                    self.cursor.execute("INSERT INTO world_map VALUES (?, ?, 0, 0)", (cell_id, tile))
            self.conn.commit()

    def get_hero(self):
        """Возвращает параметры игрока из первой таблицы."""
        self.cursor.execute("SELECT money, energy, day, pos_x, pos_y FROM player_hero WHERE id = 1")
        return self.cursor.fetchone()

    def save_hero(self, money, energy, day, x, y):
        """Сохраняет параметры игрока."""
        self.cursor.execute("UPDATE player_hero SET money=?, energy=?, day=?, pos_x=?, pos_y=? WHERE id = 1",
                            (money, energy, day, x, y))
        self.conn.commit()

    def get_map(self):
        """Возвращает данные о всех ячейках карты из второй таблицы."""
        self.cursor.execute("SELECT cell_id, tile_type, growth_stage, watered FROM world_map")
        return self.cursor.fetchall()

    def update_tile(self, cell_id, tile_type, stage, watered):
        """Обновляет состояние конкретной ячейки карты (Изменение)."""
        self.cursor.execute("UPDATE world_map SET tile_type=?, growth_stage=?, watered=? WHERE cell_id=?",
                            (tile_type, stage, watered, cell_id))
        self.conn.commit()

    def close(self):
        """Закрывает соединение с БД."""
        self.conn.close()
