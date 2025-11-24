import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk, BooleanVar, Checkbutton
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
idiomas = db["Idiomas"]

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


def abrir_crud_idiomas(username):
    def cargar_idiomas():
        for row in tree.get_children():
            tree.delete(row)
        for i, idioma in enumerate(idiomas.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                idioma.get('idioma_id', ''),
                idioma.get('nombre', ''),
                idioma.get('codigo', ''),
                idioma.get('region', ''),
                "Sí" if idioma.get('activo', False) else "No",
                idioma.get('numero_traducciones', 0),
                idioma.get('editorial_id', ''),
                idioma.get('descripcion', '')
            ), tags=(tag,))

    def obtener_idioma_seleccionado():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            idioma_id = int(valores[0])
            return idiomas.find_one({"idioma_id": idioma_id})
        return None

    def eliminar_idioma():
        idioma = obtener_idioma_seleccionado()
        if idioma:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar el idioma '{idioma['nombre']}'?")
            if confirm:
                idiomas.delete_one({"idioma_id": idioma['idioma_id']})
                cargar_idiomas()
                messagebox.showinfo("Eliminado", "Idioma eliminado correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione un idioma.")

    def abrir_formulario_idioma(titulo_ventana, idioma_existente=None):
        def guardar_idioma():
            try:
                nuevo_idioma = {
                    "idioma_id": int(entry_id.get()),
                    "nombre": entry_nombre.get(),
                    "codigo": entry_codigo.get(),
                    "region": entry_region.get(),
                    "activo": var_activo.get(),
                    "numero_traducciones": int(entry_num_traducciones.get()),
                    "editorial_id": int(entry_editorial_id.get()),
                    "descripcion": entry_descripcion.get()
                }
                if idioma_existente:
                    idiomas.update_one({"idioma_id": idioma_existente["idioma_id"]}, {"$set": nuevo_idioma})
                    messagebox.showinfo("Actualizado", "Idioma actualizado.")
                else:
                    if idiomas.find_one({"idioma_id": nuevo_idioma["idioma_id"]}):
                        messagebox.showerror("Error", "idioma_id ya existe.")
                        return
                    idiomas.insert_one(nuevo_idioma)
                    messagebox.showinfo("Agregado", "Idioma agregado.")
                ventana_form.destroy()
                cargar_idiomas()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x500")
        crear_fondo_animado(ventana_form, "./fondos/fondo5.gif", (400, 500))
        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Nombre:").pack()
        entry_nombre = Entry(ventana_form)
        entry_nombre.pack()

        Label(ventana_form, text="Código:").pack()
        entry_codigo = Entry(ventana_form)
        entry_codigo.pack()

        Label(ventana_form, text="Región:").pack()
        entry_region = Entry(ventana_form)
        entry_region.pack()

        Label(ventana_form, text="Activo:").pack()
        var_activo = BooleanVar()
        chk_activo = Checkbutton(ventana_form, variable=var_activo, text="Activo")
        chk_activo.pack()

        Label(ventana_form, text="Número de Traducciones:").pack()
        entry_num_traducciones = Entry(ventana_form)
        entry_num_traducciones.pack()

        Label(ventana_form, text="Editorial ID:").pack()
        entry_editorial_id = Entry(ventana_form)
        entry_editorial_id.pack()

        Label(ventana_form, text="Descripción:").pack()
        entry_descripcion = Entry(ventana_form)
        entry_descripcion.pack()

        if idioma_existente:
            entry_id.insert(0, idioma_existente['idioma_id'])
            entry_id.config(state="disabled")
            entry_nombre.insert(0, idioma_existente['nombre'])
            entry_codigo.insert(0, idioma_existente['codigo'])
            entry_region.insert(0, idioma_existente['region'])
            var_activo.set(idioma_existente.get('activo', False))
            entry_num_traducciones.insert(0, idioma_existente['numero_traducciones'])
            entry_editorial_id.insert(0, idioma_existente['editorial_id'])
            entry_descripcion.insert(0, idioma_existente['descripcion'])

        Button(ventana_form, text="Guardar", command=guardar_idioma).pack(pady=10)

    def crear_idioma():
        abrir_formulario_idioma("Agregar Idioma")

    def editar_idioma():
        idioma = obtener_idioma_seleccionado()
        if idioma:
            abrir_formulario_idioma("Editar Idioma", idioma)
        else:
            messagebox.showwarning("Aviso", "Seleccione un idioma.")

    
    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Idiomas - Sesión: {username}")
    ventana.geometry("900x600")
    crear_fondo_animado(ventana, "./fondos/fondo4.gif", (900, 600))
    Label(ventana, text="Idiomas registrados", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Nombre", "Código", "Región", "Activo", "Nº Traducciones", "Editorial ID", "Descripción")

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

    Button(boton_frame, text="Agregar", width=15, command=crear_idioma).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_idioma).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_idioma).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_idiomas).grid(row=0, column=3, padx=5)

    cargar_idiomas()
    ventana.mainloop()


