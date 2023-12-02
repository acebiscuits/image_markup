import tkinter as tk
from tkinter import ttk
import dpnds

def setup_ui():
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('default')
    style.map('TCombobox', fieldbackground=[('readonly', 'white')], selectbackground=[('readonly', 'white')], selectforeground=[('readonly', 'black')])
    style.configure('TCombobox', selectborderwidth=0, borderwidth=0)
    # style.map('TCombobox', selectbackground=[('readonly', 'white')], selectforeground=[('readonly', 'black')])
    root.title("Разметка изображений")
    window_width = 1000
    window_height = 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    menu_frame = tk.Frame(root, width=200, bg='gray')
    image_frame = tk.Frame(root, bg='white')
    menu_frame.pack(side=tk.LEFT, fill=tk.Y)
    image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(image_frame)
    canvas.pack(expand=True, fill=tk.BOTH)

    btn_load = tk.Button(menu_frame, text="Загрузить изображение", command=lambda: dpnds.load_image_wrapper(canvas, image_frame))
    btn_load.pack(anchor=tk.NW, padx=10, pady=10)

    drawing_mode_button = tk.Button(menu_frame, text="Выделить область", command=lambda: dpnds.toggle_drawing_mode(canvas, drawing_mode_button, message_label, class_combobox, context_menu, image_frame))
    drawing_mode_button.pack(anchor=tk.W, padx=10, pady=10)

    undo_button = tk.Button(menu_frame, text="Отменить", command=lambda: dpnds.undo_last_rectangle(canvas))
    undo_button.pack(anchor=tk.W, padx=10, pady=10)

    btn_save_markup = tk.Button(menu_frame, text="Сохранить разметку", command=lambda: dpnds.save_markup(canvas))
    btn_save_markup.pack(anchor=tk.W, padx=10, pady=10)

    btn_load_markup = tk.Button(menu_frame, text="Загрузить разметку", command=lambda: dpnds.load_markup(canvas, message_label))
    btn_load_markup.pack(anchor=tk.W, padx=10, pady=10)

    btn_clear_markup = tk.Button(menu_frame, text="Очистить разметку", command=lambda: dpnds.clear_markup(canvas, context_menu, image_frame, drawing_mode_button, class_combobox))
    btn_clear_markup.pack(anchor=tk.W, padx=10, pady=10)

    btn_clear_all = tk.Button(menu_frame, text="Очистить всё", command=lambda: dpnds.clear_canvas(canvas, drawing_mode_button, class_combobox, context_menu, image_frame))
    btn_clear_all.pack(anchor=tk.W, padx=10, pady=10)









    class_combobox = dpnds.setup_class_combobox(menu_frame, dpnds.add_class_to_combobox, dpnds.remove_selected_class_from_combobox, canvas)
    dpnds.select_first_class(class_combobox)


    # class_combobox = ttk.Combobox(root, values=['Class1', 'Class2'])
    class_combobox.pack()
    # add_class_button = tk.Button(menu_frame, text="Добавить класс", command=lambda: dpnds.add_class_prompt(class_combobox))
    # add_class_button.pack(anchor=tk.NW, padx=10)

    # remove_class_button = tk.Button(menu_frame, text="Удалить класс", command=lambda: dpnds.remove_selected_class_from_combobox(class_combobox))
    # remove_class_button.pack(anchor=tk.NW, padx=10)




    context_menu = tk.Menu(root, tearoff=0)
    # context_menu.add_command(label="Удалить класс(Unknown)", command=dpnds.set_new_unknown_class())
    # context_menu.add_command(label="удалить выбранную разметку", command=dpnds.delete_selected_markup())


    canvas.bind("<ButtonRelease-1>", lambda event: dpnds.on_canvas_click(event, canvas, class_combobox))

    # canvas.bind("<Button-3>", lambda event: dpnds.on_canvas_click_right_btn_menu(event, canvas))
    canvas.bind("<Button-3>", lambda event: dpnds.on_canvas_click_right_btn_menu(event, canvas, context_menu, image_frame, drawing_mode_button, class_combobox))





    message_label = tk.Label(canvas, text="Изображение не загружено!", bg='red')

    return root, canvas

def main():
    root, canvas = setup_ui()
    root.mainloop()

if __name__ == "__main__":
    main()
