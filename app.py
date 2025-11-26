import os
import random
import string
from cs50 import SQL
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
from flask_session import Session
from flask_socketio import SocketIO, join_room, leave_room, send
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

# Configure application
load_dotenv()
app = Flask(__name__)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["SECRET_KEY"] = "secret_key"
mail = Mail(app)
socketio = SocketIO(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///proyecto.db")

# Configurar el serializer
serializer = URLSafeTimedSerializer("180803C")


# Generate a random room code
def generate_room_code():
    """Generates a unique room code."""
    while True:
        room_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        existing_room = db.execute("SELECT id FROM rooms WHERE code = ?", room_code)
        if not existing_room:
            return room_code


# Index
@app.route("/", methods=["GET"])
def index():
    # user_id = session["user_id"]
    # rooms = db.execute(
    #     "SELECT rooms.code, rooms.name FROM rooms JOIN user_rooms ON rooms.id = user_rooms.room_id WHERE user_rooms.user_id = ?",
    #     user_id,
    # )
    # print("ye")
    # return render_template("index.html", rooms=rooms)
    return render_template("index.html")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("correo")
        password = request.form.get("password")
        cpassword = request.form.get("confirmation")

        if not username or not email or not password or not cpassword:
            flash("Asegúrate de rellenar todas las entradas", "error")
            return render_template("register.html")

        if password != cpassword:
            flash("Las contraseñas no coinciden", "error")
            return render_template("register.html")

        existing_user = db.execute(
            "SELECT * FROM usuarios WHERE username = ?", username
        )
        if len(existing_user) != 0:
            flash("El nombre de usuario ya existe", "error")
            return render_template("register.html")

        existing_email = db.execute("SELECT * FROM usuarios WHERE email = ?", email)
        if len(existing_email) != 0:
            user = existing_email[0]
            if not user["confirmed"]:
                # Si el correo ya está registrado pero no confirmado, permitir reenviar el correo de confirmación
                flash(
                    "Email registrado pero no confirmado.",
                    "error",
                )
                return render_template("register.html", resend_confirmation=True)
            else:
                flash("Email ya registrado", "error")
                return render_template("register.html")
        hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO usuarios (username, email, hash, confirmed) VALUES(?, ?, ?, ?)",
            username,
            email,
            hash,
            False,
        )

        token = serializer.dumps(email, salt="email-confirm")
        mensaje = Message(
            "Confirm Email", sender="syntaxterror9@gmail.com", recipients=[email]
        )
        link = url_for("confirm_email", token=token, email=email, _external=True)
        mensaje.body = "Por favor confirme en el siguiente enlace: " + link

        try:
            mail.send(mensaje)
        except Exception as e:
            flash(f"Error enviando el email: {str(e)}", "error")
            return redirect(url_for("login"))

        flash("Un email de confirmación ha sido enviado a tu dirección!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# Ruta para reenviar el correo de confirmación
@app.route("/resend_confirmation_email", methods=["POST"])
def resend_confirmation_email():
    if request.method == "POST":
        email = request.form.get("email")  # Obtener el email del formulario
        print(email)
        # Verificar si el email está registrado en la base de datos
        user = db.execute("SELECT * FROM usuarios WHERE email = ?", email)
        print(user)
        if not user:
            flash("Email no encontrado. Por favor, registrarse", "error")
            return redirect(url_for("register"))

        # Generar un nuevo token
        token = serializer.dumps(email, salt="email-confirm")

        # Construir el mensaje de correo
        mensaje = Message(
            "Confirm Email",
            sender="syntaxterror9@gmail.com",
            recipients=[email],
        )
        link = url_for("confirm_email", token=token, email=email, _external=True)
        mensaje.body = "Por favor confirme en el siguiente enlace: " + link

        try:
            mail.send(mensaje)
        except Exception as e:
            print(e)
            flash(f"Error en enviar el email: {str(e)}", "error")
            return redirect(url_for("login"))

        flash("Un nuevo email de confirmación ha sido enviado a tu correo!", "success")
        return render_template("login.html")

    # Manejar otros métodos HTTP si es necesario
    return redirect(url_for("index"))


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        print("rooms")
        if not request.form.get("email"):
            flash("Debe proveerse el correo", "error")
            return render_template("login.html")

        if not request.form.get("password"):
            flash("Debe proveerse la contraseña", "error")
            return render_template("login.html")

        rows = db.execute(
            "SELECT * FROM usuarios WHERE email = ?", request.form.get("email")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Correo o contraseña inválido", "error")
            return render_template("login.html")

        if not rows[0]["confirmed"]:
            flash("Cuenta no confirmada. Por favor revisar su email", "error")
            return render_template("login.html")

        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        flash("Usuario logueado correctamente! ", "success")
        return redirect(url_for("inicio"))
    # print("e")
    return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Confirm email
# Confirm email
@app.route("/<email>/confirm_email/<token>")
def confirm_email(token, email):
    try:
        mail = serializer.loads(token, salt="email-confirm", max_age=120)
    except SignatureExpired:
        # Token ha caducado, mostrar mensaje y botón para reenviar correo
        flash("Link de confirmación expirado. Click abajo para reenviar:")
        return render_template("login.html", resend_confirmation=True, email=email)

    # Resto del código para la confirmación exitosa
    rows = db.execute("SELECT * FROM usuarios WHERE email = ?", mail)
    if len(rows) != 1:
        flash("Petición de confirmación inválida", "error")
        return render_template("register.html")

    user = rows[0]
    if user["confirmed"]:
        flash("Cuenta ya confirmada. Por favor, inicie sesión", "success")
    else:
        db.execute("UPDATE usuarios SET confirmed = ? WHERE email = ?", True, mail)
        flash("Tu cuenta ha sido confirmada!", "success")

    return render_template("login.html")


# Create room
@app.route("/create_room", methods=["POST"])
@login_required
def create_room():
    room_code = generate_room_code()
    room_name = request.form.get("room_name")
    if not room_name:
        flash("Se requiere de un nombre de sala", "error")
        return render_template("index.html")
    db.execute("INSERT INTO rooms (code, name) VALUES(?, ?)", room_code, room_name)
    room_id = db.execute("SELECT id FROM rooms WHERE code = ?", room_code)[0]["id"]
    db.execute(
        "INSERT INTO user_rooms (user_id, room_id) VALUES(?, ?)",
        session["user_id"],
        room_id,
    )
    session["room_code"] = room_code
    return redirect(url_for("chat", room_code=room_code))


# Join room
@app.route("/join_room", methods=["POST"])
@login_required
def room_join():
    room_code = request.form.get("room_code")
    room = db.execute("SELECT id FROM rooms WHERE code = ?", room_code)
    if len(room) == 0:
        flash("Sala no encontrada", "error")
        return redirect(url_for("index"))

    room_id = room[0]["id"]
    try:
        db.execute(
            "INSERT INTO user_rooms (user_id, room_id) VALUES(?, ?)",
            session["user_id"],
            room_id,
        )
    except ValueError:
        return redirect("/chat")
    session["room_code"] = room_code
    return redirect(url_for("chat", room_code=room_code))


# Chat
@app.route("/chat/<room_code>")
@login_required
def chat(room_code):
    user_id = session.get("user_id")
    username = session.get("username")
    session["room_code"] = room_code
    if not room_code:
        flash("Por favor únase a una sala primero", "error")
        return redirect(url_for("index"))

    # Obtener el nombre de la sala
    room = db.execute("SELECT name FROM rooms WHERE code = ?", room_code)
    if not room:
        flash("Sala no encontrada", "error")
        return redirect(url_for("index"))
    room_name = room[0]["name"]

    messages = db.execute(
        "SELECT username, message, timestamp FROM messages WHERE room_code = ? ORDER BY timestamp",
        room_code,
    )

    # Obtener todas las salas a las que el usuario está unido
    rooms = db.execute(
        """
        SELECT rooms.code, rooms.name, rooms.gimg
        FROM rooms
        JOIN user_rooms ON rooms.id = user_rooms.room_id
        WHERE user_rooms.user_id = ?
        """,
        user_id,
    )

    # Obtener la pfp del usuario
    pfp_query = db.execute("SELECT pfp FROM usuarios WHERE id = ?", user_id)
    pfp = pfp_query[0]["pfp"]
    if pfp is None:
        pfp = "../static/images/Default.png"
    print(pfp)
    return render_template(
        "chat.html",
        username=username,
        room_code=room_code,
        room_name=room_name,
        messages=messages,
        rooms=rooms,
        pfp=pfp,
    )


@socketio.on("join")
def handle_join(data):
    room = data["room"]
    join_room(room)
    send({"msg": f"{data['username']} se ha unido a la sala."}, to=data["room"])


@socketio.on("message")
def handle_message(data):
    db.execute(
        "INSERT INTO messages (room_code, username, message) VALUES(?, ?, ?)",
        data["room"],
        data["username"],
        data["message"],
    )

    send(
        {"msg": f"{data}"},
        to=data["room"],
        include_self=False,
    )


@socketio.on("leave")
def handle_leave(data):
    room = data["room"]
    leave_room(room)


@app.route("/chat")
@login_required
def inicio():
    # Si el método es post... (subir imagen)
    user_id = session.get("user_id")
    username = session.get("username")

    # Obtener todas las salas a las que el usuario está unido
    rooms = db.execute(
        """
        SELECT rooms.code, rooms.name, rooms.gimg
        FROM rooms
        JOIN user_rooms ON rooms.id = user_rooms.room_id
        WHERE user_rooms.user_id = ?
        """,
        user_id,
    )
    # Obtener la pfp del usuario
    pfp_query = db.execute("SELECT pfp FROM usuarios WHERE id = ?", user_id)
    pfp = pfp_query[0]["pfp"]
    if pfp is None:
        pfp = "../static/images/Default.png"
    print(pfp)
    return render_template("inicio.html", username=username, rooms=rooms, pfp=pfp)


if __name__ == "__main__":
    socketio.run(app, debug=True)
