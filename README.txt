APPLICATION DECC/VAE — GESTION DES RÉUNIONS
===========================================

Application portable (clé USB) de suivi des réunions de la Direction
DECC/VAE du Ministère de l'Enseignement et de la Formation Techniques
et Professionnels (Niger).

FONCTIONNEMENT HORS LIGNE
-------------------------
Aucune installation de Python sur le PC n'est nécessaire. L'application
utilise un Python embarqué dans le dossier python\.

PREMIÈRE UTILISATION (Windows 64 bits)
--------------------------------------
1. Copiez tout le dossier sur la clé USB.
2. (Recommandé hors ligne) Placez vc_redist.x64.exe dans vendor\
   (Visual C++ Redistributable 2015-2022 x64).
3. Double-cliquez sur install.bat (une seule fois).
   - Vérifie / installe Microsoft Visual C++ Redistributable
   - Télécharge Python Standalone si absent
   - Installe les dépendances Django
   - Crée la base SQLite et le compte admin
4. Double-cliquez sur start.bat pour lancer le serveur.
5. Le navigateur s'ouvre sur http://127.0.0.1:8000
6. Connexion : admin / admin123
   (changez ce mot de passe dès que possible via /admin/)

ARRÊT
-----
- CTRL+C dans la fenêtre du serveur, ou double-clic sur stop.bat

UTILISATION
-----------
- Tableau de bord : statistiques et points critiques
- Mes réunions : liste, recherche, filtres (dates, type, service, urgence, statut)
- Nouvelle réunion : informations générales + points de l'ordre du jour
- Détail : modification, suppression, exports PDF / Word / Excel
- Export Excel global : bouton sur la liste (respecte les filtres actifs)

COMPTES
-------
Les comptes se gèrent dans l'interface d'administration Django :
  http://127.0.0.1:8000/admin/

DONNÉES
-------
Base SQLite : decc_vae\data\db.sqlite3
Sauvegardez ce fichier pour conserver l'historique.

DÉPENDANCES TECHNIQUES
----------------------
- Windows 10/11 64 bits
- Microsoft Visual C++ Redistributable 2015-2022 (x64)
- Python Standalone 3.11 (dossier python\)

En cas de problème d'import de modules natifs (Pillow, ReportLab),
installez le Redistributable puis relancez install.bat.
