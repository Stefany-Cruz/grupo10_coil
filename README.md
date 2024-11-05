# grupo10_coil
Asistente de corrección postural 

Guía para Ejecutar el Código en Visual Studio Code (VS Code) 
1.	Configura VS Code para tu Proyecto: Abre VS Code y selecciona "Open Folder" para abrir la carpeta de tu proyecto. Abre la terminal en VS Code (Ctrl + `) o de forma manual en la parte superior veras (...) aprieta ahí y te dará la opción de terminal donde darás click y luego donde dice nueva terminal. Instala las dependencias en este entorno virtual. Abre la Terminal o la línea de comandos. Asegúrate de tener Python instalado (puedes verificarlo ejecutando: python –version). Si no tienes Python, descárgalo e instálalo desde python.org. Para instalar las librerías necesarias en el entorno de desarrollo visual studio code debemos tener en cuenta que se deberá abrir una terminal para poder instalar las siguientes librerías:
•	pip install opencv-python # Para la biblioteca OpenCV pip install mediapipe # Para la biblioteca MediaPipe pip install pillow # Para la biblioteca PIL (Pillow) pip install pyodbc # Para la conexión con bases de datos usando ODBC
•	Detalles de las librerías:
o	 OpenCV (opencv-python): Se usa para procesamiento de imágenes y visión por computadora.
o	 MediaPipe (mediapipe): Útil para aplicaciones de reconocimiento de gestos y seguimiento de puntos clave. 
o	Pillow (pillow): Una biblioteca de procesamiento de imágenes en Python. pyodbc (pyodbc): Una biblioteca para conectarse y ejecutar consultas en bases de datos utilizando ODBC Notas Adicionales. 
o	Tkinter: No necesita instalación mediante pip, ya que es parte de la biblioteca estándar de Python y está incluida por defecto. math y datetime. @Estas son bibliotecas estándar de Python, por lo que tampoco requieren instalación.
Verifica que todas las librerías estén correctamente instaladas: Ejecuta: pip list y asegúrate de que las bibliotecas mencionadas estén en la lista.
2.	Detalles Sobre Cómo Configurar la Base de Datos Utilizando el Archivo base.txt Requisitos Previos:
Asegúrate de tener SQL Server instalado en tu máquina. Puedes descargarlo desde Microsoft SQL Server. Instala SQL Server Management Studio (SSMS) para administrar la base de datos. Configuración de la Base de Datos:
3.	Abre SQL Server Management Studio (SSMS) e inicia sesión en tu instancia de SQL Server. Crea una nueva base de datos: Haz clic derecho en "Bases de datos" en el panel izquierdo y selecciona "Nueva base de datos". Asigna un nombre a tu base de datos, por ejemplo: usuario. Ejecuta el archivo base.txt para crear las tablas. En SSMS, abre una nueva consulta. Copia y pega el contenido del archivo base.txt en la ventana de consulta. Asegúrate de que tu base de datos recién creada esté seleccionada en el menú desplegable de la base de datos y haz clic en "Ejecutar" Verifica que las tablas “pacientes” e “historial_posturas” se hayan creado correctamente revisando la estructura de la base de datos en SSMS.
4.	Ejecuta el Código: Abre coil3.py en VS Code. Asegúrate de que todas las importaciones no muestren errores (sin subrayados rojos). Haz clic en el botón "Run" o usa python coil3.py en la terminal de VS Code para ejecutar el script.
5.	si desea terminar de usa el programa solo haga clic en la "x". esto cerrara automáticamente el programa.
