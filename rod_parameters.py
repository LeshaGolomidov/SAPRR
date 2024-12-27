from tkinter import *
from tkinter.ttk import Treeview
from tkinter.messagebox import showerror, showinfo
import json

class RodParametersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Параметры стержней")
        self.rods_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\preprocessor\\rods.json"
        self.nodes_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\preprocessor\\nodes.json"
        self.data_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\processor\\data.json"
        self.rods_data = self.load_rods()

        self.create_widgets()

    def load_rods(self):
        try:
            with open(self.rods_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            showerror("Ошибка", "Файл rods.json поврежден. Он будет перезаписан.")
            self.save_rods({})
            return {}

    def save_rods(self, data):
        try:
            with open(self.rods_path, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def save_data_json(self):
        kernel = {}
        distributed_load = {}

        for rod_id, rod_data in self.rods_data.items():
            kernel[rod_id] = [
                rod_data["L"],
                rod_data["A"],
                rod_data["E"],
                rod_data["\u03c3"]
            ]
            if rod_data["q"] != 0.0:
                distributed_load[rod_id] = [int(rod_id), rod_data["q"]]

        output_data = [
            {"Kernel": kernel},
            {"Distributed load": distributed_load}
        ]

        try:
            with open(self.data_path, 'w') as file:
                json.dump(output_data, file, indent=4)
            showinfo("Сохранение", "Данные успешно сохранены в data.json!")
        except Exception as e:
            showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def update_nodes(self):
        try:
            nodes_count = len(self.rods_data) + 1
            nodes_data = {str(i): {"F": 0, "Fixation": False} for i in range(1, nodes_count + 1)}
            with open(self.nodes_path, 'w') as file:
                json.dump(nodes_data, file, indent=4)
        except Exception as e:
            showerror("Ошибка", f"Не удалось обновить узлы: {e}")

    def create_widgets(self):
        self.table_frame = Frame(self.root)
        self.table_frame.pack(fill=BOTH, expand=True)

        self.columns = ('№ стержня', 'L', 'A', 'E', 'σ', 'q')
        self.tree = Treeview(self.table_frame, columns=self.columns, show='headings', height=10)

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=CENTER, width=100)

        self.tree.pack(fill=BOTH, expand=True)
        self.populate_table()

        self.button_frame = Frame(self.root)
        self.button_frame.pack(fill=X)

        self.add_button = Button(self.button_frame, text="Добавить стержень", command=self.add_rod)
        self.add_button.pack(side=LEFT, padx=5, pady=5)

        self.edit_button = Button(self.button_frame, text="Редактировать стержень", command=self.edit_rod)
        self.edit_button.pack(side=LEFT, padx=5, pady=5)

        self.delete_button = Button(self.button_frame, text="Удалить стержень", command=self.delete_rod)
        self.delete_button.pack(side=LEFT, padx=5, pady=5)

        self.save_button = Button(self.button_frame, text="Сохранить и выйти", command=self.save_and_exit)
        self.save_button.pack(side=LEFT, padx=5, pady=5)

    def populate_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for rod_id, rod_data in self.rods_data.items():
            self.tree.insert('', 'end', iid=rod_id, values=(rod_id, rod_data['L'], rod_data['A'], rod_data['E'], rod_data['σ'], rod_data['q']))

    def add_rod(self):
        try:
            rod_id = str(len(self.rods_data) + 1)
            new_rod = {
                "L": 0,
                "A": 0,
                "E": 0,
                "σ": 0,
                "q": 0
            }
            self.rods_data[rod_id] = new_rod
            self.save_rods(self.rods_data)
            self.populate_table()
        except Exception as e:
            showerror("Ошибка", f"Не удалось добавить стержень: {e}")

    def edit_rod(self):
        selected_item = self.tree.selection()
        if not selected_item:
            showerror("Ошибка", "Выберите стержень для редактирования.")
            return

        rod_id = selected_item[0]
        try:
            rod_data = self.rods_data[rod_id]
            rod_data["L"] = float(self.prompt_value("Введите длину (L):", rod_data["L"]))
            rod_data["A"] = float(self.prompt_value("Введите площадь (A):", rod_data["A"]))
            rod_data["E"] = float(self.prompt_value("Введите модуль упругости (E):", rod_data["E"]))
            rod_data["σ"] = float(self.prompt_value("Введите напряжение (σ):", rod_data["σ"]))
            rod_data["q"] = float(self.prompt_value("Введите нагрузку (q):", rod_data["q"]))
            self.rods_data[rod_id] = rod_data
            self.save_rods(self.rods_data)
            self.populate_table()
        except ValueError:
            showerror("Ошибка", "Введены некорректные данные.")
        except Exception as e:
            showerror("Ошибка", f"Не удалось редактировать стержень: {e}")

    def delete_rod(self):
        selected_item = self.tree.selection()
        if not selected_item:
            showerror("Ошибка", "Выберите стержень для удаления.")
            return

        rod_id = selected_item[0]
        try:
            del self.rods_data[rod_id]
            self.save_rods(self.rods_data)
            self.populate_table()
        except Exception as e:
            showerror("Ошибка", f"Не удалось удалить стержень: {e}")

    def save_and_exit(self):
        self.update_nodes()
        self.save_data_json()
        self.root.destroy()

    def prompt_value(self, prompt, default):
        from tkinter.simpledialog import askstring
        result = askstring("Редактирование", f"{prompt} (текущее значение: {default}):")
        return result if result else default

if __name__ == "__main__":
    root = Tk()
    app = RodParametersApp(root)
    root.mainloop()
