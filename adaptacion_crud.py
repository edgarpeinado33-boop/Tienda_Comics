import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
adaptaciones = db["Adaptaciones"]

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

def abrir_crud_adaptaciones(username):
    def cargar_adaptaciones():
        for row in tree.get_children():
            tree.delete(row)
        for i, adaptacion in enumerate(adaptaciones.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                adaptacion.get('adaptacion_id', ''),
                adaptacion.get('comic_id', ''),
                adaptacion.get('tipo', ''),
                adaptacion.get('titulo', ''),
                adaptacion.get('fecha_estreno', ''),
                adaptacion.get('director', ''),
                adaptacion.get('calificacion_tmdb', ''),
                adaptacion.get('descripcion', '')
            ), tags=(tag,))

    def obtener_adaptacion_seleccionada():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            adaptacion_id = int(valores[0])
            return adaptaciones.find_one({"adaptacion_id": adaptacion_id})
        return None

    def eliminar_adaptacion():
        adaptacion = obtener_adaptacion_seleccionada()
        if adaptacion:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar la adaptación '{adaptacion['titulo']}'?")
            if confirm:
                adaptaciones.delete_one({"adaptacion_id": adaptacion['adaptacion_id']})
                cargar_adaptaciones()
                messagebox.showinfo("Eliminado", "Adaptación eliminada correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione una adaptación.")

    def abrir_formulario_adaptacion(titulo_ventana, adaptacion_existente=None):
        def guardar_adaptacion():
            try:
                nueva_adaptacion = {
                    "adaptacion_id": int(entry_id.get()),
                    "comic_id": int(entry_comic_id.get()),
                    "tipo": entry_tipo.get(),
                    "titulo": entry_titulo.get(),
                    "fecha_estreno": entry_fecha_estreno.get(),
                    "director": entry_director.get(),
                    "calificacion_tmdb": float(entry_calificacion.get()),
                    "descripcion": entry_descripcion.get()
                }
                if adaptacion_existente:
                    adaptaciones.update_one({"adaptacion_id": adaptacion_existente["adaptacion_id"]}, {"$set": nueva_adaptacion})
                    messagebox.showinfo("Actualizado", "Adaptación actualizada.")
                else:
                    if adaptaciones.find_one({"adaptacion_id": nueva_adaptacion["adaptacion_id"]}):
                        messagebox.showerror("Error", "adaptacion_id ya existe.")
                        return
                    adaptaciones.insert_one(nueva_adaptacion)
                    messagebox.showinfo("Agregado", "Adaptación agregada.")
                ventana_form.destroy()
                cargar_adaptaciones()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x500")
        
        crear_fondo_animado(ventana_form, "./fondos/fondo7.gif", (400, 500))
        
        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Comic ID:").pack()
        entry_comic_id = Entry(ventana_form)
        entry_comic_id.pack()

        Label(ventana_form, text="Tipo (Película, Serie, etc):").pack()
        entry_tipo = Entry(ventana_form)
        entry_tipo.pack()

        Label(ventana_form, text="Título:").pack()
        entry_titulo = Entry(ventana_form)
        entry_titulo.pack()

        Label(ventana_form, text="Fecha Estreno (YYYY-MM-DD):").pack()
        entry_fecha_estreno = Entry(ventana_form)
        entry_fecha_estreno.pack()

        Label(ventana_form, text="Director:").pack()
        entry_director = Entry(ventana_form)
        entry_director.pack()

        Label(ventana_form, text="Calificación TMDB:").pack()
        entry_calificacion = Entry(ventana_form)
        entry_calificacion.pack()

        Label(ventana_form, text="Descripción:").pack()
        entry_descripcion = Entry(ventana_form)
        entry_descripcion.pack()

        if adaptacion_existente:
            entry_id.insert(0, adaptacion_existente['adaptacion_id'])
            entry_id.config(state="disabled")
            entry_comic_id.insert(0, adaptacion_existente['comic_id'])
            entry_tipo.insert(0, adaptacion_existente['tipo'])
            entry_titulo.insert(0, adaptacion_existente['titulo'])
            entry_fecha_estreno.insert(0, adaptacion_existente['fecha_estreno'])
            entry_director.insert(0, adaptacion_existente['director'])
            entry_calificacion.insert(0, adaptacion_existente['calificacion_tmdb'])
            entry_descripcion.insert(0, adaptacion_existente['descripcion'])

        Button(ventana_form, text="Guardar", command=guardar_adaptacion).pack(pady=10)

    def crear_adaptacion():
        abrir_formulario_adaptacion("Agregar Adaptación")

    def editar_adaptacion():
        adaptacion = obtener_adaptacion_seleccionada()
        if adaptacion:
            abrir_formulario_adaptacion("Editar Adaptación", adaptacion)
        else:
            messagebox.showwarning("Aviso", "Seleccione una adaptación.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Adaptaciones - Sesión: {username}")
    ventana.geometry("900x600")
    crear_fondo_animado(ventana, "./fondos/fondo5.gif", (900, 600))

    Label(ventana, text="Adaptaciones registradas", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Comic ID", "Tipo", "Título", "Fecha Estreno", "Director", "Calificación TMDB", "Descripción")

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

    Button(boton_frame, text="Agregar", width=15, command=crear_adaptacion).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_adaptacion).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_adaptacion).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_adaptaciones).grid(row=0, column=3, padx=5)

    cargar_adaptaciones()
    ventana.mainloop()
