APPLICATION DECC/VAE — GESTION DES RÉUNIONS
===========================================

Application portable (clé USB) pour la Direction DECC/VAE,
Ministère de l'Éducation Nationale (Niger).

Python embarqué : dossier python\ (Standalone Build 3.11)
Base par défaut : SQLite (decc_vae\data\db.sqlite3)
PostgreSQL : DATABASE_ENGINE=postgresql dans .env

PREMIÈRE UTILISATION (Windows 64 bits)
--------------------------------------
1. Copiez tout le dossier sur la clé USB.
2. Placez vc_redist.x64.exe dans redist\ (recommandé hors ligne).
3. Double-cliquez sur install.bat (une fois).
4. Lancement sans fenêtre : double-cliquez sur launch.vbs
   Lancement avec fenêtre : start.bat ou run.bat
5. Navigateur : http://127.0.0.1:8000
6. Compte : admin / admin123  (à changer via /admin/)

SCRIPTS
-------
install.bat       Installation (VC++, pip, migrations, admin)
start.bat         Serveur + navigateur (fenêtre visible)
run.bat           Alias de start.bat
launch.vbs        Serveur masqué (pas de fenêtre terminal)
stop.bat          Arrêt du processus sur le port 8000
check_install.bat Vérification Python / Django / VC++ / base
update.bat        Mise à jour des paquets et migrations (sans écraser la base)

FONCTIONS
---------
- Réunions et points (CRUD)
- Volets : Examens, Concours, Certifications, VAE, Gestion des Données, Autre
- Types : Ordinaire, Extraordinaire, Direction/Général, Suivi, Préparation, Post-examens, Autre
- Champs « Autre à préciser » (type, lieu, volet)
- Filtres période / type / volet / urgence / statut + recherche
- Exports PDF, Word, Excel (une réunion ou toutes)
- Import Excel des points + modèle
- Rapport de période (PDF ou Word)
- Fusion de bases SQLite (menu Fusion SQLite)

ARRÊT
-----
stop.bat, ou fermez le processus python de runserver.
