import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt

class PostProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Постпроцессор Расчетов")

        self.results = None
        self.file_path = r"C:\\Users\\agolo\\OneDrive\\Рабочий стол\\САПР\\processor\\results.json"

        # Интерфейс загрузки результатов
        self.load_button = tk.Button(root, text="Загрузить результаты", command=self.refresh_results)
        self.load_button.pack()

        # Таблица для отображения результатов
        self.table = ttk.Treeview(root, columns=("X", "Nx", "Ux", "Sgx"), show="headings")
        self.table.heading("X", text="X")
        self.table.heading("Nx", text="Nx")
        self.table.heading("Ux", text="Ux")
        self.table.heading("Sgx", text="Sgx")
        self.table.pack()

        # Кнопка построения графиков
        self.plot_button = tk.Button(root, text="Построить графики", command=self.plot_graphs)
        self.plot_button.pack()

        # Кнопка сохранения результатов
        self.save_button = tk.Button(root, text="Сохранить таблицу", command=self.save_results)
        self.save_button.pack()

        # Загрузка данных при старте
        self.refresh_results()

    def refresh_results(self):
        """Загружает и обновляет данные из файла"""
        try:
            with open(self.file_path, "r") as file:
                self.results = json.load(file)
            self.populate_table()
            messagebox.showinfo("Успех", f"Результаты загружены из {self.file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить результаты: {e}")

    def populate_table(self):
        if not self.results:
            messagebox.showwarning("Внимание", "Нет данных для отображения")
            return
        for row in self.table.get_children():
            self.table.delete(row)
        for res in self.results:
            self.table.insert("", "end", values=(res["X"], res["Nx"], res["Ux"], res["Sgx"]))

    def save_results(self):
        if not self.results:
            messagebox.showwarning("Внимание", "Нет данных для сохранения")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            df = pd.DataFrame(self.results)
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Успех", f"Результаты сохранены в {file_path}")

    def plot_graphs(self):
        if not self.results:
            messagebox.showwarning("Внимание", "Нет данных для построения графиков")
            return

        X = [res["X"] for res in self.results]
        Nx = [res["Nx"] for res in self.results]
        Ux = [res["Ux"] for res in self.results]
        Sgx = [res["Sgx"] for res in self.results]

        plt.figure(figsize=(15, 10))

        # График Nx
        plt.subplot(3, 1, 1)
        plt.plot(X, Nx, label="Nx", color="blue")
        plt.title("График Nx")
        plt.xlabel("X")
        plt.ylabel("Nx")
        plt.grid()
        plt.legend()

        # График Ux
        plt.subplot(3, 1, 2)
        plt.plot(X, Ux, label="Ux", color="green")
        plt.title("График Ux")
        plt.xlabel("X")
        plt.ylabel("Ux")
        plt.grid()
        plt.legend()

        # График Sgx
        plt.subplot(3, 1, 3)
        plt.plot(X, Sgx, label="Sgx", color="red")
        plt.title("График Sgx")
        plt.xlabel("X")
        plt.ylabel("Sgx")
        plt.grid()
        plt.legend()

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = PostProcessorApp(root)
    root.mainloop()
