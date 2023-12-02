import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog, ttk

def load_image_wrapper(canvas, image_frame):
    file_path = filedialog.askopenfilename()
    if file_path:
        img = Image.open(file_path)
        frame_width, frame_height = image_frame.winfo_width(), image_frame.winfo_height()
        scale = img.width/img.height
        frame_height = frame_width/scale
        frame_height = int(frame_height)
        img = img.resize((frame_width, frame_height))
        canvas.original_img = img.copy()
        canvas.image = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, image=canvas.image, anchor="nw")
        canvas.config(scrollregion=canvas.bbox(tk.ALL))
        canvas.image_loaded = True

def toggle_drawing_mode(canvas, button, message_label, class_combobox,context_menu, image_frame):
    if not hasattr(canvas, 'image_loaded'):
        print('1')
        canvas.image_loaded = False
        flash_message(message_label, canvas, times=4)
        return

    if not canvas.image_loaded:
        canvas.image_loaded = False
        flash_message(message_label, canvas, times=4)
        return
    
    if canvas.image_loaded:
        canvas.drawing_mode = not getattr(canvas, 'drawing_mode', False)

        if canvas.drawing_mode:
            button.config(relief="sunken", text="Выделить область")
            canvas.bind("<ButtonPress-1>", lambda event: start_drawing_rectangle(canvas, event))
            canvas.bind("<B1-Motion>", lambda event: expand_rectangle(canvas, event))
            canvas.bind("<ButtonRelease-1>", lambda event: finish_drawing_rectangle(canvas, event, class_combobox))
        else:
            button.config(relief="raised", text="Выделить область")
            canvas.unbind("<ButtonPress-1>")
            canvas.unbind("<B1-Motion>")
            canvas.unbind("<ButtonRelease-1>")
            canvas.bind("<ButtonRelease-1>", lambda event: on_canvas_click(event, canvas, class_combobox))
            canvas.bind("<Button-3>", lambda event: selected_right_on_canvas_click(event, canvas, context_menu, image_frame, class_combobox, button))

    else:
        button.config(relief="raised")

def start_drawing_rectangle(canvas, event):
    canvas.start_x = event.x
    canvas.start_y = event.y
    canvas.current_rectangle = canvas.create_rectangle(canvas.start_x, canvas.start_y, canvas.start_x, canvas.start_y, outline="#002a38")

def expand_rectangle(canvas, event):
    canvas.coords(canvas.current_rectangle, canvas.start_x, canvas.start_y, event.x, event.y)

def finish_drawing_rectangle(canvas, event, class_combobox):
    if not hasattr(canvas, 'rects'):
        canvas.rects = []
    rect_id = canvas.current_rectangle
    print('rect_id: ',rect_id, 'type: ', type(rect_id))
    canvas.rects.append(rect_id)

    class_name = tk.simpledialog.askstring("Введите класс", "Введите класс разметки:")
    if not class_name:
        class_name = "unknown"

    add_class_if_new(class_combobox, class_name)  # Добавить класс, если он новый
    # Сохранение имени и класса как атрибутов элемента разметки
    canvas.itemconfig(rect_id, tags=(class_name))

def add_class_if_new(class_combobox, new_class):
    if new_class and new_class not in class_combobox['values']:
        updated_classes = list(class_combobox['values']) + [new_class]
        class_combobox['values'] = updated_classes
        class_combobox.set(new_class)  # Выбрать новый класс

def undo_last_rectangle(canvas):
    if hasattr(canvas, 'rects') and canvas.rects:
        last_rect_id = canvas.rects.pop()
        canvas.delete(last_rect_id)

def save_markup(canvas):
    if hasattr(canvas, 'rects') and canvas.rects:
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if save_path:
            with open(save_path, 'w') as file:
                for rect_id in canvas.rects:
                    rect = canvas.coords(rect_id)
                    file.write(f"{rect[0]}, {rect[1]}, {rect[2]}, {rect[3]}\n")
            print("Разметка сохранена в:", save_path)
        else:
            print("Сохранение отменено")
    else:
        print("Нет разметки для сохранения")

def load_markup(canvas, message_label):
    if not hasattr(canvas, 'image_loaded'):
        canvas.image_loaded = False
        flash_message(message_label, canvas, times=4)
        return

    if not canvas.image_loaded:
        canvas.image_loaded = False
        flash_message(message_label, canvas, times=4)
        return
    if hasattr(canvas, 'rects'):
        for rect_id in canvas.rects:
            canvas.delete(rect_id)
        canvas.rects.clear()

    markup_path = filedialog.askopenfilename(title="Выберите файл разметки", filetypes=[("Text files", "*.txt")])
    if markup_path:
        with open(markup_path, 'r') as file:
            for line in file:
                x1, y1, x2, y2 = map(float, line.strip().split(','))
                rect_id = canvas.create_rectangle(x1, y1, x2, y2, outline="#002a38")
                if not hasattr(canvas, 'rects'):
                    canvas.rects = []
                canvas.rects.append(rect_id)
        print("Разметка загружена из:", markup_path)
    else:
        print("Загрузка отменена")

def clear_markup(canvas, context_menu, image_frame, drawing_mode_button, class_combobox):
    canvas.delete("all")
    # canvas.image_loaded = False
    if hasattr(canvas, 'rects'):
        canvas.rects.clear()
    canvas.create_image(0, 0, image=canvas.image, anchor="nw")
    canvas.bind("<Button-3>", lambda event: on_canvas_click_right_btn_menu(event, canvas, context_menu, image_frame, drawing_mode_button, class_combobox))



def clear_canvas(canvas, button, class_combobox, context_menu, image_frame):
    canvas.delete("all")
    canvas.image_loaded = False
    if hasattr(canvas, 'rects'):
        canvas.rects.clear()
    button.config(relief="raised")
    canvas.image_loaded = False
    class_combobox['values'] = []
    class_combobox.set('')
    canvas.bind("<Button-3>", lambda event: on_canvas_click_right_btn_menu(event, canvas, context_menu, image_frame, button, class_combobox))




# def add_class_to_combobox(class_combobox):
#     new_class = tk.simpledialog.askstring("Новый класс", "Введите название класса:")
#     if new_class and new_class not in class_combobox['values']:
#         updated_classes = list(class_combobox['values']) + [new_class]
#         class_combobox['values'] = updated_classes
#         select_first_class(class_combobox)


def setup_class_combobox(menu_frame, on_class_add, on_class_remove, canvas):
    class_combobox = ttk.Combobox(menu_frame, values=[], state='readonly')
    class_combobox.pack(anchor=tk.NW, padx=10, pady=5, fill=tk.X)

    add_class_button = tk.Button(menu_frame, text="Добавить класс", command=lambda: on_class_add(class_combobox))
    add_class_button.pack(anchor=tk.NW, pady=5, padx=10)

    remove_class_button = tk.Button(menu_frame, text="Удалить класс", command=lambda: on_class_remove(class_combobox, canvas))
    remove_class_button.pack(anchor=tk.NW,pady=5, padx=10)

    return class_combobox

def add_class_to_combobox(class_combobox):
    new_class = tk.simpledialog.askstring("Новый класс", "Введите название класса:")
    print(new_class)
    print([new_class])
    if new_class and new_class not in class_combobox['values']:
        updated_classes = list(class_combobox['values']) + [new_class]
        class_combobox['values'] = updated_classes
        select_first_class(class_combobox)

def remove_selected_class_from_combobox(class_combobox, canvas):
    current_class = class_combobox.get()
    updated_classes = [c for c in class_combobox['values'] if c != current_class]
    class_combobox['values'] = updated_classes
    # print(class_combobox['values'])
    select_first_class(class_combobox)
    # print('IT: ', type(canvas.find_all()))
    for item in canvas.find_all():
        print('item_type: ',type(item ), 'item: ', item)
        tag = canvas.gettags(item)
        # print(canvas,getid())
        print("current_class: ",current_class,"\ntag: ", tag)
        if len(tag) > 0:
            if current_class == tag[0]:
                canvas.itemconfig(item, tags = ('unknown'))
            

        if 'unknown' not in class_combobox['values'] and len(tag) > 0:
            class_combobox['values'] = list(class_combobox['values']) + ['unknown']
            select_first_class(class_combobox)
                # pass
    for i in canvas.find_all():
        print(canvas.gettags(i))


def select_first_class(class_combobox):
    if class_combobox['values']:
        class_combobox.set(class_combobox['values'][0])
    else:
        class_combobox.set('')






def on_canvas_click(event, canvas, class_combobox):
    x_click_pos = event.x
    y_click_pos = event.y
    touched_rects = []
    for rect_id in canvas.rects:
        if canvas.coords(rect_id)[0] <= x_click_pos <= canvas.coords(rect_id)[2] and canvas.coords(rect_id)[1] <= y_click_pos <= canvas.coords(rect_id)[3]:
            touched_rects.append(rect_id)
    touched_rects.sort()
    if hasattr(canvas, 'clicks_count'):
        canvas.clicks_count += 1
    elif not hasattr(canvas, 'clicks_count'):
        canvas.clicks_count = 1
    if hasattr(canvas, 'touched_rects') and not touched_rects:
        canvas.itemconfig(canvas.last_painted, fill="")
        hide_selected_item_class(canvas)
        canvas.touched_rects = touched_rects
        canvas.clicks_count = 0
        canvas.last_painted = 0
    elif hasattr(canvas, 'touched_rects') and canvas.touched_rects == touched_rects:
        if len(canvas.touched_rects) < canvas.clicks_count:
            canvas.itemconfig(canvas.last_painted, fill="")
            hide_selected_item_class(canvas)
            canvas.clicks_count = 0
            canvas.last_painted = 0
        else:
            canvas.itemconfig(canvas.last_painted, fill="")
            hide_selected_item_class(canvas)
            canvas.itemconfig(canvas.touched_rects[-(canvas.clicks_count)], fill="gray", stipple="gray50")
            show_selected_item_class(canvas)

            canvas.last_painted = canvas.touched_rects[-(canvas.clicks_count)]
    elif hasattr(canvas, 'touched_rects') and canvas.touched_rects != touched_rects:
        canvas.itemconfig(canvas.last_painted, fill="")
        hide_selected_item_class(canvas)
        canvas.touched_rects = touched_rects
        canvas.clicks_count = 1
        if(len(canvas.touched_rects) == 1):
            canvas.clicks_count = 1
            if canvas.last_painted == canvas.touched_rects[-(canvas.clicks_count)]:
                canvas.itemconfig(canvas.touched_rects[-(canvas.clicks_count)], fill="")
                hide_selected_item_class(canvas)
            else:
                canvas.itemconfig(canvas.touched_rects[-(canvas.clicks_count)], fill="gray", stipple="gray50")
                show_selected_item_class(canvas)
        elif canvas.last_painted == canvas.touched_rects[-(canvas.clicks_count)]:
            canvas.itemconfig(canvas.last_painted, fill="")
            hide_selected_item_class(canvas)
            canvas.itemconfig(canvas.touched_rects[-(canvas.clicks_count + 1)], fill="gray", stipple="gray50")
            canvas.clicks_count += 1
            show_selected_item_class(canvas)
        else:
            canvas.itemconfig(canvas.touched_rects[-(canvas.clicks_count)], fill="gray", stipple="gray50")
            show_selected_item_class(canvas)
        
        canvas.last_painted = canvas.touched_rects[-(canvas.clicks_count)]
    elif not hasattr(canvas, 'touched_rects'):
        canvas.touched_rects = touched_rects
        canvas.itemconfig(canvas.touched_rects[-(canvas.clicks_count)], fill="gray", stipple="gray50")
        show_selected_item_class(canvas)
        canvas.last_painted = canvas.touched_rects[-(canvas.clicks_count)]



def change_class_in_menu(canvas, class_combobox):
    if len(canvas.touched_rects):
        choosen_class = class_combobox.get()
        print(choosen_class)
        canvas.itemconfig(canvas.touched_rects.pop(0), tags=(choosen_class))
        canvas.itemconfig(canvas.last_painted, fill="")
        canvas.clicks_count = 0
        canvas.last_painted = 0
        hide_selected_item_class(canvas)


# def change_class_for_item(canvas, item_id, class_combobox):
#     choosen_class = tk.simpledialog.askfloat("Выбор класса", "Выберите класс:")


def add_new_class_in_menu(canvas, class_combobox):
    if len(canvas.touched_rects):
    # item_id = touched_rects.pop(0)
        input_class_for_item(canvas, canvas.touched_rects.pop(0), class_combobox)

def input_class_for_item(canvas, item_id, class_combobox):
    # Отображение диалогового окна для выбора класса
    choosen_class = tk.simpledialog.askstring("Выбор класса", "Выберите класс:", initialvalue=class_combobox.get())
    print(type(choosen_class))
    print(type(class_combobox['values']))
    # Обновление класса выбранного объекта, если класс был выбран
    if choosen_class:
        canvas.itemconfig(item_id, tags=(choosen_class))
        # Добавляем новый класс в комбобокс, если он там ещё не представлен
        if choosen_class not in class_combobox['values']:
            class_combobox['values'] = list(class_combobox['values']) + [choosen_class]
    canvas.itemconfig(canvas.last_painted, fill="")
    canvas.clicks_count = 0
    canvas.last_painted = 0
    hide_selected_item_class(canvas)

def hide_selected_item_class(canvas):
    canvas.delete(canvas.class_message)
def show_selected_item_class(canvas):
    center_x = int((canvas.coords(canvas.touched_rects[-(canvas.clicks_count)])[0] + canvas.coords(canvas.touched_rects[-(canvas.clicks_count)])[2]) / 2)
    center_y = int((canvas.coords(canvas.touched_rects[-(canvas.clicks_count)])[1] + canvas.coords(canvas.touched_rects[-(canvas.clicks_count)])[3]) / 2)
    # if len(canvas.gettags(canvas.touched_rects[-(canvas.clicks_count)]) > 1):
    _class = canvas.gettags(canvas.touched_rects[-(canvas.clicks_count)])[:len(canvas.gettags(canvas.touched_rects[-(canvas.clicks_count)]))]
    print('len', len(canvas.gettags(canvas.touched_rects[-(canvas.clicks_count)])))
    canvas.class_message = canvas.create_text(center_x, center_y, text = _class)

def menu_if_is_selected(event, context_menu):
    # show_selected_item_class(canvas)
    context_menu.tk_popup(event.x_root, event.y_root)
    
def selected_right_on_canvas_click(event, canvas, context_menu, image_frame, class_combobox, button):
    # print('menu')
    try:
        # start_len = context_menu.index('end')
        if context_menu.index('end') != None:
            for i in range(context_menu.index('end') + 1):
                context_menu.delete(0)
        index = context_menu.index("Изменить класс")
        
        # print(index)
    except tk.TclError:
        context_menu.add_command(label="Удалить класс(Unknown)", command= lambda: set_new_unknown_class(canvas, class_combobox))
        context_menu.add_command(label="удалить выбранную разметку", command = lambda: delete_selected_markup(canvas, class_combobox))#this
        context_menu.add_command(label="изменить класс на выбранный в списке", command = lambda: change_class_in_menu(canvas, class_combobox))
        context_menu.add_command(label="ввести новый класс", command = lambda: add_new_class_in_menu(canvas, class_combobox))
        print('except')
    
    # menu_if_is_selected(event, context_menu)

    x_click_pos = event.x
    y_click_pos = event.y

    if not hasattr(canvas, 'last_painted') or not hasattr(canvas, 'rects') or not context_menu.index('end'):
        on_canvas_click_right_btn_menu(event, canvas, context_menu, image_frame, class_combobox, button)
        if hasattr(canvas, 'clicks_count') and hasattr(canvas, 'last_painted'):
            canvas.itemconfig(canvas.last_painted, fill="")
            canvas.clicks_count = 0
            canvas.last_painted = 0
    elif not canvas.last_painted:
        on_canvas_click_right_btn_menu(event, canvas, context_menu, image_frame, class_combobox, button)
    elif canvas.coords(canvas.last_painted)[0] <= x_click_pos <= canvas.coords(canvas.last_painted)[2] and canvas.coords(canvas.last_painted)[1] <= y_click_pos <= canvas.coords(canvas.last_painted)[3]:   
        # context_menu.tk_popup(event.x_root, event.y_root)
        menu_if_is_selected(event, context_menu)
    else:
        if hasattr(canvas, 'clicks_count') and hasattr(canvas, 'last_painted'):
            canvas.itemconfig(canvas.last_painted, fill="")
            canvas.clicks_count = 0
            canvas.last_painted = 0
        on_canvas_click_right_btn_menu(event, canvas, context_menu, image_frame, class_combobox, button)

def default_menu(event, context_menu):
    context_menu.tk_popup(event.x_root, event.y_root)
def on_canvas_click_right_btn_menu(event, canvas, context_menu, image_frame, class_combobox, button):#функция меню по умолчанию или мимо разметки
    try:
        if context_menu.index('end') != None:
            for i in range(context_menu.index('end') + 1):
                context_menu.delete(0)
        index = context_menu.index("Отменить")

    except tk.TclError:
        context_menu.add_command(label="Отменить", command = lambda: undo_last_rectangle(canvas))
        context_menu.add_command(label="Загрузить изображение", command = lambda: load_image_wrapper(canvas, image_frame))
        context_menu.add_command(label="Очистить разметку", command = lambda: clear_markup(canvas, context_menu, image_frame, button, class_combobox))
        context_menu.add_command(label="Очистить все", command = lambda: clear_canvas(canvas, button, class_combobox, context_menu, image_frame))

        # context_menu.add_command(label="Удалить класс(Unknown)", command=set_new_unknown_class())
        # context_menu.add_command(label="удалить выбранную разметку", command=delete_selected_markup())
        print('except')
    default_menu(event, context_menu)
def change_class(event):
    print('change')

def set_new_unknown_class(canvas, class_combobox):
    canvas.itemconfig(canvas.last_painted, tags="unknown")
    add_class_if_new(class_combobox, "unknown")
    canvas.clicks_count = 0
    canvas.last_painted = 0
    hide_selected_item_class(canvas)
    canvas.itemconfig(canvas.last_painted, fill="")


def delete_selected_markup(canvas, class_combobox):
    # print(canvas.rects)
    hide_selected_item_class(canvas)
    canvas.delete(canvas.touched_rects[-(canvas.clicks_count)])
    canvas.rects = [i for i in canvas.rects if i != canvas.touched_rects[-(canvas.clicks_count)]]
    print(canvas.rects)







def flash_message(message_label, canvas, times=4):
    def show_message():
        message_label.place(relx=0.5, rely=0.5, anchor='center')
        canvas.after(1000, hide_message)
    def hide_message():
        message_label.place_forget()
    show_message()
    return