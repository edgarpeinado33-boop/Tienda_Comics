import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
premios = db["Premios"]

def crear_fondo_animado(ventana, gif_path, size):
    
    gif = Image.open(gif_path)
    frames = [ImageTk.PhotoImage(frame.resize(size, Image.LANCZOS)) for frame in ImageSequence.Iterator(gif)]

    fondo_label = tk.Label(ventana)
    fondo_label.place(x=0, y=0, relwidth=1, relheight=1)

    def animar(ind=0):
        if fondo_label.winfo_exists():
            fondo_label.configure(image=frames[ind])
            ventana.after(100, animar, (ind + 1) % len(frames))

    animar()
    return fondo_label


def crear_fondo_estatico(ventana, img_path, size):
    
    img = Image.open(img_path).resize(size, Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    fondo_label = tk.Label(ventana, image=img_tk)
    fondo_label.image = img_tk 
    fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
    return fondo_label

def abrir_crud_premios(username):
    def cargar_premios():
        for row in tree.get_children():
            tree.delete(row)
        for i, premio in enumerate(premios.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                premio.get('premio_id', ''),
                premio.get('nombre', ''),
                premio.get('categoria', ''),
                premio.get('fecha', ''),
                premio.get('comic_id', ''),
                premio.get('autor_id', ''),
                premio.get('descripcion', ''),
                'Sí' if premio.get('activo', False) else 'No'
            ), tags=(tag,))

    def obtener_premio_seleccionado():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            premio_id = int(valores[0])
            return premios.find_one({"premio_id": premio_id})
        return None

    def eliminar_premio():
        premio = obtener_premio_seleccionado()
        if premio:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar el premio '{premio['nombre']}'?")
            if confirm:
                premios.delete_one({"premio_id": premio['premio_id']})
                cargar_premios()
                messagebox.showinfo("Eliminado", "Premio eliminado correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione un premio.")

    def abrir_formulario_premio(titulo_ventana, premio_existente=None):
        def guardar_premio():
            try:
                nuevo_premio = {
                    "premio_id": int(entry_id.get()),
                    "nombre": entry_nombre.get(),
                    "categoria": entry_categoria.get(),
                    "fecha": entry_fecha.get(),
                    "comic_id": int(entry_comic_id.get()),
                    "autor_id": int(entry_autor_id.get()),
                    "descripcion": entry_descripcion.get(),
                    "activo": var_activo.get() == 1
                }
                if premio_existente:
                    premios.update_one({"premio_id": premio_existente["premio_id"]}, {"$set": nuevo_premio})
                    messagebox.showinfo("Actualizado", "Premio actualizado.")
                else:
                    if premios.find_one({"premio_id": nuevo_premio["premio_id"]}):
                        messagebox.showerror("Error", "premio_id ya existe.")
                        return
                    premios.insert_one(nuevo_premio)
                    messagebox.showinfo("Agregado", "Premio agregado.")
                ventana_form.destroy()
                cargar_premios()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x550")
        crear_fondo_animado(ventana_form, "./fondos/fondo7.gif", (400, 550))
        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Nombre:").pack()
        entry_nombre = Entry(ventana_form)
        entry_nombre.pack()

        Label(ventana_form, text="Categoría:").pack()
        entry_categoria = Entry(ventana_form)
        entry_categoria.pack()

        Label(ventana_form, text="Fecha (YYYY-MM-DD):").pack()
        entry_fecha = Entry(ventana_form)
        entry_fecha.pack()

        Label(ventana_form, text="Comic ID:").pack()
        entry_comic_id = Entry(ventana_form)
        entry_comic_id.pack()

        Label(ventana_form, text="Autor ID:").pack()
        entry_autor_id = Entry(ventana_form)
        entry_autor_id.pack()

        Label(ventana_form, text="Descripción:").pack()
        entry_descripcion = Entry(ventana_form)
        entry_descripcion.pack()

        var_activo = tk.IntVar()
        tk.Checkbutton(ventana_form, text="Activo", variable=var_activo).pack()

        if premio_existente:
            entry_id.insert(0, premio_existente['premio_id'])
            entry_id.config(state="disabled")
            entry_nombre.insert(0, premio_existente['nombre'])
            entry_categoria.insert(0, premio_existente['categoria'])
            entry_fecha.insert(0, premio_existente['fecha'])
            entry_comic_id.insert(0, premio_existente['comic_id'])
            entry_autor_id.insert(0, premio_existente['autor_id'])
            entry_descripcion.insert(0, premio_existente['descripcion'])
            var_activo.set(1 if premio_existente['activo'] else 0)

        Button(ventana_form, text="Guardar", command=guardar_premio).pack(pady=10)

    def crear_premio():
        abrir_formulario_premio("Agregar Premio")

    def editar_premio():
        premio = obtener_premio_seleccionado()
        if premio:
            abrir_formulario_premio("Editar Premio", premio)
        else:
            messagebox.showwarning("Aviso", "Seleccione un premio.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Premios - Sesión: {username}")
    ventana.geometry("1000x600")
    crear_fondo_animado(ventana, "./fondos/fondo6.gif", (1000, 600))
    Label(ventana, text="Premios registrados", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Nombre", "Categoría", "Fecha", "Comic ID", "Autor ID", "Descripción", "Activo")

    tree = ttk.Treeview(frame_interno, columns=columnas, show="headings", selectmode="browse")

    style = ttk.Style()
    style.theme_use('default')
    style.configure("Treeview",
                    background="white",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="white",
                    font=("Arial", 10),
                    bordercolor="black",
                    borderwidth=1)
    style.configure("Treeview.Heading",
                    font=("Arial", 11, "bold"),
                    background="#d9d9d9",
                    foreground="black",
                    relief="raised",
                    bordercolor="black",
                    borderwidth=1)
    style.map("Treeview",
              background=[('selected', '#3399FF')],
              foreground=[('selected', 'white')])

    tree.tag_configure('oddrow', background='white')
    tree.tag_configure('evenrow', background='#f0f0f0')

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center", stretch=True)

    scrollbar_v = ttk.Scrollbar(frame_interno, orient="vertical", command=tree.yview)
    scrollbar_h = ttk.Scrollbar(frame_interno, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

    tree.grid(row=0, column=0, sticky='nsew')
    scrollbar_v.grid(row=0, column=1, sticky='ns')
    scrollbar_h.grid(row=1, column=0, sticky='ew')

    frame_interno.grid_rowconfigure(0, weight=1)
    frame_interno.grid_columnconfigure(0, weight=1)

    boton_frame = tk.Frame(ventana)
    boton_frame.pack(pady=10)

    Button(boton_frame, text="Agregar", width=15, command=crear_premio).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_premio).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_premio).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_premios).grid(row=0, column=3, padx=5)

    cargar_premios()
    ventana.mainloop()
