import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk, StringVar, Checkbutton
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence


db = get_db()
usuarios = db["Usuarios"]

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

def abrir_crud_usuarios(username_sesion):
    def cargar_usuarios():
        for row in tree.get_children():
            tree.delete(row)
        for i, usuario in enumerate(usuarios.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                usuario.get('usuario_id', ''),
                usuario.get('username', ''),
                usuario.get('email', ''),
                usuario.get('rol', ''),
                "Sí" if usuario.get('activo', False) else "No",
                usuario.get('fecha_creacion', ''),
                usuario.get('ultimo_acceso', '') or ""
            ), tags=(tag,))

    def obtener_usuario_seleccionado():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            usuario_id = int(valores[0])
            return usuarios.find_one({"usuario_id": usuario_id})
        return None

    def eliminar_usuario():
        usuario = obtener_usuario_seleccionado()
        if usuario:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar el usuario '{usuario['username']}'?")
            if confirm:
                usuarios.delete_one({"usuario_id": usuario['usuario_id']})
                cargar_usuarios()
                messagebox.showinfo("Eliminado", "Usuario eliminado correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione un usuario.")

    def abrir_formulario_usuario(titulo_ventana, usuario_existente=None):
        def guardar_usuario():
            try:
                nuevo_usuario = {
                    "usuario_id": int(entry_id.get()),
                    "username": entry_username.get(),
                    "password_hash": entry_password_hash.get(),
                    "email": entry_email.get(),
                    "rol": combo_rol.get(),
                    "activo": var_activo.get(),
                    "fecha_creacion": entry_fecha_creacion.get(),
                    "ultimo_acceso": entry_ultimo_acceso.get() if entry_ultimo_acceso.get() else None
                }
                if usuario_existente:
                    usuarios.update_one({"usuario_id": usuario_existente["usuario_id"]}, {"$set": nuevo_usuario})
                    messagebox.showinfo("Actualizado", "Usuario actualizado.")
                else:
                    if usuarios.find_one({"usuario_id": nuevo_usuario["usuario_id"]}):
                        messagebox.showerror("Error", "usuario_id ya existe.")
                        return
                    usuarios.insert_one(nuevo_usuario)
                    messagebox.showinfo("Agregado", "Usuario agregado.")
                ventana_form.destroy()
                cargar_usuarios()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x450")
        crear_fondo_animado(ventana_form, "./fondos/fondo7.gif", (400, 450))
        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Username:").pack()
        entry_username = Entry(ventana_form)
        entry_username.pack()

        Label(ventana_form, text="Password Hash:").pack()
        entry_password_hash = Entry(ventana_form)
        entry_password_hash.pack()

        Label(ventana_form, text="Email:").pack()
        entry_email = Entry(ventana_form)
        entry_email.pack()

        Label(ventana_form, text="Rol:").pack()
        combo_rol = ttk.Combobox(ventana_form, values=["cliente", "administrador"], state="readonly")
        combo_rol.pack()

        var_activo = tk.BooleanVar()
        chk_activo = Checkbutton(ventana_form, text="Activo", variable=var_activo)
        chk_activo.pack()

        Label(ventana_form, text="Fecha Creación (YYYY-MM-DD):").pack()
        entry_fecha_creacion = Entry(ventana_form)
        entry_fecha_creacion.pack()

        Label(ventana_form, text="Último Acceso (YYYY-MM-DD o vacío):").pack()
        entry_ultimo_acceso = Entry(ventana_form)
        entry_ultimo_acceso.pack()

        if usuario_existente:
            entry_id.insert(0, usuario_existente['usuario_id'])
            entry_id.config(state="disabled")
            entry_username.insert(0, usuario_existente['username'])
            entry_password_hash.insert(0, usuario_existente['password_hash'])
            entry_email.insert(0, usuario_existente['email'])
            combo_rol.set(usuario_existente['rol'])
            var_activo.set(usuario_existente.get('activo', False))
            entry_fecha_creacion.insert(0, usuario_existente['fecha_creacion'])
            entry_ultimo_acceso.insert(0, usuario_existente.get('ultimo_acceso') or "")

        Button(ventana_form, text="Guardar", command=guardar_usuario).pack(pady=10)

    def crear_usuario():
        abrir_formulario_usuario("Agregar Usuario")

    def editar_usuario():
        usuario = obtener_usuario_seleccionado()
        if usuario:
            abrir_formulario_usuario("Editar Usuario", usuario)
        else:
            messagebox.showwarning("Aviso", "Seleccione un usuario.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Usuarios - Sesión: {username_sesion}")
    ventana.geometry("900x600")
    crear_fondo_animado(ventana, "./fondos/fondo4.gif", (900, 600))
    Label(ventana, text="Usuarios registrados", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Username", "Email", "Rol", "Activo", "Fecha Creación", "Último Acceso")

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

    Button(boton_frame, text="Agregar", width=15, command=crear_usuario).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_usuario).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_usuario).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_usuarios).grid(row=0, column=3, padx=5)

    cargar_usuarios()
    ventana.mainloop()


