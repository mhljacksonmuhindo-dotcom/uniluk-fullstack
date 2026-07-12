import os
import re
import sqlite3

from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for

# Chargement optionnel des variables via python-dotenv 
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["DATABASE"] = DATABASE_PATH
app.config["ADMIN_USER"] = os.getenv("ADMIN_USER")
app.config["ADMIN_PASS"] = os.getenv("ADMIN_PASS")
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
app.config["MAX_ZIP_BYTES"] = 20 * 1024 * 1024  # 20 Mo

def connexion():

    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = connexion()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS inscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            postnom TEXT NOT NULL,
            sexe TEXT NOT NULL,
            telephone TEXT NOT NULL,
            email TEXT NOT NULL,
            date_naissance TEXT NOT NULL,
            lieu_naissance TEXT NOT NULL,
            nationalite TEXT NOT NULL,
            etat_civil TEXT NOT NULL,
            religion TEXT NOT NULL,
            groupe_sanguin TEXT NOT NULL,
            province TEXT,
            ville TEXT,
            adresse TEXT NOT NULL,
            nom_pere TEXT NOT NULL,
            nom_mere TEXT NOT NULL,
            nom_responsable_financier TEXT NOT NULL,
            telephone_responsable_financier TEXT NOT NULL,
            profession_anterieure TEXT NOT NULL,
            residence TEXT NOT NULL,
            nom_dortoir TEXT,
            nom_quartier TEXT,
            annee_scolaire TEXT NOT NULL,
            etablissement_frequente TEXT NOT NULL,
            diplome_obtenu TEXT NOT NULL,
            domaine TEXT NOT NULL,
            faculte TEXT NOT NULL,
            filiere TEXT NOT NULL,
            mention TEXT NOT NULL,
            promotion TEXT NOT NULL,
            etablissement TEXT NOT NULL,
            message TEXT,
            dossier_zip_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
     """
    )
    db.execute(
    """
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        email TEXT NOT NULL,
        telephone TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """
)
    db.commit()
    db.close()

def allowed_zip(filename):
    return (filename or "").lower().endswith(".zip")

def secure_basename(name: str, max_len: int = 60) -> str:
    base = os.path.splitext(name or "")[0] or "dossier"
    base = re.sub(r"[^A-Za-z0-9_-]+", "_", base)
    return base[:max_len]

def admin_connecte():
    return bool(session.get("admin_logged_in"))

def static_page(template_name: str):
    return render_template(template_name)

STATIC_PAGES = [
    ("/universite", "universite.html", "universite"),
    ("/uniluk", "uniluk.html", "uniluk"),
    ("/istm", "istm.html", "istm"),
    ("/ista", "ista.html", "ista"),
    ("/campus", "campus.html", "campus"),
    ("/actualites", "actualites.html", "actualites"),
    ("/admission", "admission.html", "admission"),
]

for rule, template_name, endpoint_name in STATIC_PAGES:
    app.add_url_rule(
        rule,
        endpoint=endpoint_name,
        view_func=lambda t=template_name: static_page(t),
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        telephone = request.form.get("telephone")
        message = request.form.get("message")
        db = connexion()
        db.execute(
            """
            INSERT INTO contacts
            (nom, prenom, email, telephone, message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                nom,
                prenom,
                email,
                telephone,
                message
            )
        )
        db.commit()
        db.close()
        flash("Votre message a été envoyé avec succès.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "GET":
        return render_template("inscription.html")

    form = request.form

    required_fields = [
        "nom",
        "postnom",
        "prenom",
        "sexe",
        "lieu_naissance",
        "date_naissance",
        "nationalite",
        "etat_civil",
        "religion",
        "groupe_sanguin",
        "adresse",
        "telephone",
        "email",
        "nom_pere",
        "nom_mere",
        "nom_responsable_financier",
        "telephone_responsable_financier",
        "profession_anterieure",
        "residence",
        "annee_scolaire",
        "diplome_obtenu",

        "domaine",
        "faculte",
        "filiere",
        "mention",
        "promotion",
    ]

    dossier_zip = request.files.get("dossier_zip")
    if not dossier_zip or dossier_zip.filename is None:
        flash("Veuillez téléverser le dossier ZIP.", "danger")
        return redirect(url_for("inscription"))

    if not allowed_zip(dossier_zip.filename):
        flash("Le dossier ZIP doit avoir une extension .zip.", "danger")
        return redirect(url_for("inscription"))

    # taille ZIP
    dossier_zip.stream.seek(0, os.SEEK_END)
    file_size = dossier_zip.stream.tell()
    dossier_zip.stream.seek(0)

    if file_size > app.config["MAX_ZIP_BYTES"]:
        flash("Le ZIP dépasse 20Mo maximum.", "danger")
        return redirect(url_for("inscription"))

    missing = [field for field in required_fields if not form.get(field)]

    if missing:
        flash("Veuillez remplir tous les champs obligatoires.", "danger")
        return redirect(url_for("inscription"))

    columns = [
        "nom",
        "prenom",
        "postnom",
        "sexe",
        "date_naissance",
        "lieu_naissance",
        "nationalite",
        "etat_civil",
        "religion",
        "groupe_sanguin",
        "telephone",
        "email",
        "province",
        "ville",
        "adresse",
        "etablissement",
        "filiere",
        "message",
        "nom_pere",
        "nom_mere",
        "nom_responsable_financier",
        "telephone_responsable_financier",
        "profession_anterieure",
        "residence",
        "nom_dortoir",
        "nom_quartier",
        "annee_scolaire",
        "etablissement_frequente",
        "diplome_obtenu",
        "domaine",
        "faculte",
        "mention",
        "promotion",
        "dossier_zip_path",
    ]

    values = [
        form.get("nom"),
        form.get("prenom"),
        form.get("postnom"),
        form.get("sexe"),
        form.get("date_naissance"),
        form.get("lieu_naissance"),
        form.get("nationalite"),
        form.get("etat_civil"),
        form.get("religion"),
        form.get("groupe_sanguin"),
        form.get("telephone"),
        form.get("email"),
        form.get("province", ""),
        form.get("ville", ""),
        form.get("adresse"),
        form.get("etablissement", ""),
        form.get("filiere"),
        form.get("message", ""),
        form.get("nom_pere"),
        form.get("nom_mere"),
        form.get("nom_responsable_financier"),
        form.get("telephone_responsable_financier"),
        form.get("profession_anterieure"),
        form.get("residence"),
        form.get("nom_dortoir", ""),
        form.get("nom_quartier", ""),
        form.get("annee_scolaire"),
        form.get("etablissement_frequente", ""),
        form.get("diplome_obtenu"),
        form.get("domaine"),
        form.get("faculte"),
        form.get("mention"),
        form.get("promotion"),
        None,  
    ]


    placeholders = ", ".join(["?"] * len(columns))
    column_list = ", ".join(columns)

    db = connexion()
    try:
        db.execute(
            f"""
            INSERT INTO inscriptions ({column_list})
            VALUES ({placeholders})
            """,
            values,
        )
        inscription_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        safe_name = secure_basename(dossier_zip.filename)
        saved_name = f"dossier_{inscription_id}_{safe_name}.zip"
        saved_path = os.path.join(app.config["UPLOAD_FOLDER"], saved_name)
        dossier_zip.save(saved_path)

        db.execute(
            "UPDATE inscriptions SET dossier_zip_path = ? WHERE id = ?",
            (saved_name, inscription_id),
        )
        db.commit()
    finally:
        db.close()

    flash("Votre inscription a bien été enregistrée.", "success")
    return redirect(url_for("inscription"))

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if admin_connecte():
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == app.config["ADMIN_USER"] and password == app.config["ADMIN_PASS"]:
            session["admin_logged_in"] = True
            flash("Connexion réussie.", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Identifiants incorrects.", "danger")
    return render_template("admin/login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("admin_login"))

@app.route("/admin/dashboard")
def admin_dashboard():
    if not admin_connecte():
        return redirect(url_for("admin_login"))

    db = connexion()
    try:
        total = db.execute("SELECT COUNT(*) AS count FROM inscriptions").fetchone()["count"]
        recent = db.execute("SELECT * FROM inscriptions ORDER BY id DESC LIMIT 5").fetchall()
    finally:
        db.close()

    return render_template("admin/dashboard.html", total=total, recent=recent)

@app.route("/admin/inscriptions")
def admin_inscriptions():
    if not admin_connecte():
        return redirect(url_for("admin_login"))

    search = request.args.get("search", "").strip()
    db = connexion()
    try:
        if search:
            term = f"%{search}%"
            inscriptions = db.execute(
                """
                SELECT * FROM inscriptions
                WHERE nom LIKE ? OR prenom LIKE ? OR email LIKE ? OR filiere LIKE ?
                ORDER BY id DESC
                """,
                (term, term, term, term),
            ).fetchall()
        else:
            inscriptions = db.execute("SELECT * FROM inscriptions ORDER BY id DESC").fetchall()
    finally:
        db.close()

    return render_template(
        "admin/inscriptions.html",
        inscriptions=inscriptions,
        search=search,
    )

@app.route("/admin/inscriptions/edit/<int:inscription_id>", methods=["GET", "POST"])
def admin_edit_inscription(inscription_id):
    if not admin_connecte():
        return redirect(url_for("admin_login"))

    db = connexion()
    try:
        inscription_row = db.execute(
            "SELECT * FROM inscriptions WHERE id = ?",
            (inscription_id,),
        ).fetchone()

        if inscription_row is None:
            flash("Inscription introuvable.", "danger")
            return redirect(url_for("admin_inscriptions"))

        if request.method == "POST":
            form = request.form

            db.execute(
                """
                UPDATE inscriptions SET
                    nom = ?, prenom = ?, sexe = ?, date_naissance = ?, telephone = ?,
                    email = ?, province = ?, ville = ?, adresse = ?, etablissement = ?,
                    filiere = ?, message = ?
                WHERE id = ?
                """,
                (
                    form.get("nom", inscription_row["nom"]),
                    form.get("prenom", inscription_row["prenom"]),
                    form.get("sexe", inscription_row["sexe"]),
                    form.get("date_naissance", inscription_row["date_naissance"]),
                    form.get("telephone", inscription_row["telephone"]),
                    form.get("email", inscription_row["email"]),
                    form.get("province", inscription_row["province"]),
                    form.get("ville", inscription_row["ville"]),
                    form.get("adresse", inscription_row["adresse"]),
                    form.get("etablissement", inscription_row["etablissement"]),
                    form.get("filiere", inscription_row["filiere"]),
                    form.get("message", inscription_row["message"]),
                    inscription_id,
                ),
            )
            db.commit()

            flash("Inscription mise à jour.", "success")
            return redirect(url_for("admin_inscriptions"))

        return render_template("admin/edit_inscription.html", inscription=inscription_row)
    finally:
        db.close()

@app.route("/admin/inscriptions/delete/<int:inscription_id>")
def admin_delete_inscription(inscription_id):
    if not admin_connecte():
        return redirect(url_for("admin_login"))

    db = connexion()
    try:
        db.execute("DELETE FROM inscriptions WHERE id = ?", (inscription_id,))
        db.commit()
    finally:
        db.close()

    flash("Inscription supprimée.", "info")
    return redirect(url_for("admin_inscriptions"))
@app.route("/admin/messages")
def admin_messages():

    if not admin_connecte():
        return redirect(url_for("admin_login"))

    db = connexion()

    messages = db.execute(
        """
        SELECT * FROM contacts
        ORDER BY id DESC
        """
    ).fetchall()

    db.close()

    return render_template(
        "admin/messages.html",
        messages=messages
    )

@app.route("/admin/inscriptions/zip/<int:inscription_id>")
def admin_download_zip(inscription_id: int):
    if not admin_connecte():
        return redirect(url_for("admin_login"))

    db = connexion()
    try:
        inscription_row = db.execute(
            "SELECT dossier_zip_path FROM inscriptions WHERE id = ?",
            (inscription_id,),
        ).fetchone()
    finally:
        db.close()

    if inscription_row is None or not inscription_row["dossier_zip_path"]:
        flash("Dossier ZIP introuvable.", "danger")
        return redirect(url_for("admin_inscriptions"))

    filename = inscription_row["dossier_zip_path"]
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(path):
        flash("Le fichier ZIP n'existe plus sur le serveur.", "danger")
        return redirect(url_for("admin_inscriptions"))

    return send_file(
        path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/zip",
    )

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)

