# Importación de módulos necesarios
import os  # Para manejar rutas y archivos
import shutil  # Para copiar y mover archivos
import threading  # Para ejecutar tareas en hilos separados
import tkinter as tk  # Para crear interfaces gráficas
from tkinter import filedialog  # Para abrir un explorador de archivos
from tkinter import messagebox  # Para mostrar mensajes emergentes

import pyttsx3  # Para la síntesis de voz
from PIL import Image, ImageTk  # Para manejar imágenes

# Inicialización del narrador de texto
narrador = pyttsx3.init()

# Función para narrar texto utilizando un hilo separado
def narrar_texto(texto):
    """
    Permite que el chatbot hable en voz alta el texto proporcionado.
    Se utiliza un hilo separado para evitar que comience a hablar a
    la vez que se lanza la interfaz
    """
    def narrar():
        narrador.say(texto)
        narrador.runAndWait()

    # Crear y ejecutar el hilo para la narración
    hilo = threading.Thread(target=narrar)
    hilo.start()

# Función para seleccionar una imagen desde el explorador de archivos
def seleccionar_imagen():
    """
    Abre un cuadro de diálogo que permite seleccionar un archivo de imagen.
    Solo acepta formatos específicos: .png, .jpg, .jpeg, .gif.
    Devuelve la ruta del archivo seleccionado o None si no se selecciona nada.
    """
    ruta_imagen = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.gif")]
    )
    return ruta_imagen if ruta_imagen else None

# Función para cargar las respuestas desde un archivo de texto
def cargar_respuestas(archivo):
    """
    Lee un archivo de texto con claves y respuestas, y las almacena en un diccionario.
    Cada entrada contiene una clave binaria y las respuestas (breve y detallada).
    """
    respuestas = {}
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if ":" in linea and "||" in linea:
                    # Separar la clave y las respuestas
                    clave, respuestas_texto = map(str.strip, linea.split(":", 1))
                    breve, detallada = map(str.strip, respuestas_texto.split("||"))
                    respuestas[clave] = {"breve": breve, "detallada": detallada}
                elif ":" in linea:  # Caso especial: claves sin respuestas
                    clave = linea.split(":")[0].strip()
                    respuestas[clave] = {"breve": "", "detallada": ""}
    except FileNotFoundError:
        print(f"Error: el archivo '{archivo}' no se encontró.")
    except Exception as e:
        print(f"Ocurrió un error al cargar las respuestas: {e}")
    return respuestas

# Función para guardar o editar respuestas en el archivo de conocimiento
def editar_respuesta(archivo, clave, breve, detallada):
    """
    Actualiza o agrega una entrada de respuesta al archivo de conocimiento.
    Si la clave ya existe, se sobrescribe su contenido.
    """
    try:
        lineas_actualizadas = []
        with open(archivo, "r", encoding="utf-8") as f:
            for linea in f:
                if linea.startswith(clave + ":"):
                    # Sobrescribir la línea correspondiente a la clave
                    lineas_actualizadas.append(f"{clave}: {breve} || {detallada}\n")
                else:
                    lineas_actualizadas.append(linea)
        with open(archivo, "w", encoding="utf-8") as f:
            # Escribir las líneas actualizadas en el archivo
            f.writelines(lineas_actualizadas)
    except Exception as e:
        print(f"Error al editar la respuesta: {e}")

# Función para cargar una imagen basada en la clave binaria
def cargar_imagen(clave):
    """
    Busca una imagen en la carpeta "Imagenes" con el nombre correspondiente a la clave binaria.
    Si encuentra la imagen, la redimensiona al 25% de su tamaño original.
    Devuelve la imagen redimensionada en formato PhotoImage o None si no se encuentra.
    """
    ruta_imagen = os.path.join("Imagenes", f"{clave}.png")
    if os.path.exists(ruta_imagen):
        imagen = Image.open(ruta_imagen)
        nuevo_tamano = (int(imagen.width * 0.25), int(imagen.height * 0.25))
        imagen_redimensionada = imagen.resize(nuevo_tamano)
        return ImageTk.PhotoImage(imagen_redimensionada)
    return None

# Archivo de conocimiento que contiene las respuestas
archivo_respuestas = "./BaseDeConocimiento.txt"
# Cargar las respuestas existentes en un diccionario
respuestas = cargar_respuestas(archivo_respuestas)

# Diccionario de preguntas y sus respuestas posibles (codificadas en binario)
preguntas = {
    "estado": {"triste": "00", "ansioso/a": "01", "aburrido/a": "10", "normal": "11"},
    "amigos": {"muy bien": "00", "regular": "01", "no tengo amigos": "10", "mal": "11"},
    "familia": {"estable y de apoyo": "00", "a veces discutimos mucho": "01", "es conflictiva y no tengo mucho contacto con ellos": "10"},
    "apoyo_externo": {"sí, recibo ayuda profesional": "00", "no, pero lo estoy considerando": "01", "no, no sé por dónde empezar": "10", "no lo necesito": "11"},
}

# Función para generar una clave binaria basada en las respuestas del usuario
def generar_clave_binaria(respuestas_usuario):
    """
    Combina las respuestas del usuario (en binario) para generar una clave única.
    La clave se usa para acceder al conocimiento.
    """
    return (
        preguntas["estado"][respuestas_usuario["estado"]] +
        preguntas["amigos"][respuestas_usuario["amigos"]] +
        preguntas["familia"][respuestas_usuario["familia"]] +
        preguntas["apoyo_externo"][respuestas_usuario["apoyo_externo"]]
    )

# Función para mostrar la respuesta breve y detallada basada en las respuestas del usuario
def mostrar_respuesta(respuestas_usuario):
    """
    Muestra una ventana emergente con la respuesta breve correspondiente a la clave binaria generada
    a partir de las respuestas del usuario. Si la respuesta tiene una versión detallada,
    ofrece un botón para mostrarla en una ventana separada.
    También muestra la imagen asociada a la clave si está disponible.
    """
    clave = generar_clave_binaria(respuestas_usuario)
    if clave in respuestas:
        # Recuperar las respuestas breve y detallada asociadas a la clave
        respuesta_breve = respuestas[clave].get("breve", "")
        respuesta_detallada = respuestas[clave].get("detallada", "")
        imagen = cargar_imagen(clave)  # Cargar la imagen asociada a la clave

        def mostrar_detalles():
            """
            Muestra una ventana con la respuesta detallada y la imagen asociada (si existe).
            También narra la respuesta detallada.
            """
            narrar_texto(respuesta_detallada)
            ventana_detalle = tk.Toplevel(root)
            ventana_detalle.title("Respuesta detallada")
            tk.Label(ventana_detalle, text=respuesta_detallada, wraplength=400).pack(pady=10)
            if imagen:
                etiqueta_imagen = tk.Label(ventana_detalle, image=imagen)
                etiqueta_imagen.pack(pady=10)
                ventana_detalle.image = imagen  # Prevenir que la imagen sea recolectada por el recolector de basura
            tk.Button(ventana_detalle, text="Aceptar", command=ventana_detalle.destroy).pack(pady=10)

        if respuesta_breve:
            # Mostrar la respuesta breve en una ventana emergente
            ventana = tk.Toplevel(root)
            ventana.title("Respuesta breve")
            tk.Label(ventana, text=respuesta_breve, wraplength=400).pack(pady=10)
            if imagen:
                etiqueta_imagen = tk.Label(ventana, image=imagen)
                etiqueta_imagen.pack(pady=10)
                ventana.image = imagen  # Prevenir que la imagen sea recolectada por el recolector de basura
            if respuesta_detallada:
                # Botón para mostrar la respuesta detallada si está disponible
                tk.Button(ventana, text="Detalles", command=mostrar_detalles).pack(pady=5)
            tk.Button(ventana, text="Aceptar", command=ventana.destroy).pack(pady=10)
            narrar_texto(respuesta_breve)  # Narrar la respuesta breve
        else:
            # Mensaje en caso de no tener respuesta breve para la clave generada
            mensaje = "No cuento con el conocimiento suficiente como para ayudarte con esa respuesta."
            narrar_texto(mensaje)

            # Crear una ventana emergente para mostrar el mensaje
            ventana_sin_respuesta = tk.Toplevel(root)
            ventana_sin_respuesta.title("Sin conocimiento")
            tk.Label(ventana_sin_respuesta, text=mensaje, wraplength=400).pack(pady=10)

            # Botón para agregar conocimiento
            tk.Button(
                ventana_sin_respuesta,
                text="Agregar conocimiento",
                command=lambda: agregar_conocimiento(respuestas_usuario)
            ).pack(pady=10)

            tk.Button(ventana_sin_respuesta, text="Cerrar", command=ventana_sin_respuesta.destroy).pack(pady=10)


# Función para agregar conocimiento al archivo y actualizar las respuestas
def agregar_conocimiento(respuestas_usuario):
    """
    Permite agregar una nueva respuesta (breve y detallada) al conocimiento del chatbot.
    También ofrece la opción de asociar una imagen a la clave generada.
    """
    def ingresar_conocimiento():
        """
        Valida los campos de entrada, agrega la nueva respuesta al archivo de conocimiento,
        y opcionalmente asocia una imagen seleccionada a la clave.
        """
        breve = entrada_breve.get().strip()
        detallada = entrada_detallada.get().strip()
        clave = generar_clave_binaria(respuestas_usuario)

        if clave in respuestas and (respuestas[clave]["breve"] or respuestas[clave]["detallada"]):
            # Si la clave ya tiene respuestas asociadas, muestra una advertencia
            mensaje = "Ya se cuenta con conocimiento para esta combinación de respuestas."
            narrar_texto(mensaje)
            messagebox.showwarning("Duplicado", mensaje)
        elif breve and detallada:
            # Seleccionar una imagen asociada
            ruta_imagen = seleccionar_imagen()
            if ruta_imagen:
                nueva_ruta_imagen = os.path.join("Imagenes", f"{clave}.png")
                try:
                    # Copiar la imagen seleccionada a la carpeta "Imagenes" con el nombre correspondiente a la clave
                    shutil.copy(ruta_imagen, nueva_ruta_imagen)
                except Exception as e:
                    mensaje = f"Error al copiar la imagen: {e}"
                    narrar_texto(mensaje)
                    messagebox.showerror("Error", mensaje)
                    return

            # Guardar las respuestas en el archivo de conocimiento
            editar_respuesta(archivo_respuestas, clave, breve, detallada)
            # Recargar el conocimiento para reflejar los cambios
            respuestas.update(cargar_respuestas(archivo_respuestas))
            mensaje = "Conocimiento agregado correctamente."
            narrar_texto(mensaje)
            messagebox.showinfo("Éxito", mensaje)
            ventana_agregar.destroy()
        else:
            # Mensaje de error si los campos de texto están vacíos
            mensaje = "Por favor, completa ambos campos."
            narrar_texto(mensaje)
            messagebox.showerror("Error", mensaje)

    # Crear una ventana emergente para agregar conocimiento
    ventana_agregar = tk.Toplevel(root)
    ventana_agregar.title("Agregar conocimiento")
    tk.Label(ventana_agregar, text="Respuesta breve:").pack(pady=5)
    entrada_breve = tk.Entry(ventana_agregar, width=50)
    entrada_breve.pack(pady=5)
    tk.Label(ventana_agregar, text="Respuesta detallada:").pack(pady=5)
    entrada_detallada = tk.Entry(ventana_agregar, width=50)
    entrada_detallada.pack(pady=5)

    # Botón para ingresar el conocimiento (incluye la selección de imagen)
    tk.Button(ventana_agregar, text="Seleccionar Imagen y Guardar Conocimiento", command=ingresar_conocimiento).pack(pady=10)

# Configuración de la ventana principal de la aplicación
root = tk.Tk()
root.title("Chatbot de Apoyo Emocional")

# Variables que almacenan las respuestas seleccionadas por el usuario
estado_var = tk.StringVar(value="triste")
amigos_var = tk.StringVar(value="muy bien")
familia_var = tk.StringVar(value="estable y de apoyo")
apoyo_externo_var = tk.StringVar(value="sí, recibo ayuda profesional")

# Crear los menús desplegables para capturar las respuestas del usuario
tk.Label(root, text="¿Cómo te sientes la mayor parte del tiempo?").pack()
tk.OptionMenu(root, estado_var, *preguntas["estado"].keys()).pack()

tk.Label(root, text="¿Cómo te llevas con tus amigos?").pack()
tk.OptionMenu(root, amigos_var, *preguntas["amigos"].keys()).pack()

tk.Label(root, text="¿Cómo es tu relación con tu familia?").pack()
tk.OptionMenu(root, familia_var, *preguntas["familia"].keys()).pack()

tk.Label(root, text="¿Has buscado apoyo externo?").pack()
tk.OptionMenu(root, apoyo_externo_var, *preguntas["apoyo_externo"].keys()).pack()

# Botón para procesar las respuestas y mostrar la respuesta correspondiente
tk.Button(root, text="Enviar", command=lambda: mostrar_respuesta({
    "estado": estado_var.get(),
    "amigos": amigos_var.get(),
    "familia": familia_var.get(),
    "apoyo_externo": apoyo_externo_var.get()
})).pack(pady=10)

# Inicia el bucle principal de la interfaz gráfica
root.mainloop()
