import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pandas as pd
import os
import io
import webbrowser

def open_pdf(pdf_file):
    webbrowser.open_new_tab(f"file://{pdf_file}")

class App:
    def __init__(self, master):
        self.master = master
        master.title("Сверка данных ЖСТ")

        # Основной фрейм для элементов
        self.main_frame = tk.Frame(master, bg="#E0E0E0")  # Серый фон
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Фрейм для кнопки "Выбрать папку"
        self.folder_frame = tk.Frame(self.main_frame, bg="white", relief="raised", bd=2) 
        self.folder_frame.pack(side=tk.LEFT, padx=20, pady=20)

        

        self.button_folder = tk.Button(self.folder_frame, text="Выбрать папку\nтестпакета с\nреестрами .csvу", command=self.open_folder, width=15, height=4)
        self.button_folder.pack(pady=15)

        # Фрейм для кнопки "Сравнить"
        self.compare_frame = tk.Frame(self.main_frame, bg="white", relief="raised", bd=2)
        self.compare_frame.pack(side=tk.LEFT, padx=20, pady=20)

        self.button_compare = tk.Button(self.compare_frame, text="Сравнить", command=self.show_comparison_window, width=15, height=2)
        self.button_compare.pack(pady=15)

        # ... (остальной код из предыдущего примера) ...
        self.folder_path = None
        self.jst_data = None
        self.jst_docs_data = None
        self.vik_data = None
        self.pvk_data = None
        self.rt_data = None
        self.uzk_data = None

        self.comparison_window = None  # Окно для таблицы сравнения

    def open_folder(self):
        self.folder_path = filedialog.askdirectory()
        print(f"Выбрана папка: {self.folder_path}")

    def show_comparison_window(self):
        if self.folder_path is None:
            tk.messagebox.showerror("Ошибка", "Выберите папку с реестрами!")
            return

        if self.comparison_window is not None:
            self.comparison_window.destroy()

        self.comparison_window = tk.Toplevel(self.master)
        self.comparison_window.title("Сравнение данных")

        self.frame_comparison = tk.Frame(self.comparison_window)
        self.frame_comparison.pack(pady=10)

        self.label_comparison = tk.Label(self.frame_comparison, text="Данные для сравнения:")
        self.label_comparison.pack()

        self.tree = ttk.Treeview(self.frame_comparison, columns=("№ Заключения", "Номер линии", "Дата", "Титул", "Номер СС", "Размер элементов", "Клеймо сварщика", "Заключения"), show="headings")
        self.tree.heading("№ Заключения", text="№ Заключения")
        self.tree.heading("Номер линии", text="Номер линии")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Титул", text="Титул")
        self.tree.heading("Номер СС", text="Номер СС")
        self.tree.heading("Размер элементов", text="Размер элементов")
        self.tree.heading("Клеймо сварщика", text="Клеймо сварщика")
        self.tree.heading("Заключения", text="Заключения")
        self.tree.pack()

        # Кнопка "Обновить сравнение"
        self.button_update = tk.Button(self.frame_comparison, text="Обновить сравнение", command=self.update_comparison)
        self.button_update.pack(pady=10)

        # Кнопка "Редактировать"
        self.button_edit = tk.Button(self.frame_comparison, text="Редактировать", command=self.edit_data)
        self.button_edit.pack(pady=10)

        self.compare_data()

    def compare_data(self):
        if self.folder_path is None:
            tk.messagebox.showerror("Ошибка", "Выберите папку с реестрами!")
            return

        try:
            # Загрузка данных из CSV-файлов
            # Преобразование данных в ЖСТ_Титул2.csv
            with open(os.path.join(self.folder_path, "table_data", "ЖСТ_Титул2.csv"), 'r', encoding='windows-1251') as f:
                jst_data_raw = f.read()
            jst_data_raw = jst_data_raw.replace(";", "|")
            self.jst_data = pd.read_csv(io.StringIO(jst_data_raw), sep="|", encoding='windows-1251')

            self.jst_docs_data = pd.read_csv(os.path.join(self.folder_path, "docs_ЖСТ", "ЖСТ.csv"), encoding="windows-1251", sep=";")
            self.vik_data = pd.read_csv(os.path.join(self.folder_path, "Заключение ВИК", "Заключение ВИК.csv"), encoding="windows-1251", sep=";")
            self.pvk_data = pd.read_csv(os.path.join(self.folder_path, "Заключение ПВК", "Заключение ПВК.csv"), encoding="windows-1251", sep=";")
            self.rt_data = pd.read_csv(os.path.join(self.folder_path, "Заключение РТ", "Заключение РТ.csv"), encoding="windows-1251", sep=";")
            self.uzk_data = pd.read_csv(os.path.join(self.folder_path, "Заключение УЗК", "Заключение УЗК.csv"), encoding="windows-1251", sep=";")
        except pd.errors.ParserError as e:
            tk.messagebox.showerror("Ошибка", f"Ошибка при чтении CSV-файлов: {e}")
            return

        self.tree.delete(*self.tree.get_children())

        # Сравнение данных
        for index, row in self.jst_data.iterrows():
            # Сравнение с "docs_ЖСТ"
            jst_docs_match = self.jst_docs_data[(self.jst_docs_data["Номер линии"] == row["Номер линии"]) & (self.jst_docs_data["Титул"] == row["Титул"])]

            # Сравнение с ВИК
            vik_match = self.vik_data[(self.vik_data["№ Заключения"] == row["№ Заключения"]) & (self.vik_data["Способ и результаты"] == row["Способ и результаты"]) & (self.vik_data["Дата"] == row["Дата Способ и результаты"]) & (self.vik_data["Титул"] == row["Титул"]) & (self.vik_data["Обозначение сварного соединения"] == row["Обозначение сварного соединения"]) & (self.vik_data["Наружный диаметр элемента"] == row["Наружный диаметр элемента"]) & (self.vik_data["Ф.И.О. сварщика, личное клеймо"] == row["Ф.И.О. сварщика, личное клеймо"])]

            # Сравнение с ПВК
            pvk_match = self.pvk_data[(self.pvk_data["№ Заключения"] == row["№ Заключения"]) & (self.pvk_data["Способ и результаты"] == row["Способ и результаты"]) & (self.pvk_data["Дата"] == row["Дата Способ и результаты"]) & (self.pvk_data["Титул"] == row["Титул"]) & (self.pvk_data["Обозначение сварного соединения"] == row["Обозначение сварного соединения"]) & (self.pvk_data["Наружный диаметр элемента"] == row["Наружный диаметр элемента"]) & (self.pvk_data["Ф.И.О. сварщика, личное клеймо"] == row["Ф.И.О. сварщика, личное клеймо"])]

            # Сравнение с РТ
            rt_match = self.rt_data[(self.rt_data["№ Заключения"] == row["№ Заключения"]) & (self.rt_data["Способ и результаты"] == row["Способ и результаты"]) & (self.rt_data["Дата"] == row["Дата Способ и результаты"]) & (self.rt_data["Титул"] == row["Титул"]) & (self.rt_data["Обозначение сварного соединения"] == row["Обозначение сварного соединения"]) & (self.rt_data["Наружный диаметр элемента"] == row["Наружный диаметр элемента"]) & (self.rt_data["Ф.И.О. сварщика, личное клеймо"] == row["Ф.И.О. сварщика, личное клеймо"])]

            # Сравнение с УЗК
            uzk_match = self.uzk_data[(self.uzk_data["№ Заключения"] == row["№ Заключения"]) & (self.uzk_data["Способ и результаты"] == row["Способ и результаты"]) & (self.uzk_data["Дата"] == row["Дата Способ и результаты"]) & (self.uzk_data["Титул"] == row["Титул"]) & (self.uzk_data["Обозначение сварного соединения"] == row["Обозначение сварного соединения"]) & (self.uzk_data["Наружный диаметр элемента"] == row["Наружный диаметр элемента"]) & (self.uzk_data["Ф.И.О. сварщика, личное клеймо"] == row["Ф.И.О. сварщика, личное клеймо"])]

            # Добавление строки в деревовидный виджет
            if jst_docs_match.empty or vik_match.empty or pvk_match.empty or rt_match.empty or uzk_match.empty:
                self.tree.insert("", "end", values=(row["№ Заключения"], row["Номер линии"], row["Дата"], row["Титул"], row["Номер СС"], row["Размер элементов"], row["Клеймо сварщика"], row["Заключения"]), tags=("red"))
            else:
                self.tree.insert("", "end", values=(row["№ Заключения"], row["Номер линии"], row["Дата"], row["Титул"], row["Номер СС"], row["Размер элементов"], row["Клеймо сварщика"], row["Заключения"]), tags=("green"))

            # Кнопка для открытия PDF
            pdf_path = os.path.join(self.folder_path, "Заключение ВИК", "Заключение ВИК.pdf") # Замените "Заключение ВИК.pdf" на реальный путь к PDF-файлу 
            self.tree.insert("", "end", values=(row["№ Заключения"], row["Номер линии"], row["Дата"], row["Титул"], row["Номер СС"], row["Размер элементов"], row["Клеймо сварщика"], row["Заключения"]), tags=("green"))
            self.tree.tag_bind("green", "<Button-1>", lambda event: open_pdf(pdf_path))

    def update_comparison(self):
        # Обновление данных в таблице
        self.tree.delete(*self.tree.get_children())

        # Обновление данных в датафреймах
        # Преобразование данных в ЖСТ_Титул2.csv
        with open(os.path.join(self.folder_path, "table_data", "ЖСТ_Титул2.csv"), 'r', encoding='windows-1251') as f:
            jst_data_raw = f.read()
        jst_data_raw = jst_data_raw.replace(";", "|")
        self.jst_data = pd.read_csv(io.StringIO(jst_data_raw), sep="|", encoding='windows-1251')

        self.jst_docs_data = pd.read_csv(os.path.join(self.folder_path, "docs_ЖСТ", "ЖСТ.csv"), encoding="windows-1251", sep=";")
        self.vik_data = pd.read_csv(os.path.join(self.folder_path, "Заключение ВИК", "Заключение ВИК.csv"), encoding="windows-1251", sep=";")
        self.pvk_data = pd.read_csv(os.path.join(self.folder_path, "Заключение ПВК", "Заключение ПВК.csv"), encoding="windows-1251", sep=";")
        self.rt_data = pd.read_csv(os.path.join(self.folder_path, "Заключение РТ", "Заключение РТ.csv"), encoding="windows-1251", sep=";")
        self.uzk_data = pd.read_csv(os.path.join(self.folder_path, "Заключение УЗК", "Заключение УЗК.csv"), encoding="windows-1251", sep=";")

        # Вызов функции для сравнения данных
        self.compare_data()

    def edit_data(self):
        # Функция для ручного редактирования данных, пока не реализована
        tk.messagebox.showinfo("Редактирование", "Функция редактирования еще не реализована.")

root = tk.Tk()
app = App(root)
root.mainloop()