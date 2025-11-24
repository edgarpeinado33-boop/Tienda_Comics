import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
import os
from db_config import get_db
from cliente_crud_1 import abrir_crud_clientes_1
from admin_crud import abrir_crud_administradores
import qrcode
from PIL import ImageTk


db = get_db()
usuarios = db["Usuarios"]

def generar_qr():
    ## URL de archivo compartido (Drive, Dropbox, etc.)
    url_zip_drive = "https://drive.google.com/file/d/1ZPL3Y_6na7RmPNCqj4e4xCsiN4QdegkN/view?usp=sharing" ## <-- Pega aquí el enlace de tu ZIP

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url_zip_drive)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    ventana_qr = tk.Toplevel(ventana)
    ventana_qr.title("QR para descargar ZIP")
    ventana_qr.geometry("300x300")

    img = img.resize((280, 280))
    img_tk = ImageTk.PhotoImage(img)

    label_qr = tk.Label(ventana_qr, image=img_tk)
    label_qr.image = img_tk
    label_qr.pack(padx=10, pady=10)

def autenticar():
    username = entry_usuario.get()
    password = entry_contrasena.get()

    user = usuarios.find_one({
        "username": username,
        "password_hash": password,
        "activo": True
    })

    if user:
        ventana.destroy()
        if user["rol"] == "cliente":
            abrir_crud_clientes_1(user["username"])
        elif user["rol"] == "administrador":
            abrir_crud_administradores(user["username"])
        else:
            messagebox.showwarning("Error", "Rol desconocido.")
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

def registrar_usuario():
    def guardar_usuario():
        username = entry_ruser.get()
        password = entry_rpass.get()
        email = entry_remail.get()

        if not username or not password or not email:
            messagebox.showwarning("Campos vacíos", "Completa todos los campos.")
            return

        if usuarios.find_one({"username": username}):
            messagebox.showerror("Error", "El nombre de usuario ya existe.")
            return

        nuevo_usuario = {
            "usuario_id": usuarios.count_documents({}) + 1,
            "username": username,
            "password_hash": password,
            "email": email,
            "rol": "cliente",
            "activo": True,
            "fecha_creacion": "2025-05-15",
            "ultimo_acceso": None
        }

        usuarios.insert_one(nuevo_usuario)
        messagebox.showinfo("Registrado", "Usuario cliente registrado correctamente.")
        ventana_registro.destroy()

    ventana_registro = tk.Toplevel(ventana)
    ventana_registro.title("Registro de Cliente")
    ventana_registro.geometry("350x300")

    fuente = ("Arial", 12)

    tk.Label(ventana_registro, text="Nombre de Usuario", font=fuente).pack(pady=5)
    entry_ruser = tk.Entry(ventana_registro, font=fuente)
    entry_ruser.pack()

    tk.Label(ventana_registro, text="Contraseña", font=fuente).pack(pady=5)
    entry_rpass = tk.Entry(ventana_registro, show="*", font=fuente)
    entry_rpass.pack()

    tk.Label(ventana_registro, text="Email", font=fuente).pack(pady=5)
    entry_remail = tk.Entry(ventana_registro, font=fuente)
    entry_remail.pack()

    tk.Button(ventana_registro, text="Registrar", command=guardar_usuario, font=fuente, bg="#4CAF50", fg="white").pack(pady=15)

ventana = tk.Tk()
ventana.title("Login - Komado Comics")
ventana.geometry("600x400")
ventana.resizable(False, False)


gif_path = os.path.join(os.path.dirname(__file__), "fondos", "fondo.gif")
gif = Image.open(gif_path)

frames = [ImageTk.PhotoImage(frame.resize((600, 400), Image.LANCZOS)) for frame in ImageSequence.Iterator(gif)]

fondo_label = tk.Label(ventana)
fondo_label.place(x=0, y=0, relwidth=1, relheight=1)

def animar(ind=0):
    if fondo_label.winfo_exists():
        fondo_label.configure(image=frames[ind])
        ventana.after(100, animar, (ind + 1) % len(frames))

animar()


frame_login = tk.Frame(ventana, bg="#FFFFFF", bd=3, relief="ridge")
frame_login.place(relx=0.5, rely=0.5, anchor="center")

for i in range(4):
    frame_login.grid_rowconfigure(i, pad=5)

tk.Label(frame_login, text="Bienvenidos a Komado Comics", font=("Arial Black", 18), fg="#C0392B", bg="#FFFFFF").pack(pady=(15, 20))

fuente = ("Arial", 14)

tk.Label(frame_login, text="Usuario", font=fuente, bg="#FFFFFF").pack()
entry_usuario = tk.Entry(frame_login, font=fuente, width=25)
entry_usuario.pack(pady=5)

tk.Label(frame_login, text="Contraseña", font=fuente, bg="#FFFFFF").pack()
entry_contrasena = tk.Entry(frame_login, show="*", font=fuente, width=25)
entry_contrasena.pack(pady=5)

tk.Button(frame_login, text="Iniciar sesión", command=autenticar, font=fuente, bg="#2980B9", fg="white", width=20).pack(pady=10)
tk.Button(frame_login, text="Registrarse", command=registrar_usuario, font=fuente, bg="#F1C40F", fg="black", width=20).pack(pady=(0, 15))
tk.Button(frame_login, text="Generar QR descarga ZIP", command=generar_qr, font=fuente, bg="#27AE60", fg="white", width=25).pack(pady=(0, 15))
tk.Button(frame_login, text="Cancelar", command=ventana.destroy, font=fuente, bg="#E74C3C", fg="white", width=20).pack(pady=(0, 15))

ventana.mainloop()