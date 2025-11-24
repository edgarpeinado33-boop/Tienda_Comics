import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
eventos = db["Eventos"]

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

def abrir_crud_eventos(username):
    def cargar_eventos():
        for row in tree.get_children():
            tree.delete(row)
        for i, evento in enumerate(eventos.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                evento.get('evento_id', ''),
                evento.get('nombre', ''),
                evento.get('fecha_inicio', ''),
                evento.get('fecha_fin', ''),
                evento.get('ubicacion', ''),
                evento.get('descripcion', ''),
                evento.get('asistentes', ''),
                "Sí" if evento.get('activo', False) else "No"
            ), tags=(tag,))

    def obtener_evento_seleccionado():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            evento_id = int(valores[0])
            return eventos.find_one({"evento_id": evento_id})
        return None

    def eliminar_evento():
        evento = obtener_evento_seleccionado()
        if evento:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar el evento '{evento['nombre']}'?")
            if confirm:
                eventos.delete_one({"evento_id": evento['evento_id']})
                cargar_eventos()
                messagebox.showinfo("Eliminado", "Evento eliminado correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione un evento.")

    def abrir_formulario_evento(titulo_ventana, evento_existente=None):
        def guardar_evento():
            try:
                nuevo_evento = {
                    "evento_id": int(entry_id.get()),
                    "nombre": entry_nombre.get(),
                    "fecha_inicio": entry_fecha_inicio.get(),
                    "fecha_fin": entry_fecha_fin.get(),
                    "ubicacion": entry_ubicacion.get(),
                    "descripcion": entry_descripcion.get(),
                    "asistentes": int(entry_asistentes.get()),
                    "activo": var_activo.get()
                }
                if evento_existente:
                    eventos.update_one({"evento_id": evento_existente["evento_id"]}, {"$set": nuevo_evento})
                    messagebox.showinfo("Actualizado", "Evento actualizado.")
                else:
                    if eventos.find_one({"evento_id": nuevo_evento["evento_id"]}):
                        messagebox.showerror("Error", "evento_id ya existe.")
                        return
                    eventos.insert_one(nuevo_evento)
                    messagebox.showinfo("Agregado", "Evento agregado.")
                ventana_form.destroy()
                cargar_eventos()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x550")
        crear_fondo_animado(ventana_form, "./fondos/fondo5.gif", (400, 550))
        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Nombre:").pack()
        entry_nombre = Entry(ventana_form)
        entry_nombre.pack()

        Label(ventana_form, text="Fecha Inicio (YYYY-MM-DD):").pack()
        entry_fecha_inicio = Entry(ventana_form)
        entry_fecha_inicio.pack()

        Label(ventana_form, text="Fecha Fin (YYYY-MM-DD):").pack()
        entry_fecha_fin = Entry(ventana_form)
        entry_fecha_fin.pack()

        Label(ventana_form, text="Ubicación:").pack()
        entry_ubicacion = Entry(ventana_form)
        entry_ubicacion.pack()

        Label(ventana_form, text="Descripción:").pack()
        entry_descripcion = Entry(ventana_form)
        entry_descripcion.pack()

        Label(ventana_form, text="Asistentes:").pack()
        entry_asistentes = Entry(ventana_form)
        entry_asistentes.pack()

        var_activo = tk.BooleanVar()
        chk_activo = tk.Checkbutton(ventana_form, text="Activo", variable=var_activo)
        chk_activo.pack()

        if evento_existente:
            entry_id.insert(0, evento_existente['evento_id'])
            entry_id.config(state="disabled")
            entry_nombre.insert(0, evento_existente['nombre'])
            entry_fecha_inicio.insert(0, evento_existente['fecha_inicio'])
            entry_fecha_fin.insert(0, evento_existente['fecha_fin'])
            entry_ubicacion.insert(0, evento_existente['ubicacion'])
            entry_descripcion.insert(0, evento_existente['descripcion'])
            entry_asistentes.insert(0, evento_existente['asistentes'])
            var_activo.set(evento_existente.get('activo', False))

        Button(ventana_form, text="Guardar", command=guardar_evento).pack(pady=10)

    def crear_evento():
        abrir_formulario_evento("Agregar Evento")

    def editar_evento():
        evento = obtener_evento_seleccionado()
        if evento:
            abrir_formulario_evento("Editar Evento", evento)
        else:
            messagebox.showwarning("Aviso", "Seleccione un evento.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Eventos - Sesión: {username}")
    ventana.geometry("900x600")
    crear_fondo_animado(ventana, "./fondos/fondo7.gif", (900, 600))
    Label(ventana, text="Eventos registrados", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Nombre", "Fecha Inicio", "Fecha Fin", "Ubicación", "Descripción", "Asistentes", "Activo")

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

    Button(boton_frame, text="Agregar", width=15, command=crear_evento).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_evento).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_evento).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_eventos).grid(row=0, column=3, padx=5)

    cargar_eventos()
    ventana.mainloop()
