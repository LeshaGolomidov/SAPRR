from tkinter import *
from tkinter.ttk import Treeview
from tkinter.messagebox import showerror, showinfo
from tkinter.simpledialog import askstring
import json

class NodeParametersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Параметры узлов")
        self.nodes_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\preprocessor\\nodes.json"
        self.data_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\processor\\data.json"
        self.nodes_data = self.load_nodes()
        self.support = ""  # Заделка по умолчанию

        self.create_widgets()

    def load_nodes(self):
        try:
            with open(self.nodes_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            showerror("Ошибка", "Файл nodes.json поврежден. Он будет перезаписан.")
            self.save_nodes({})
            return {}

    def save_nodes(self, data):
        try:
            with open(self.nodes_path, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def save_support_and_forces(self):
        forces = {str(i): [i, node["F"]] for i, node in self.nodes_data.items()}
        output_data = {
            "Concentrated load": forces,
            "Support": self.support
        }
        try:
            with open(self.data_path, 'w') as file:
                json.dump(output_data, file, indent=4)
            showinfo("Сохранение", "Данные успешно сохранены!")
        except Exception as e:
            showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def create_widgets(self):
        self.table_frame = Frame(self.root)
        self.table_frame.pack(fill=BOTH, expand=True)

        self.columns = ('№ узла', 'F', 'Заделка')
        self.tree = Treeview(self.table_frame, columns=self.columns, show='headings', height=10)

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=CENTER, width=100)

        self.tree.pack(fill=BOTH, expand=True)
        self.populate_table()

        self.button_frame = Frame(self.root)
        self.button_frame.pack(fill=X)

        self.add_fixation_button = Button(self.button_frame, text="Настроить заделки", command=self.configure_support)
        self.add_fixation_button.pack(side=LEFT, padx=5, pady=5)

        self.edit_force_button = Button(self.button_frame, text="Редактировать F", command=self.edit_force)
        self.edit_force_button.pack(side=LEFT, padx=5, pady=5)

        self.save_button = Button(self.button_frame, text="Сохранить и выйти", command=self.save_and_exit)
        self.save_button.pack(side=LEFT, padx=5, pady=5)

    def populate_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for node_id, node_data in self.nodes_data.items():
            self.tree.insert('', 'end', iid=node_id, values=(node_id, node_data['F'], "Да" if node_data['Fixation'] else "Нет"))

    def configure_support(self):
        support_window = Toplevel(self.root)
        support_window.title("Настройка заделок")

        left_var = BooleanVar()
        right_var = BooleanVar()

        Checkbutton(support_window, text="Левая заделка", variable=left_var).pack(anchor=W, padx=10, pady=5)
        Checkbutton(support_window, text="Правая заделка", variable=right_var).pack(anchor=W, padx=10, pady=5)

        def save_support():
            # Обновляем заделки в nodes.json
            if left_var.get():
                self.nodes_data["1"]["Fixation"] = True
            else:
                self.nodes_data["1"]["Fixation"] = False

            last_node = str(len(self.nodes_data))
            if right_var.get():
                self.nodes_data[last_node]["Fixation"] = True
            else:
                self.nodes_data[last_node]["Fixation"] = False

            # Обновляем self.support для data.json
            if left_var.get() and right_var.get():
                self.support = "from two sides"
            elif left_var.get():
                self.support = "left"
            elif right_var.get():
                self.support = "right"
            else:
                self.support = ""

            # Сохраняем изменения
            self.save_nodes(self.nodes_data)
            self.populate_table()
            showinfo("Сохранение заделок", f"Текущая заделка: {self.support}")
            support_window.destroy()

        Button(support_window, text="Сохранить", command=save_support).pack(pady=10)

    def edit_force(self):
        selected_item = self.tree.selection()
        if not selected_item:
            showerror("Ошибка", "Выберите узел для редактирования F.")
            return

        node_id = selected_item[0]
        try:
            node_data = self.nodes_data[node_id]
            node_data["F"] = float(self.prompt_value("Введите значение силы (F):", node_data["F"]))
            self.nodes_data[node_id] = node_data
            self.save_nodes(self.nodes_data)
            self.populate_table()
        except ValueError:
            showerror("Ошибка", "Введены некорректные данные.")
        except Exception as e:
            showerror("Ошибка", f"Не удалось редактировать узел: {e}")

    def save_and_exit(self):
        self.save_support_and_forces()
        self.root.destroy()

    def prompt_value(self, prompt, default):
        result = askstring("Редактирование", f"{prompt} (текущее значение: {default}):")
        return result if result else default

if __name__ == "__main__":
    root = Tk()
    app = NodeParametersApp(root)
    root.mainloop()
