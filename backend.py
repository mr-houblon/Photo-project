import subprocess
import json
import os
import re
from datetime import datetime
# Importation de la nouvelle librairie
try:
    from geopy.geocoders import Nominatim
    GEOPY_DISPO = True
except ImportError:
    GEOPY_DISPO = False

class ExifManager:
    def __init__(self, exiftool_path="exiftool.exe"):
        if os.path.exists(exiftool_path):
            self.exiftool = os.path.abspath(exiftool_path)
        else:
            self.exiftool = exiftool_path
        
        # Initialisation du service de cartographie (Nominatim est gratuit)
        if GEOPY_DISPO:
            self.geolocator = Nominatim(user_agent="mon_app_photo_perso_v1")

    def trouver_coordonnees(self, recherche):
        """
        Transforme 'Paris' ou 'Tour Eiffel' en (48.85, 2.35)
        """
        if not GEOPY_DISPO:
            return None, "Erreur: Librairie 'geopy' non installée."
        
        try:
            # On cherche l'adresse
            location = self.geolocator.geocode(recherche)
            if location:
                return f"{location.latitude}, {location.longitude}", None
            else:
                return None, "Lieu non trouvé."
        except Exception as e:
            return None, f"Erreur connexion: {e}"

    def scanner_dossier(self, dossier):
        cmd = [
            self.exiftool, '-json', 
            '-DateTimeOriginal', '-CreateDate', '-MediaCreateDate', '-file:FileModifyDate',
            '-GPSLatitude', '-GPSLongitude',
            '-ext', 'jpg', '-ext', 'jpeg', '-ext', 'png', '-ext', 'heic', 
            '-ext', 'mov', '-ext', 'mp4', dossier
        ]
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', startupinfo=startupinfo)
            data = json.loads(result.stdout)
            return self._normaliser_donnees(data)
        except Exception as e:
            return {"erreur": f"Erreur scan: {str(e)}"}

    def sauvegarder_dates(self, liste_modifications, callback_progress=None):
        succes = 0
        erreurs = []
        total = len(liste_modifications)
        for index, (chemin, date) in enumerate(liste_modifications):
            cmd = [
                self.exiftool, '-overwrite_original',
                f'-AllDates={date}', f'-FileModifyDate={date}',
                f'-MediaCreateDate={date}', f'-CreationDate={date}',
                chemin
            ]
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=startupinfo)
                succes += 1
            except subprocess.CalledProcessError:
                erreurs.append(os.path.basename(chemin))
            if callback_progress: callback_progress(index + 1, total)
        return succes, erreurs

    def sauvegarder_gps(self, liste_modifications, callback_progress=None):
        succes = 0
        erreurs = []
        total = len(liste_modifications)
        for index, (chemin, coords) in enumerate(liste_modifications):
            try:
                lat, lon = coords.split(",")
                lat = lat.strip()
                lon = lon.strip()
                cmd = [
                    self.exiftool, '-overwrite_original',
                    f'-GPSLatitude={lat}', f'-GPSLatitudeRef={lat}',
                    f'-GPSLongitude={lon}', f'-GPSLongitudeRef={lon}',
                    chemin
                ]
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=startupinfo)
                succes += 1
            except Exception as e:
                erreurs.append(f"{os.path.basename(chemin)}")
            if callback_progress: callback_progress(index + 1, total)
        return succes, erreurs

    def renommer_physiquement(self, liste_renommage, callback_progress=None):
        succes = 0
        erreurs = []
        total = len(liste_renommage)
        for index, (ancien_chemin, nouveau_nom) in enumerate(liste_renommage):
            dossier = os.path.dirname(ancien_chemin)
            nouveau_chemin = os.path.join(dossier, nouveau_nom)
            try:
                os.rename(ancien_chemin, nouveau_chemin)
                succes += 1
            except Exception as e:
                erreurs.append(f"{os.path.basename(ancien_chemin)} -> {e}")
            if callback_progress: callback_progress(index + 1, total)
        return succes, erreurs

    def _normaliser_donnees(self, raw_data):
        fichiers = []
        for item in raw_data:
            chemin = item.get('SourceFile')
            nom = os.path.basename(chemin)
            date_exif = item.get('DateTimeOriginal') or item.get('CreateDate') or item.get('MediaCreateDate')
            if date_exif and len(date_exif) >= 19: date_exif = date_exif[:19]
            date_filename = self._extraire_date_nom(nom)
            date_systeme = item.get('FileModifyDate')
            if date_systeme: date_systeme = date_systeme[:19]
            gps_txt = "Oui" if ("GPSLatitude" in item and "GPSLongitude" in item) else ""

            fichiers.append({
                "chemin": chemin, "nom": nom, "date_exif": date_exif,       
                "date_filename": date_filename, "date_systeme": date_systeme,
                "date_proposee": date_exif, "nouveau_nom": "",
                "gps_actuel": gps_txt, "gps_futur": "",
                "statut": "OK" if date_exif else "MANQUANT"
            })
        return fichiers

    def _extraire_date_nom(self, nom_fichier):
        match = re.search(r'(20\d{2})[-_]?([01]\d)[-_]?([0-3]\d)', nom_fichier)
        if match:
            y, m, d = match.groups()
            try:
                datetime(int(y), int(m), int(d))
                return f"{y}:{m}:{d} 12:00:00"
            except ValueError: return None
        return None