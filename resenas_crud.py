import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
resenas = db["Reseñas"]

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

def abrir_crud_resenas(username):
    def cargar_resenas():
        for row in tree.get_children():
            tree.delete(row)
        for i, resena in enumerate(resenas.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                resena.get('resena_id', ''),
                resena.get('usuario', ''),
                resena.get('comic_id', ''),
                resena.get('calificacion', ''),
                resena.get('comentario', ''),
                resena.get('fecha', ''),
                "Sí" if resena.get('recomendado', False) else "No",
                resena.get('likes', '')
            ), tags=(tag,))

    def obtener_resena_seleccionada():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            resena_id = int(valores[0])
            return resenas.find_one({"resena_id": resena_id})
        return None

    def eliminar_resena():
        resena = obtener_resena_seleccionada()
        if resena:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar la reseña del usuario '{resena['usuario']}'?")
            if confirm:
                resenas.delete_one({"resena_id": resena['resena_id']})
                cargar_resenas()
                messagebox.showinfo("Eliminado", "Reseña eliminada correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione una reseña.")

    def abrir_formulario_resena(titulo_ventana, resena_existente=None):
        def guardar_resena():
            try:
                nueva_resena = {
                    "resena_id": int(entry_id.get()),
                    "usuario": entry_usuario.get(),
                    "comic_id": int(entry_comic_id.get()),
                    "calificacion": int(entry_calificacion.get()),
                    "comentario": entry_comentario.get(),
                    "fecha": entry_fecha.get(),
                    "recomendado": var_recomendado.get() == 1,
                    "likes": int(entry_likes.get())
                }
                if resena_existente:
                    resenas.update_one({"resena_id": resena_existente["resena_id"]}, {"$set": nueva_resena})
                    messagebox.showinfo("Actualizado", "Reseña actualizada.")
                else:
                    if resenas.find_one({"resena_id": nueva_resena["resena_id"]}):
                        messagebox.showerror("Error", "resena_id ya existe.")
                        return
                    resenas.insert_one(nueva_resena)
                    messagebox.showinfo("Agregado", "Reseña agregada.")
                ventana_form.destroy()
                cargar_resenas()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x500")
        crear_fondo_animado(ventana_form, "./fondos/fondo6.gif", (400, 500))
        Label(ventana_form, text="ID Reseña:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Usuario:").pack()
        entry_usuario = Entry(ventana_form)
        entry_usuario.pack()

        Label(ventana_form, text="Comic ID:").pack()
        entry_comic_id = Entry(ventana_form)
        entry_comic_id.pack()

        Label(ventana_form, text="Calificación (1-5):").pack()
        entry_calificacion = Entry(ventana_form)
        entry_calificacion.pack()

        Label(ventana_form, text="Comentario:").pack()
        entry_comentario = Entry(ventana_form)
        entry_comentario.pack()

        Label(ventana_form, text="Fecha (YYYY-MM-DD):").pack()
        entry_fecha = Entry(ventana_form)
        entry_fecha.pack()

        Label(ventana_form, text="¿Recomendado?:").pack()
        var_recomendado = tk.IntVar()
        tk.Checkbutton(ventana_form, text="Sí", variable=var_recomendado).pack()

        Label(ventana_form, text="Likes:").pack()
        entry_likes = Entry(ventana_form)
        entry_likes.pack()

        if resena_existente:
            entry_id.insert(0, resena_existente['resena_id'])
            entry_id.config(state="disabled")
            entry_usuario.insert(0, resena_existente['usuario'])
            entry_comic_id.insert(0, resena_existente['comic_id'])
            entry_calificacion.insert(0, resena_existente['calificacion'])
            entry_comentario.insert(0, resena_existente['comentario'])
            entry_fecha.insert(0, resena_existente['fecha'])
            var_recomendado.set(1 if resena_existente['recomendado'] else 0)
            entry_likes.insert(0, resena_existente['likes'])

        Button(ventana_form, text="Guardar", command=guardar_resena).pack(pady=10)

    def crear_resena():
        abrir_formulario_resena("Agregar Reseña")

    def editar_resena():
        resena = obtener_resena_seleccionada()
        if resena:
            abrir_formulario_resena("Editar Reseña", resena)
        else:
            messagebox.showwarning("Aviso", "Seleccione una reseña.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Reseñas - Sesión: {username}")
    ventana.geometry("950x600")
    crear_fondo_animado(ventana, "./fondos/fondo3.gif", (950, 600))
    Label(ventana, text="Reseñas registradas", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Usuario", "Comic ID", "Calificación", "Comentario", "Fecha", "Recomendado", "Likes")
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

    Button(boton_frame, text="Agregar", width=15, command=crear_resena).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_resena).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_resena).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_resenas).grid(row=0, column=3, padx=5)

    cargar_resenas()
    ventana.mainloop()
