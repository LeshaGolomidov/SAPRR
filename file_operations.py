import json
from tkinter import filedialog, messagebox

def save_project():
    try:
        # Чтение данных из rods.json и nodes.json
        rods_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\preprocessor\\rods.json"
        nodes_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\preprocessor\\nodes.json"

        with open(rods_path, 'r') as rods_file:
            rods_data = json.load(rods_file)

        with open(nodes_path, 'r') as nodes_file:
            nodes_data = json.load(nodes_file)

        # Сохранение в единый файл
        combined_data = {
            "rods": rods_data,
            "nodes": nodes_data
        }

        save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Сохранить проект"
        )

        if save_path:
            with open(save_path, 'w') as save_file:
                json.dump(combined_data, save_file, indent=4)
            messagebox.showinfo("Успех", "Проект успешно сохранён!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить проект: {e}")

def open_project():
    try:
        # Открытие файла проекта
        open_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            title="Открыть проект"
        )

        if open_path:
            with open(open_path, 'r') as open_file:
                combined_data = json.load(open_file)

            # Запись данных обратно в rods.json и nodes.json
            rods_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\preprocessor\\rods.json"
            nodes_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\preprocessor\\nodes.json"

            with open(rods_path, 'w') as rods_file:
                json.dump(combined_data.get("rods", {}), rods_file, indent=4)

            with open(nodes_path, 'w') as nodes_file:
                json.dump(combined_data.get("nodes", {}), nodes_file, indent=4)

            messagebox.showinfo("Успех", "Проект успешно открыт и данные загружены!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть проект: {e}")
