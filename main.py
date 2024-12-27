import json
import tkinter as tk
from tkinter.messagebox import showwarning, showinfo
from preprocessor import PreprocessorApp
from postprocessor import PostProcessorApp
from processor import calculate_and_save_results


class ProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Процессор")
        self.label = tk.Label(root, text="Процессор выполняет расчеты")
        self.label.pack()

        self.run_button = tk.Button(root, text="Запустить расчет", command=self.run_processor)
        self.run_button.pack()

        self.status_label = tk.Label(root, text="Статус: ожидание")
        self.status_label.pack()

        self.calculated = False

    def run_processor(self):
        try:
            with open(r"C:\Users\agolo\OneDrive\Рабочий стол\САПР\processor\data.json", "r") as file:
                data = json.load(file)

            # Передаем данные в процессор
            calculate_and_save_results(data)

            self.calculated = True
            self.status_label.config(text="Статус: расчеты выполнены")
            showinfo("Успех", "Расчеты успешно выполнены и результаты сохранены.")
        except Exception as e:
            self.status_label.config(text="Статус: ошибка расчета")
            showwarning("Ошибка", f"Ошибка при выполнении расчетов: {e}")
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Главное меню")

        self.preprocessor_button = tk.Button(root, text="Препроцессор", command=self.open_preprocessor)
        self.preprocessor_button.pack()

        self.processor_button = tk.Button(root, text="Процессор", command=self.open_processor)
        self.processor_button.pack()

        self.postprocessor_button = tk.Button(root, text="Постпроцессор", command=self.open_postprocessor)
        self.postprocessor_button.pack()

        self.processor_calculated = False

    def open_preprocessor(self):
        preprocessor_window = tk.Toplevel(self.root)
        PreprocessorApp(preprocessor_window)

    def open_processor(self):
        processor_window = tk.Toplevel(self.root)
        processor_app = ProcessorApp(processor_window)

        def on_close():
            if processor_app.calculated:
                self.processor_calculated = True
            processor_window.destroy()

        processor_window.protocol("WM_DELETE_WINDOW", on_close)

    def open_postprocessor(self):
        if not self.processor_calculated:
            showwarning("Предупреждение", "Постпроцессор не может быть открыт без выполнения расчетов в процессоре.")
            return

        postprocessor_window = tk.Toplevel(self.root)
        postprocessor_app = PostProcessorApp(postprocessor_window)

        # Обновить данные перед показом окна
        try:
            postprocessor_app.refresh_results()
        except AttributeError as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
