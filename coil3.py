import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import math
import pyodbc
import datetime

# Definir la conexion a la base de datos
conn_str = (
    'DRIVER={SQL Server};'
    'SERVER=DESKTOP-L3S0G6J\\SQLEXPRESS;'  # Cambia a tu servidor
    'DATABASE=usuario;'  # Nombre de tu base de datos
    'UID=stefany;'  # Usuario de tu base de datos
    'PWD=terry;'  # Contraseña
)

# Establecer la conexion a la base de datos
conexion = pyodbc.connect(conn_str)
cursor = conexion.cursor()

# Variables globales para almacenar los datos del paciente
usuario_actual = {}

# Variables globales para el seguimiento del tiempo de la postura
ultima_postura = None
hora_inicio_postura = None


# Funcion para registrar un nuevo usuario
def registrar_usuario(entry_primer_nombre, entry_segundo_nombre, entry_apellido_paterno, entry_apellido_materno, entry_edad, entry_sexo, entry_tipo_usuario, entry_username, entry_password, registro_window, label_info_usuario):
    primer_nombre = entry_primer_nombre.get()
    segundo_nombre = entry_segundo_nombre.get() or None
    apellido_paterno = entry_apellido_paterno.get()
    apellido_materno = entry_apellido_materno.get() or None
    edad = entry_edad.get()
    sexo = entry_sexo.get()
    tipo_usuario = entry_tipo_usuario.get()
    username = entry_username.get()
    password = entry_password.get()

    query = "INSERT INTO pacientes (primer_nombre, segundo_nombre, apellido_paterno, apellido_materno, edad, sexo, tipo_usuario, username, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    values = (primer_nombre, segundo_nombre, apellido_paterno, apellido_materno, edad, sexo, tipo_usuario, username, password)

    try:
        cursor.execute(query, values)
        conexion.commit()
        messagebox.showinfo("Éxito", "Usuario registrado exitosamente")
        registro_window.destroy()
        mostrar_formulario_login(label_info_usuario)
    except pyodbc.IntegrityError:
        messagebox.showerror("Error", "El usuario ya existe")

# Funcion para mostrar la informacion del usuario
def mostrar_info_usuario(label_info_usuario):
    segundo_nombre = usuario_actual['segundo_nombre'] if usuario_actual['segundo_nombre'] else ""
    apellido_materno = usuario_actual['apellido_materno'] if usuario_actual['apellido_materno'] else ""
    nombre_completo = f"{usuario_actual['primer_nombre']} {segundo_nombre} {usuario_actual['apellido_paterno']} {apellido_materno}".strip()
    label_info_usuario.config(text=f"Nombre: {nombre_completo} | Edad: {usuario_actual['edad']} años | Tipo de Usuario: {usuario_actual['tipo_usuario']}")

# Funcion para calcular el angulo entre tres puntos
def calcular_angulo(a, b, c):
    angulo = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    )
    angulo = abs(angulo)
    if angulo > 180.0:
        angulo = 360 - angulo
    return angulo

# Funcion para detectar malas y buenas posturas basadas en angulos y medir el tiempo de cada postura
def detectar_mala_buena_postura(resultados, frame):
    global ultima_postura, hora_inicio_postura

    landmarks = resultados.pose_landmarks.landmark

    # Obtener las coordenadas de las articulaciones clave
    hombro_izquierdo = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
    cadera_izquierda = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
    rodilla_izquierda = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
    codo_izquierdo = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
    muneca_izquierda = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]
    oreja_izquierda = [landmarks[mp_pose.PoseLandmark.LEFT_EAR].x, landmarks[mp_pose.PoseLandmark.LEFT_EAR].y]
    tobillo_izquierdo = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]

    # Calcular ángulos importantes
    angulo_hombro_cadera_rodilla = calcular_angulo(hombro_izquierdo, cadera_izquierda, rodilla_izquierda)
    angulo_hombro_codo_muneca = calcular_angulo(hombro_izquierdo, codo_izquierdo, muneca_izquierda)
    angulo_oreja_hombro_cadera = calcular_angulo(oreja_izquierda, hombro_izquierdo, cadera_izquierda)
    angulo_cadera_rodilla_tobillo = calcular_angulo(cadera_izquierda, rodilla_izquierda, tobillo_izquierdo)
    angulo_codo_hombro_cadera = calcular_angulo(codo_izquierdo, hombro_izquierdo, cadera_izquierda)

    # Determinar el tipo de postura
    tipo_postura = "Buena postura"
    if angulo_hombro_cadera_rodilla < 160:
        cv2.putText(frame, "Mala postura: Cuerpo inclinado hacia adelante", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        tipo_postura = "Cuerpo inclinado hacia adelante"
    elif angulo_hombro_cadera_rodilla >= 160 and angulo_hombro_cadera_rodilla <= 180:
        cv2.putText(frame, "Buena postura: Cuerpo derecho", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    if angulo_hombro_codo_muneca > 150:
        cv2.putText(frame, "Mala postura: Brazo mal posicionado", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        tipo_postura = "Brazo mal posicionado"
    elif angulo_hombro_codo_muneca <= 150 and angulo_hombro_codo_muneca >= 90:
        cv2.putText(frame, "Buena postura: Brazo en buena posicion", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    if angulo_oreja_hombro_cadera < 140:
        cv2.putText(frame, "Mala postura: Cabeza inclinada hacia adelante", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        tipo_postura = "Cabeza inclinada hacia adelante"
    elif angulo_oreja_hombro_cadera >= 140 and angulo_oreja_hombro_cadera <= 180:
        cv2.putText(frame, "Buena postura: Cabeza bien alineada", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    if angulo_cadera_rodilla_tobillo < 150:
        cv2.putText(frame, "Mala postura: Piernas mal alineadas", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        tipo_postura = "Piernas mal alineadas"
    elif angulo_cadera_rodilla_tobillo >= 150 and angulo_cadera_rodilla_tobillo <= 180:
        cv2.putText(frame, "Buena postura: Piernas bien alineadas", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    if angulo_codo_hombro_cadera < 90:
        cv2.putText(frame, "Mala postura: Brazo superior en mala posicion", (10, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        tipo_postura = "Brazo superior en mala posicion"
    elif angulo_codo_hombro_cadera >= 90 and angulo_codo_hombro_cadera <= 180:
        cv2.putText(frame, "Buena postura: Brazo superior bien alineado", (10, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Registrar el tiempo de la postura
    if tipo_postura != ultima_postura:
        if ultima_postura is not None:
            # Calcular el tiempo en que se mantuvo la postura
            duracion = (datetime.datetime.now() - hora_inicio_postura).total_seconds()
            guardar_postura_en_db(ultima_postura, duracion)
        
        # Actualizar la postura y la hora de inicio
        ultima_postura = tipo_postura
        hora_inicio_postura = datetime.datetime.now()
def guardar_postura_en_db(tipo_postura, duracion):
    if usuario_actual:
        try:
            query = "INSERT INTO historial_posturas (id_paciente, tipo_postura, duracion, fecha) VALUES (?, ?, ?, ?)"
            fecha_actual = datetime.datetime.now()
            cursor.execute(query, (usuario_actual['id'], tipo_postura, duracion, fecha_actual))
            conexion.commit()
        except Exception as e:
            print(f"Error al guardar la postura: {e}")


# Funcion para iniciar sesion
def iniciar_sesion(entry_username, entry_password, label_info_usuario):
    username = entry_username.get()
    password = entry_password.get()

    query = "SELECT * FROM pacientes WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()

    if result:
        global usuario_actual
        usuario_actual = {
            "id": result[0],
            "primer_nombre": result[1],
            "segundo_nombre": result[2],
            "apellido_paterno": result[3],
            "apellido_materno": result[4],
            "edad": result[5],
            "sexo": result[6],
            "tipo_usuario": result[7],
            "username": result[8]
        }
        messagebox.showinfo("Exito", f"Bienvenido, {usuario_actual['primer_nombre']}")
        root.deiconify()
        login_window.destroy()
        mostrar_info_usuario(label_info_usuario)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

# Funcion para mostrar el historial de posturas
def mostrar_historial_posturas():
    if not usuario_actual:
        messagebox.showerror("Error", "Debe iniciar sesion para ver el historial de posturas")
        return

    query = "SELECT tipo_postura, duracion, fecha FROM historial_posturas WHERE id_paciente = ? ORDER BY fecha DESC"
    cursor.execute(query, (usuario_actual['id'],))
    resultados = cursor.fetchall()

    historial_window = tk.Toplevel(root)
    historial_window.title("Historial de Posturas")

    if resultados:
        tk.Label(historial_window, text="Historial de Posturas", font=("Helvetica", 14)).pack(pady=10)
        for postura in resultados:
            tipo_postura, duracion, fecha = postura
            texto = f"Postura: {tipo_postura}, Duracion: {duracion} segundos, Fecha: {fecha}"
            tk.Label(historial_window, text=texto, font=("Helvetica", 10)).pack(anchor="w", padx=10)
    else:
        tk.Label(historial_window, text="No hay historial de posturas para este usuario.", font=("Helvetica", 10)).pack(pady=10)

# Funcion para iniciar sesion
def iniciar_sesion(entry_username, entry_password, label_info_usuario):
    username = entry_username.get()
    password = entry_password.get()

    # Consulta para verificar las credenciales
    query = "SELECT * FROM pacientes WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()

    if result:
        global usuario_actual
        usuario_actual = {
            "id": result[0],
            "primer_nombre": result[1],
            "segundo_nombre": result[2],
            "apellido_paterno": result[3],
            "apellido_materno": result[4],
            "edad": result[5],
            "sexo": result[6],
            "tipo_usuario": result[7],
            "username": result[8]
        }
        messagebox.showinfo("Exito", f"Bienvenido, {usuario_actual['primer_nombre']}")
        root.deiconify()
        login_window.destroy()
        mostrar_info_usuario(label_info_usuario)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

# Funcion para mostrar el historial de posturas
def mostrar_historial_posturas():
    if not usuario_actual:
        messagebox.showerror("Error", "Debe iniciar sesión para ver el historial de posturas")
        return

    query = "SELECT tipo_postura, duracion, fecha FROM historial_posturas WHERE id_paciente = ? ORDER BY fecha DESC"
    cursor.execute(query, (usuario_actual['id'],))
    resultados = cursor.fetchall()

    historial_window = tk.Toplevel(root)
    historial_window.title("Historial de Posturas")

    if resultados:
        tk.Label(historial_window, text="Historial de Posturas", font=("Helvetica", 14)).pack(pady=10)
        for postura in resultados:
            tipo_postura, duracion, fecha = postura
            texto = f"Postura: {tipo_postura}, Duración: {duracion} segundos, Fecha: {fecha}"
            tk.Label(historial_window, text=texto, font=("Helvetica", 10)).pack(anchor="w", padx=10)
    else:
        tk.Label(historial_window, text="No hay historial de posturas para este usuario.", font=("Helvetica", 10)).pack(pady=10)

        

# Interfaz grafica para el registro de usuarios
def mostrar_formulario_registro():
    root.withdraw()  # Ocultar la ventana principal mientras se registra un usuario

    registro_window = tk.Toplevel(root)
    registro_window.title("Registrar Usuario")

    tk.Label(registro_window, text="Primer Nombre:").grid(row=0, column=0, sticky="w")
    entry_primer_nombre = tk.Entry(registro_window)
    entry_primer_nombre.grid(row=0, column=1)

    tk.Label(registro_window, text="Segundo Nombre (Opcional):").grid(row=1, column=0, sticky="w")
    entry_segundo_nombre = tk.Entry(registro_window)
    entry_segundo_nombre.grid(row=1, column=1)

    tk.Label(registro_window, text="Primer Apellido:").grid(row=2, column=0, sticky="w")
    entry_apellido_paterno = tk.Entry(registro_window)
    entry_apellido_paterno.grid(row=2, column=1)

    tk.Label(registro_window, text="Segundo Apellido (Opcional):").grid(row=3, column=0, sticky="w")
    entry_apellido_materno = tk.Entry(registro_window)
    entry_apellido_materno.grid(row=3, column=1)

    tk.Label(registro_window, text="Edad:").grid(row=4, column=0, sticky="w")
    entry_edad = tk.Entry(registro_window)
    entry_edad.grid(row=4, column=1)

    tk.Label(registro_window, text="Sexo (M/F):").grid(row=5, column=0, sticky="w")
    entry_sexo = tk.Entry(registro_window)
    entry_sexo.grid(row=5, column=1)

    tk.Label(registro_window, text="Tipo de Usuario (Oficinista, Recuperación, Otro):").grid(row=6, column=0, sticky="w")
    entry_tipo_usuario = tk.Entry(registro_window)
    entry_tipo_usuario.grid(row=6, column=1)

    tk.Label(registro_window, text="Username:").grid(row=7, column=0, sticky="w")
    entry_username = tk.Entry(registro_window)
    entry_username.grid(row=7, column=1)

    tk.Label(registro_window, text="Contraseña:").grid(row=8, column=0, sticky="w")
    entry_password = tk.Entry(registro_window, show="*")
    entry_password.grid(row=8, column=1)

    tk.Button(registro_window, text="Registrar", command=lambda: registrar_usuario(entry_primer_nombre, entry_segundo_nombre, entry_apellido_paterno, entry_apellido_materno, entry_edad, entry_sexo, entry_tipo_usuario, entry_username, entry_password, registro_window, label_info_usuario)).grid(row=9, columnspan=2)

# Interfaz grafica para el inicio de sesion
def mostrar_formulario_login(label_info_usuario):
    global login_window
    login_window = tk.Toplevel(root)
    login_window.title("Iniciar Sesión")

    tk.Label(login_window, text="Username:").grid(row=0, column=0, sticky="w")
    entry_username = tk.Entry(login_window)
    entry_username.grid(row=0, column=1)

    tk.Label(login_window, text="Contraseña:").grid(row=1, column=0, sticky="w")
    entry_password = tk.Entry(login_window, show="*")
    entry_password.grid(row=1, column=1)

    tk.Button(login_window, text="Iniciar Sesión", command=lambda: iniciar_sesion(entry_username, entry_password, label_info_usuario)).grid(row=2, columnspan=2)

# Funcion que muestra las opciones al usuario para elegir entre iniciar sesion o registrarse
def mostrar_opciones(label_info_usuario):
    opciones_window = tk.Toplevel(root)
    opciones_window.title("Opciones")

    tk.Label(opciones_window, text="¿Ya tienes cuenta o deseas registrarte?").pack(pady=10)

    # Boton para iniciar sesion
    btn_iniciar_sesion = tk.Button(opciones_window, text="Iniciar Sesión", command=lambda: [opciones_window.destroy(), mostrar_formulario_login(label_info_usuario)])
    btn_iniciar_sesion.pack(pady=5)

    # Boton para registrarse
    btn_registrarse = tk.Button(opciones_window, text="Registrarse", command=lambda: [opciones_window.destroy(), mostrar_formulario_registro()])
    btn_registrarse.pack(pady=5)

# Configuracion de la interfaz grafica principal
root = tk.Tk()
root.title("Detección de Postura")

# Etiqueta para mostrar la informacion del usuario en la interfaz principal
label_info_usuario = tk.Label(root, text="Bienvenido, inicia sesión para ver tu información", font=("Helvetica", 12), pady=10)
label_info_usuario.pack()

btn_historial_posturas = tk.Button(root, text="Ver Historial de Posturas", command=mostrar_historial_posturas)
btn_historial_posturas.pack(pady=10)


# Mostrar el menu de opciones (Iniciar sesion o Registrarse)
root.withdraw()  # Ocultar la ventana principal hasta que el usuario tome una decision
mostrar_opciones(label_info_usuario)

# Inicializacion de la camara y configuracion de la deteccion de manos y poses
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing_hands = mp.solutions.drawing_utils

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing_poses = mp.solutions.drawing_utils

# Inicializacion de la camara
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    messagebox.showerror("Error", "No se pudo acceder a la cámara. Verifica que este conectada correctamente.")

# Funcion para procesar manos
def process_hands(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing_hands.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                            mp_drawing_hands.DrawingSpec(color=(0, 0, 0), thickness=2),
                                            mp_drawing_hands.DrawingSpec(color=(255, 255, 255), thickness=2))

# Funcion para procesar poses (cuerpo completo)
def process_full_body(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)
    if results.pose_landmarks:
        mp_drawing_poses.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                        mp_drawing_poses.DrawingSpec(color=(0, 255, 0), thickness=2),
                                        mp_drawing_poses.DrawingSpec(color=(0, 0, 255), thickness=2))
        detectar_mala_buena_postura(results, frame)

# Funcion para actualizar la camara
def actualizar_camara(label_cam):
    ret, frame = cap.read()
    if ret:
        process_hands(frame)
        process_full_body(frame)

        # Convertir el frame al formato correcto para Tkinter
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img_tk = ImageTk.PhotoImage(image=img)
        
        # Actualizar el label de la camara en tkinter
        label_cam.img_tk = img_tk  # Mantener la referencia a la imagen
        label_cam.config(image=img_tk)

    label_cam.after(10, actualizar_camara, label_cam)

# Configuracion de la interfaz grafica de la camara
frame_cam = tk.Frame(root)
frame_cam.pack()

label_cam = tk.Label(frame_cam)
label_cam.pack()

# Funcion para liberar la camara al cerrar la ventana
def on_closing():
    cap.release()  # Liberar la camara
    cv2.destroyAllWindows()  # Cerrar ventanas de OpenCV
    root.quit()

# Vincular el cierre de la ventana con la liberacion de la camara
root.protocol("WM_DELETE_WINDOW", on_closing)

# Comenzar a actualizar el feed de la camara
actualizar_camara(label_cam)

# Iniciar el bucle principal de Tkinter
root.mainloop()

# Liberar la camara y cerrar la ventana al salir
cap.release()
cv2.destroyAllWindows()
