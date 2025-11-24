import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
mangas = db["Mangas"]

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


def abrir_crud_mangas(username):
    def cargar_mangas():
        for row in tree.get_children():
            tree.delete(row)
        for i, manga in enumerate(mangas.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                manga.get('manga_id', ''),
                manga.get('titulo', ''),
                manga.get('autor_id', ''),
                manga.get('editorial_id', ''),
                manga.get('fecha_publicacion', ''),
                manga.get('genero', ''),
                manga.get('precio', ''),
                manga.get('sinopsis', '')
            ), tags=(tag,))

    def obtener_manga_seleccionado():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            manga_id = int(valores[0])
            return mangas.find_one({"manga_id": manga_id})
        return None

    def eliminar_manga():
        manga = obtener_manga_seleccionado()
        if manga:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar el manga '{manga['titulo']}'?")
            if confirm:
                mangas.delete_one({"manga_id": manga['manga_id']})
                cargar_mangas()
                messagebox.showinfo("Eliminado", "Manga eliminado correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione un manga.")

    def abrir_formulario_manga(titulo_ventana, manga_existente=None):
        def guardar_manga():
            try:
                nuevo_manga = {
                    "manga_id": int(entry_id.get()),
                    "titulo": entry_titulo.get(),
                    "autor_id": int(entry_autor_id.get()),
                    "editorial_id": int(entry_editorial_id.get()),
                    "fecha_publicacion": entry_fecha_publicacion.get(),
                    "genero": entry_genero.get(),
                    "precio": float(entry_precio.get()),
                    "sinopsis": entry_sinopsis.get()
                }
                if manga_existente:
                    mangas.update_one({"manga_id": manga_existente["manga_id"]}, {"$set": nuevo_manga})
                    messagebox.showinfo("Actualizado", "Manga actualizado.")
                else:
                    if mangas.find_one({"manga_id": nuevo_manga["manga_id"]}):
                        messagebox.showerror("Error", "manga_id ya existe.")
                        return
                    mangas.insert_one(nuevo_manga)
                    messagebox.showinfo("Agregado", "Manga agregado.")
                ventana_form.destroy()
                cargar_mangas()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x500")
        crear_fondo_animado(ventana_form, "./fondos/fondo5.gif", (400, 500))
        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Título:").pack()
        entry_titulo = Entry(ventana_form)
        entry_titulo.pack()

        Label(ventana_form, text="Autor ID:").pack()
        entry_autor_id = Entry(ventana_form)
        entry_autor_id.pack()

        Label(ventana_form, text="Editorial ID:").pack()
        entry_editorial_id = Entry(ventana_form)
        entry_editorial_id.pack()

        Label(ventana_form, text="Fecha Publicación (YYYY-MM-DD):").pack()
        entry_fecha_publicacion = Entry(ventana_form)
        entry_fecha_publicacion.pack()

        Label(ventana_form, text="Género:").pack()
        entry_genero = Entry(ventana_form)
        entry_genero.pack()

        Label(ventana_form, text="Precio:").pack()
        entry_precio = Entry(ventana_form)
        entry_precio.pack()

        Label(ventana_form, text="Sinopsis:").pack()
        entry_sinopsis = Entry(ventana_form)
        entry_sinopsis.pack()

        if manga_existente:
            entry_id.insert(0, manga_existente['manga_id'])
            entry_id.config(state="disabled")
            entry_titulo.insert(0, manga_existente['titulo'])
            entry_autor_id.insert(0, manga_existente['autor_id'])
            entry_editorial_id.insert(0, manga_existente['editorial_id'])
            entry_fecha_publicacion.insert(0, manga_existente['fecha_publicacion'])
            entry_genero.insert(0, manga_existente['genero'])
            entry_precio.insert(0, manga_existente['precio'])
            entry_sinopsis.insert(0, manga_existente['sinopsis'])

        Button(ventana_form, text="Guardar", command=guardar_manga).pack(pady=10)

    def crear_manga():
        abrir_formulario_manga("Agregar Manga")

    def editar_manga():
        manga = obtener_manga_seleccionado()
        if manga:
            abrir_formulario_manga("Editar Manga", manga)
        else:
            messagebox.showwarning("Aviso", "Seleccione un manga.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Mangas - Sesión: {username}")
    ventana.geometry("900x600")
    crear_fondo_animado(ventana, "./fondos/fondo7.gif", (900, 600))
    Label(ventana, text="Mangas registrados", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Título", "Autor ID", "Editorial ID", "Fecha Publicación", "Género", "Precio", "Sinopsis")

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
        tree.column(col, width=100, anchor="center", stretch=True)

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

    Button(boton_frame, text="Agregar", width=15, command=crear_manga).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_manga).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_manga).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_mangas).grid(row=0, column=3, padx=5)

    cargar_mangas()
    ventana.mainloop()
