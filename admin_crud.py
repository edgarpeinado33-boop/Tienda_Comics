import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, StringVar
from tkinter import ttk
from db_config import get_db
from cliente_crud import abrir_crud_clientes
from comic_crud import abrir_crud_comics
import subprocess
import sys
from PIL import Image, ImageTk, ImageSequence
import os
from autor_crud import abrir_crud_autores
from compra_crud import abrir_crud_compras
from detalle_venta_crud import abrir_crud_detalle_ventas
from ediciones_especiales_crud import abrir_crud_ediciones_especiales
from editoriales_crud import abrir_crud_editoriales
from eventos_crud import abrir_crud_eventos
from guionistas_crud import abrir_crud_guionistas
from idiomas_crud import abrir_crud_idiomas
from ilustradores_crud import abrir_crud_ilustradores
from personajes_crud import abrir_crud_personajes
from premios_crud import abrir_crud_premios
from resenas_crud import abrir_crud_resenas
from series_crud import abrir_crud_series
from ventas_crud import abrir_crud_ventas
from adaptacion_crud import abrir_crud_adaptaciones  
from tienda_crud import abrir_crud_tienda
from usuario_crud import abrir_crud_usuarios

db = get_db()
admins = db["Administradores"]

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

def abrir_crud_administradores(username):
    def cargar_admins():
        for row in tree.get_children():
            tree.delete(row)
        for i, admin in enumerate(admins.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                admin['admin_id'],
                admin['nombre'],
                admin['email'],
                admin['telefono'],
                admin['fecha_ingreso'],
                "Sí" if admin['activo'] else "No",
                admin['rol'],
                admin['username']
            ), tags=(tag,))
 
    def obtener_admin_seleccionado():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            admin_id = int(valores[0])
            return admins.find_one({"admin_id": admin_id})
        return None

    def eliminar_admin():
        admin = obtener_admin_seleccionado()
        if admin:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar a {admin['nombre']}?")
            if confirm:
                admins.delete_one({"admin_id": admin['admin_id']})
                cargar_admins()
                messagebox.showinfo("Eliminado", "Administrador eliminado correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione un administrador.")

    def abrir_formulario_admin(titulo, admin_existente=None):
        def guardar_admin():
            try:
                nuevo_admin = {
                    "admin_id": int(entry_id.get()),
                    "nombre": entry_nombre.get(),
                    "email": entry_email.get(),
                    "telefono": entry_telefono.get(),
                    "fecha_ingreso": entry_fecha.get(),
                    "activo": var_activo.get() == "1",
                    "rol": entry_rol.get(),
                    "username": entry_username.get()
                }

                if admin_existente:
                    admins.update_one({"admin_id": admin_existente["admin_id"]}, {"$set": nuevo_admin})
                    messagebox.showinfo("Actualizado", "Administrador actualizado.")
                else:
                    if admins.find_one({"admin_id": nuevo_admin["admin_id"]}):
                        messagebox.showerror("Error", "admin_id ya existe.")
                        return
                    admins.insert_one(nuevo_admin)
                    messagebox.showinfo("Agregado", "Administrador agregado.")

                ventana_form.destroy()
                cargar_admins()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo)
        ventana_form.geometry("400x400")
         
        crear_fondo_animado(ventana_form, "./fondos/fondo6.gif", (400, 400))
        
        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Nombre:").pack()
        entry_nombre = Entry(ventana_form)
        entry_nombre.pack()

        Label(ventana_form, text="Email:").pack()
        entry_email = Entry(ventana_form)
        entry_email.pack()

        Label(ventana_form, text="Teléfono:").pack()
        entry_telefono = Entry(ventana_form)
        entry_telefono.pack()

        Label(ventana_form, text="Fecha Ingreso (YYYY-MM-DD):").pack()
        entry_fecha = Entry(ventana_form)
        entry_fecha.pack()

        Label(ventana_form, text="Activo (1 = Sí, 0 = No):").pack()
        var_activo = StringVar()
        entry_activo = Entry(ventana_form, textvariable=var_activo)
        entry_activo.pack()

        Label(ventana_form, text="Rol:").pack()
        entry_rol = Entry(ventana_form)
        entry_rol.pack()

        Label(ventana_form, text="Username:").pack()
        entry_username = Entry(ventana_form)
        entry_username.pack()

        if admin_existente:
            entry_id.insert(0, admin_existente['admin_id'])
            entry_id.config(state="disabled")
            entry_nombre.insert(0, admin_existente['nombre'])
            entry_email.insert(0, admin_existente['email'])
            entry_telefono.insert(0, admin_existente['telefono'])
            entry_fecha.insert(0, admin_existente['fecha_ingreso'])
            var_activo.set("1" if admin_existente['activo'] else "0")
            entry_rol.insert(0, admin_existente['rol'])
            entry_username.insert(0, admin_existente['username'])

        Button(ventana_form, text="Guardar", command=guardar_admin).pack(pady=10)

    def cerrar_sesion():
      ventana.destroy()
      subprocess.Popen([sys.executable, "main.py"])
    def crear_admin():
        abrir_formulario_admin("Agregar Administrador")

    def editar_admin():
        admin = obtener_admin_seleccionado()
        if admin:
            abrir_formulario_admin("Editar Administrador", admin)
        else:
            messagebox.showwarning("Aviso", "Seleccione un administrador.")

    ventana = tk.Tk()
    ventana.title(f"CRUD Administradores - Sesión: {username}")
    ventana.geometry("980x600")
    

    ventana.resizable(False, False)

    
    ventana.wm_attributes('-transparentcolor', 'pink')  
    
    gif_path = os.path.join(os.path.dirname(__file__), "fondos", "fondo3.gif")
    gif = Image.open(gif_path)
    frames = [ImageTk.PhotoImage(frame.resize((1100, 600), Image.LANCZOS)) for frame in ImageSequence.Iterator(gif)]

    fondo_label = tk.Label(ventana, bg='pink')  
    fondo_label.place(x=0, y=0, relwidth=1, relheight=1)

    def animar(ind=0):
        if fondo_label.winfo_exists():
            fondo_label.configure(image=frames[ind])
            ventana.after(100, animar, (ind + 1) % len(frames))

    animar()

    Label(ventana, text="Administradores", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Nombre", "Email", "Teléfono", "Fecha Ingreso", "Activo", "Rol", "Username")

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

   
    Button(boton_frame, text="Agregar", width=15, command=crear_admin).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_admin).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_admin).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_admins).grid(row=0, column=3, padx=5)
    Button(boton_frame, text="Ir a Clientes", width=15, command=lambda: abrir_crud_clientes(username)).grid(row=0, column=4, padx=5)
    Button(boton_frame, text="Ir a Comics", width=15, command=lambda: abrir_crud_comics(username)).grid(row=0, column=5, padx=5)

    
    Button(boton_frame, text="Ir a Autores", width=15, command=lambda: abrir_crud_autores(username)).grid(row=1, column=0, padx=5, pady=5)
    Button(boton_frame, text="Ir a Compras", width=15, command=lambda: abrir_crud_compras(username)).grid(row=1, column=1, padx=5, pady=5)
    Button(boton_frame, text="Ir a Detalle Ventas", width=15, command=lambda: abrir_crud_detalle_ventas(username)).grid(row=1, column=2, padx=5, pady=5)
    Button(boton_frame, text="Ir a Ediciones Especiales", width=15, command=lambda: abrir_crud_ediciones_especiales(username)).grid(row=1, column=3, padx=5, pady=5)
    Button(boton_frame, text="Ir a Editoriales", width=15, command=lambda: abrir_crud_editoriales(username)).grid(row=1, column=4, padx=5, pady=5)
    Button(boton_frame, text="Ir a Eventos", width=15, command=lambda: abrir_crud_eventos(username)).grid(row=1, column=5, padx=5, pady=5)

    
    Button(boton_frame, text="Ir a Guionistas", width=15, command=lambda: abrir_crud_guionistas(username)).grid(row=2, column=0, padx=5, pady=5)
    Button(boton_frame, text="Ir a Idiomas", width=15, command=lambda: abrir_crud_idiomas(username)).grid(row=2, column=1, padx=5, pady=5)
    Button(boton_frame, text="Ir a Ilustradores", width=15, command=lambda: abrir_crud_ilustradores(username)).grid(row=2, column=2, padx=5, pady=5)
    Button(boton_frame, text="Ir a Personajes", width=15, command=lambda: abrir_crud_personajes(username)).grid(row=2, column=3, padx=5, pady=5)
    Button(boton_frame, text="Ir a Premios", width=15, command=lambda: abrir_crud_premios(username)).grid(row=2, column=4, padx=5, pady=5)
    Button(boton_frame, text="Ir a Reseñas", width=15, command=lambda: abrir_crud_resenas(username)).grid(row=2, column=5, padx=5, pady=5)

    
    Button(boton_frame, text="Ir a Series", width=15, command=lambda: abrir_crud_series(username)).grid(row=3, column=0, padx=5, pady=5)
    Button(boton_frame, text="Ir a Ventas", width=15, command=lambda: abrir_crud_ventas(username)).grid(row=3, column=1, padx=5, pady=5)
    Button(boton_frame, text="Ir a Adaptaciones", width=15, command=lambda: abrir_crud_adaptaciones(username)).grid(row=3, column=2, padx=5, pady=5)  
    Button(boton_frame, text="Ir a Tienda", width=15, command=lambda: abrir_crud_tienda(username)).grid(row=3, column=3, padx=5, pady=5)
    Button(boton_frame, text="Ir a Usuarios", width=15, command=lambda: abrir_crud_usuarios(username)).grid(row=3, column=4, padx=5, pady=5)
    
    Button(boton_frame, text="Cerrar Sesión", width=15, bg="red", fg="white", command=cerrar_sesion).grid(row=3, column=5, padx=5, pady=5)

    cargar_admins()
    ventana.mainloop()
