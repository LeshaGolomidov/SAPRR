from tkinter import *
from tkinter.messagebox import showwarning, showinfo
import json
from file_operations import save_project, open_project
from construction import ConstructionApp

class PreprocessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Препроцессор")

        # Очищаем JSON файлы rods.json и nodes.json при запуске
        self.clear_json_files()
        self.create_widgets()

    def clear_json_files(self):
        rods_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\preprocessor\\rods.json"
        nodes_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\preprocessor\\nodes.json"

        # Очищаем содержимое файлов
        try:
            with open(rods_path, 'w') as rods_file:
                json.dump({}, rods_file)
            with open(nodes_path, 'w') as nodes_file:
                json.dump({}, nodes_file)
        except Exception as e:
            showwarning("Ошибка", f"Не удалось очистить файлы JSON: {e}")

    def create_widgets(self):
        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.save_button = Button(self.main_frame, text="Сохранить", command=save_project)
        self.save_button.pack(fill=X, pady=5)

        self.load_button = Button(self.main_frame, text="Загрузить файл", command=open_project)
        self.load_button.pack(fill=X, pady=5)

        self.rod_params_button = Button(self.main_frame, text="Параметры стержней", command=self.open_rod_parameters)
        self.rod_params_button.pack(fill=X, pady=5)

        self.node_params_button = Button(self.main_frame, text="Параметры узлов", command=self.open_node_parameters)
        self.node_params_button.pack(fill=X, pady=5)

        self.draw_button = Button(self.main_frame, text="Отрисовка", command=self.open_construction)
        self.draw_button.pack(fill=X, pady=5)

        self.save_exit_button = Button(self.main_frame, text="Сохранить и выйти", command=self.save_and_exit)
        self.save_exit_button.pack(fill=X, pady=5)

    def open_rod_parameters(self):
        rod_window = Toplevel(self.root)
        from rod_parameters import RodParametersApp
        RodParametersApp(rod_window)

    def open_node_parameters(self):
        node_window = Toplevel(self.root)
        from node_parameters import NodeParametersApp
        NodeParametersApp(node_window)

    def open_construction(self):
        try:
            construction_window = Toplevel(self.root)
            ConstructionApp(construction_window)
        except Exception as e:
            showwarning("Ошибка", f"Не удалось отобразить конструкцию: {e}")

    def save_and_exit(self):
        rods_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\preprocessor\\rods.json"
        nodes_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\preprocessor\\nodes.json"
        data_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\processor\\data.json"

        try:
            with open(rods_path, 'r') as rods_file:
                rods_data = json.load(rods_file)

            with open(nodes_path, 'r') as nodes_file:
                nodes_data = json.load(nodes_file)

            kernel_data = {
                "Kernel": {
                    key: [
                        rod["L"], rod["A"], rod["E"], rod["\u03c3"]
                    ] for key, rod in rods_data.items()
                }
            }

            distributed_load = {
                "Distributed load": {
                    key: [int(key), rod["q"]] for key, rod in rods_data.items()
                }
            }

            concentrated_load = {
                "Concentrated load": {
                    key: [int(key), node["F"]] for key, node in nodes_data.items()
                }
            }

            support = {"Support": "from two sides"}  # Default support
            for key, node in nodes_data.items():
                if node.get("Fixation"):
                    if key == "1":
                        support["Support"] = "left"
                    elif key == str(len(nodes_data)):
                        support["Support"] = "right"
                    if nodes_data.get("1", {}).get("Fixation") and nodes_data.get(str(len(nodes_data)), {}).get("Fixation"):
                        support["Support"] = "from two sides"

            final_data = [kernel_data, concentrated_load, distributed_load, support]

            with open(data_path, 'w') as data_file:
                json.dump(final_data, data_file, indent=4)

            showinfo("Сохранение", "Данные успешно сохранены в data.json!")
        except Exception as e:
            showwarning("Ошибка", f"Не удалось сохранить данные: {e}")

        self.root.destroy()

    def draw(self):
        showwarning("Отрисовка", "Функция отрисовки будет реализована позже.")

if __name__ == "__main__":
    root = Tk()
    app = PreprocessorApp(root)
    root.mainloop()
