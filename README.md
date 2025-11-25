# SyntaxTerror
### Video Demo: https://youtu.be/pllW9lK0Gf8
### Description:
Nuestro proyecto consiste en una aplicación web de mensajería utilizando flask como framework
y web-sockets para realizar la conexión entre los usuarios. La aplicación contiene un sistema
de creación de salas mediante códigos de unión mostradas en el header de la sección del chat.
Todas las salas a las que está unida el usuario se ven desplegadas verticalmente en una
"sección para el usuario", donde además se puede observar la foto de perfil y nombre del
usuario.


Entre las características de la aplicación se pueden destacar:
- Hashing de contraseñas utilizando werkzeug.security
- El sistema de sesiones es manejado por la librería flask_session
- Confirmación de cuenta mediante enlace enviado al correo electrónico, utilizando flask-mail
e itsdangerous.
- Validaciones mediante mensajes flash utilizando iziToast
- Utilización del servicio de almacenamiento en la nube Cloudinary para fotos de perfil/grupo
- Consulta a la base de datos utilizando sintaxis sqlite3 mediante la librería de cs50 para python
- Creación de códigos para salas apoyándonos de las librerías random y string
- Validación de contraseña segura utilizando la librería re (función desactivada para efectos demostrativos)

La aplicación cuenta con seis rutas principales: /, register, login, logout, chat, chat/<room_code>, y rutas
complementarias como las utilizadas para confirmar la cuenta con un token enviado al email, o la de crear y
unirse a salas.

El estilo de la aplicación está basado en la interfaz de Discord; lo cual se ve reflejado en la ruta principal,
y en la de chats; se intenta simular la interfaz de chat de discord. Se hizo uso de plantillas para login,
register, /, y chat; las cuales contienen sus estilos en static.

El archivo helpers.py contiene el decorador "login_required" para manejar que el acceso a la página de chats
sea permitido únicamente si hay un usuario en la sesión. Del mismo modo, contiene la función validate_password,
utilizada para procurar que la contraseña que se introduce es compleja (segura).

El archivo proyecto.db es la base de datos de la aplicación, y fue modificada utilizando la extensión SqlTools
para VSCode; para realizar consultas sin ocupar un archivo del tipo "consultas.sql".

Cabe resaltar que no se hizo uso de archivos javascript; por lo que no existe una carpeta "script" en /static.
El código javascript se encuentra dentro de etiquetas script en el html, lo mismo para varios estilos con style.

También está el archivo "requirements.txt", el cual lista todas las librerías utilizadas por la aplicación y que
necesitan ser instaladas para que funcione correctamente.

Por último, app.py es el archivo python de la aplicación donde se configura la aplicación mediante flask. Obsérvese
que se utiliza la librería flask-socketio para tratar con los web-sockets.

Implementaciones futuras:
- Chatbot utilizando la librería openai
- Reproducción de música utilizando yt-dlp y ffmpeg
- Edición de nombres de usuario y salas, y fotos de usuarios y salas.
- Mejora del estilo (hacerlo responsivo, mejorar el css...)
