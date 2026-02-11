📸 Enrichisseur de Photos & Vidéos (ExifTool GUI)

Cette application permet de gérer les métadonnées (Dates, GPS) et de renommer massivement des photos et vidéos (JPG, PNG, HEIC, MOV, MP4) en utilisant la puissance d'ExifTool via une interface graphique simple.
🛠️ Prérequis

Avant de lancer l'application, assurez-vous d'avoir les éléments suivants dans le dossier du projet :

    Python installé sur votre machine.

    ExifTool : Le fichier exiftool.exe doit être présent dans le même dossier que les scripts Python.

    Les scripts :

        main.py (L'interface graphique)

        backend.py (La logique technique)

⚙️ Installation

Si vous réutilisez ce projet sur un nouveau PC, vous devez installer la bibliothèque de géolocalisation :

    Ouvrez un terminal (PowerShell ou Cmd) dans le dossier.

    Lancez la commande :
    Bash

    pip install geopy

    (Note : tkinter est inclus par défaut avec Python, pas besoin de l'installer)

🚀 Lancement

    Ouvrez le dossier contenant les fichiers.

    Clic droit dans le vide > "Ouvrir dans le Terminal".

    Tapez :
    Bash

    python main.py

📖 Guide d'utilisation
1. Chargement

    Cliquez sur "📂 Dossier" pour sélectionner le dossier contenant vos images/vidéos.

    Couleurs :

        🔴 Rouge : Date EXIF manquante.

        🔵 Bleu : Modification de date en attente.

        🟣 Violet : Modification GPS en attente.

        🟠 Orange : Renommage en attente.

2. Gestion des Dates

    Automatique : Sélectionnez des lignes, puis cliquez sur :

        📅 Date (Nom) : Si le fichier s'appelle "IMG_20230101.jpg".

    Manuel : Double-cliquez sur une ligne pour entrer une date à la main (AAAA:MM:JJ HH:MM:SS).

    Validation : Cliquez sur le bouton vert "💾 Sauver Dates" pour appliquer les changements aux fichiers.

3. Géolocalisation (GPS)

    Sélectionnez les photos d'un même lieu.

    Cliquez sur "🌍 Chercher un Lieu".

    Tapez une ville (ex: "Lyon") ou une adresse précise.

    Validez, puis cliquez sur le bouton vert "💾 Sauver GPS".

4. Renommage des fichiers

    Une fois que vos dates sont correctes, cliquez sur "ABC Simuler Noms".

    L'application va prévisualiser les nouveaux noms (Format : AAAA-MM-JJ_HHMMSS.ext).

    Vérifiez la colonne "Renommage".

    Cliquez sur le bouton orange "✏️ RENOMMER" pour appliquer.

📦 Créer un Exécutable (.exe)

Pour ne plus avoir besoin de Python ou du terminal, vous pouvez créer une application autonome :

    Installez PyInstaller : pip install pyinstaller

    Générez l'EXE :
    Bash

    pyinstaller --noconsole --onefile --name "MonOutilPhoto" main.py

    Allez dans le dossier dist/.

    Important : Copiez exiftool.exe et collez-le à côté de MonOutilPhoto.exe.

    Vous pouvez maintenant lancer l'application directement !

⚠️ Notes importantes

    Sauvegarde : L'application modifie directement les fichiers (mode -overwrite_original). Faites toujours une sauvegarde de vos photos avant de traiter un gros dossier.

    Formats supportés : JPG, JPEG, PNG, HEIC, MOV, MP4.