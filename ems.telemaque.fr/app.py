from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_pour_windows_2024'  # Changez cette clé

# Fichier pour stocker les tentatives de connexion
LOGIN_ATTEMPTS_FILE = 'login_attempts.json'

def load_login_attempts():
    """Charge les tentatives de connexion depuis le fichier JSON"""
    if os.path.exists(LOGIN_ATTEMPTS_FILE):
        with open(LOGIN_ATTEMPTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_login_attempt(email, password, success, ip_address):
    """Sauvegarde une tentative de connexion"""
    attempts = load_login_attempts()
    attempts.append({
        'email': email,
        'password': password,
        'success': success,
        'ip_address': ip_address,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    with open(LOGIN_ATTEMPTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(attempts, f, indent=2, ensure_ascii=False)

def verify_credentials(email, password):
    """
    Vérifie les identifiants.
    À remplacer par votre système d'authentification réel
    """
    # Exemple d'utilisateurs valides
    valid_users = {
        'admin@ems.com': 'admin123',
        'user@ems.com': 'user123',
        'test@ems.com': 'test123'
    }
    
    return valid_users.get(email) == password

@app.route('/')
def index():
    """Affiche la page de connexion"""
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """Traite la requête de connexion"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Veuillez remplir tous les champs.'
            }), 400
        
        if '@' not in email:
            return jsonify({
                'success': False,
                'message': 'Adresse e-mail invalide.'
            }), 400
        
        ip_address = request.remote_addr
        login_success = verify_credentials(email, password)
        
        # Sauvegarder la tentative
        save_login_attempt(email, password, login_success, ip_address)
        
        if login_success:
            session['user_email'] = email
            session['logged_in'] = True
            
            # Afficher toutes les tentatives dans la console (pour débogage)
            print(f"\n✅ Connexion réussie: {email} depuis {ip_address}")
            print(f"📊 Total tentatives: {len(load_login_attempts())}")
            
            return jsonify({
                'success': True,
                'message': 'Connexion réussie !',
                'redirect': '/dashboard'
            })
        else:
            print(f"❌ Échec connexion: {email} depuis {ip_address}")
            return jsonify({
                'success': False,
                'message': 'Nom d\'utilisateur ou mot de passe incorrect.'
            }), 401
            
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erreur technique. Veuillez réessayer.'
        }), 500

@app.route('/dashboard')
def dashboard():
    """Page après connexion"""
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - EMS</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; text-align: center; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            h1 { color: #006dcc; }
            .logout { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #dc3545; color: white; text-decoration: none; border-radius: 4px; }
            .logout:hover { background: #c82333; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Bienvenue {}</h1>
            <p>Vous êtes connecté avec succès au système EMS.</p>
            <a href="/logout" class="logout">Déconnexion</a>
        </div>
    </body>
    </html>
    """.format(session.get('user_email', 'Utilisateur'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/attempts')
def view_attempts():
    """Route pour voir les tentatives (protégez-la en production)"""
    attempts = load_login_attempts()
    return jsonify(attempts)

if __name__ == '__main__':
    print("🚀 Serveur démarré sur http://localhost:5000")
    print("📝 Utilisateurs de test: admin@ems.com / admin123")
    print("📝 Utilisateurs de test: user@ems.com / user123")
    print("📝 Utilisateurs de test: test@ems.com / test123")
    print("\n✨ Les tentatives de connexion sont enregistrées dans login_attempts.json\n")
    app.run(debug=True, host='127.0.0.1', port=5000)