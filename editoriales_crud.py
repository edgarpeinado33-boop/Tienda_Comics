import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
editoriales = db["Editoriales"]

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

def abrir_crud_editoriales(username):
    def cargar_editoriales():
        for row in tree.get_children():
            tree.delete(row)
        for i, ed in enumerate(editoriales.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                ed.get('editorial_id', ''),
                ed.get('nombre', ''),
                ed.get('pais', ''),
                ed.get('fundacion', ''),
                ed.get('ceo', ''),
                ed.get('sede', ''),
                ed.get('cantidad_comics', ''),
                ed.get('web', '')
            ), tags=(tag,))

    def obtener_editorial_seleccionada():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            editorial_id = int(valores[0])
            return editoriales.find_one({"editorial_id": editorial_id})
        return None

    def eliminar_editorial():
        ed = obtener_editorial_seleccionada()
        if ed:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar la editorial '{ed['nombre']}'?")
            if confirm:
                editoriales.delete_one({"editorial_id": ed['editorial_id']})
                cargar_editoriales()
                messagebox.showinfo("Eliminado", "Editorial eliminada correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione una editorial.")

    def abrir_formulario_editorial(titulo_ventana, editorial_existente=None):
        def guardar_editorial():
            try:
                nuevo_ed = {
                    "editorial_id": int(entry_id.get()),
                    "nombre": entry_nombre.get(),
                    "pais": entry_pais.get(),
                    "fundacion": entry_fundacion.get(),
                    "ceo": entry_ceo.get(),
                    "sede": entry_sede.get(),
                    "cantidad_comics": int(entry_cantidad_comics.get()),
                    "web": entry_web.get()
                }
                if editorial_existente:
                    editoriales.update_one({"editorial_id": editorial_existente["editorial_id"]}, {"$set": nuevo_ed})
                    messagebox.showinfo("Actualizado", "Editorial actualizada.")
                else:
                    if editoriales.find_one({"editorial_id": nuevo_ed["editorial_id"]}):
                        messagebox.showerror("Error", "editorial_id ya existe.")
                        return
                    editoriales.insert_one(nuevo_ed)
                    messagebox.showinfo("Agregado", "Editorial agregada.")
                ventana_form.destroy()
                cargar_editoriales()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x550")
        crear_fondo_animado(ventana_form, "./fondos/fondo4.gif", (400, 550))
        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Nombre:").pack()
        entry_nombre = Entry(ventana_form)
        entry_nombre.pack()

        Label(ventana_form, text="País:").pack()
        entry_pais = Entry(ventana_form)
        entry_pais.pack()

        Label(ventana_form, text="Fundación (YYYY-MM-DD):").pack()
        entry_fundacion = Entry(ventana_form)
        entry_fundacion.pack()

        Label(ventana_form, text="CEO:").pack()
        entry_ceo = Entry(ventana_form)
        entry_ceo.pack()

        Label(ventana_form, text="Sede:").pack()
        entry_sede = Entry(ventana_form)
        entry_sede.pack()

        Label(ventana_form, text="Cantidad de cómics:").pack()
        entry_cantidad_comics = Entry(ventana_form)
        entry_cantidad_comics.pack()

        Label(ventana_form, text="Web:").pack()
        entry_web = Entry(ventana_form)
        entry_web.pack()

        if editorial_existente:
            entry_id.insert(0, editorial_existente['editorial_id'])
            entry_id.config(state="disabled")
            entry_nombre.insert(0, editorial_existente['nombre'])
            entry_pais.insert(0, editorial_existente['pais'])
            entry_fundacion.insert(0, editorial_existente['fundacion'])
            entry_ceo.insert(0, editorial_existente['ceo'])
            entry_sede.insert(0, editorial_existente['sede'])
            entry_cantidad_comics.insert(0, editorial_existente['cantidad_comics'])
            entry_web.insert(0, editorial_existente['web'])

        Button(ventana_form, text="Guardar", command=guardar_editorial).pack(pady=10)

    def crear_editorial():
        abrir_formulario_editorial("Agregar Editorial")

    def editar_editorial():
        ed = obtener_editorial_seleccionada()
        if ed:
            abrir_formulario_editorial("Editar Editorial", ed)
        else:
            messagebox.showwarning("Aviso", "Seleccione una editorial.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Editoriales - Sesión: {username}")
    ventana.geometry("900x600")
    crear_fondo_animado(ventana, "./fondos/fondo6.gif", (900, 600))
    Label(ventana, text="Editoriales registradas", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Nombre", "País", "Fundación", "CEO", "Sede", "Cantidad cómics", "Web")

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
        tree.column(col, width=110, anchor="center", stretch=True)

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

    Button(boton_frame, text="Agregar", width=15, command=crear_editorial).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_editorial).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_editorial).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_editoriales).grid(row=0, column=3, padx=5)

    cargar_editoriales()
    ventana.mainloop()


