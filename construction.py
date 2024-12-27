from tkinter import *
from tkinter.messagebox import showerror
import json
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow, Circle, Rectangle

class ConstructionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Отрисовка конструкции")
        self.rods_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\preprocessor\\rods.json"
        self.nodes_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\preprocessor\\nodes.json"

        self.rods_data = self.load_json(self.rods_path)
        self.nodes_data = self.load_json(self.nodes_path)

        self.create_widgets()

    def load_json(self, path):
        try:
            with open(path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            showerror("Ошибка", f"Файл {path} не найден.")
            return {}
        except json.JSONDecodeError:
            showerror("Ошибка", f"Файл {path} повреждён.")
            return {}

    def create_widgets(self):
        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.draw_button = Button(self.main_frame, text="Показать конструкцию", command=self.draw_construction)
        self.draw_button.pack(fill=X, pady=5)

        self.exit_button = Button(self.main_frame, text="Закрыть", command=self.root.destroy)
        self.exit_button.pack(fill=X, pady=5)

    def draw_construction(self):
        if not self.rods_data or not self.nodes_data:
            showerror("Ошибка", "Нет данных для отрисовки.")
            return

        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.axis('off')

            # Найти максимальное значение A для правильного расположения элементов
            max_A = max(rod['A'] for rod in self.rods_data.values())
            max_offset = max_A * 0.3 + 0.3  # Дополнительное смещение для номеров стержней

            # Отрисовка стержней
            for rod_id, rod_data in self.rods_data.items():
                node_start = int(rod_id)
                node_end = node_start + 1

                if str(node_start) in self.nodes_data and str(node_end) in self.nodes_data:
                    x1, x2 = node_start, node_end
                    A = rod_data['A']
                    L = rod_data['L']
                    E = rod_data['E']
                    height = A * 0.1  # Пропорциональная высота стержня

                    # Отрисовка стержня (две линии)
                    ax.plot([x1, x2], [height / 2, height / 2], 'k-', lw=2)  # Верхняя линия
                    ax.plot([x1, x2], [-height / 2, -height / 2], 'k-', lw=2)  # Нижняя линия

                    # Номер стержня в маленьком кружке
                    circle = Circle(((x1 + x2) / 2, max_offset / 3), 0.1, edgecolor='black', facecolor='none', lw=1.5)
                    ax.add_patch(circle)
                    ax.text((x1 + x2) / 2, max_offset / 3, f"{rod_id}", ha='center', va='center', fontsize=8)

                    # Параметры E и A над стержнем
                    ax.text((x1 + x2) / 2, max_offset / 3 + 0.2, f"E={E}, A={A}", ha='center', va='center', fontsize=8, color='blue')

                    # Длина стержня
                    length_y = -0.3 - max_A * 0.1  # Координата длины ниже квадратов узлов
                    ax.text((x1 + x2) / 2, length_y, f"{L}L", ha='center', va='center', fontsize=8, color='green')

                    # Распределённая нагрузка q
                    q = rod_data['q']
                    if q != 0:
                        self.draw_q_force(ax, x1, x2, q)

            # Отрисовка узлов
            for node_id, node_data in self.nodes_data.items():
                x = int(node_id)

                # Узел в виде вертикальной линии
                ax.plot([x, x], [-0.3, 0.3], 'k-', lw=2)

                # Номер узла в квадрате
                square_y = -0.3 - max_A * 0.1  # Динамическое расположение квадратов ниже стержней
                square = Rectangle((x - 0.15, square_y - 0.2), 0.3, 0.3, edgecolor='black', facecolor='white', lw=1.5)
                ax.add_patch(square)
                ax.text(x, square_y - 0.05, f"{node_id}", ha='center', va='center', fontsize=8)

                # Заземление, если Fixation = True
                if node_data['Fixation']:
                    self.draw_block(ax, x, -0.3, 0.3, is_first=(node_id == "1"))

                # Сосредоточенная сила F
                F = node_data['F']
                if F != 0:
                    direction = 0.4 if F > 0 else -0.4
                    arrow = FancyArrow(x, 0, direction, 0, width=0.02, head_width=0.08, color='red')
                    ax.add_patch(arrow)
                    ax.text(x + (0.5 if F > 0 else -0.5), 0.1, f"{abs(F)}F", color='red', fontsize=10, va='center')

            plt.show()

        except Exception as e:
            showerror("Ошибка", f"Не удалось отобразить конструкцию: {e}")

    def draw_block(self, ax, x, start, end, is_first):
        for current_y in range(int(start * 100), int(end * 100), 5):
            if is_first:
                ax.plot([x, x - 0.05], [current_y / 100, (current_y + 5) / 100], 'k-', lw=1)
            else:
                ax.plot([x, x + 0.05], [current_y / 100, (current_y + 5) / 100], 'k-', lw=1)

    def draw_q_force(self, ax, x1, x2, q):
        y_pos = 0  # Линия q совпадает с линией сил F

        # Рисуем линию q
        ax.plot([x1, x2], [y_pos, y_pos], 'blue', lw=1)

        # Добавляем стрелки вдоль линии q, убираем первую стрелку
        step = (x2 - x1) / 10  # Шаг между стрелками (пропорционально длине стержня)
        current_x = x1 + step  # Начинаем со второй стрелки
        while current_x + step / 2 <= x2:  # Последняя стрелка не выходит за пределы x2
            if q > 0:
                ax.arrow(current_x, y_pos, step / 3, 0, head_width=0.05, head_length=0.1, fc='blue', ec='blue')
            else:
                ax.arrow(current_x + step / 3, y_pos, -step / 3, 0, head_width=0.05, head_length=0.1, fc='blue', ec='blue')
            current_x += step

        # Указатель значения q
        mid_x = (x1 + x2) / 2
        ax.text(mid_x, y_pos - 0.1, f"{q}q", color='blue', fontsize=10, va='center', ha='center')

if __name__ == "__main__":
    root = Tk()
    ConstructionApp(root)
    root.mainloop()
