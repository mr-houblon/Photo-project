import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from backend import ExifManager
import threading
import os

class PhotoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enrichisseur Photo - Recherche Lieu Intégrée")
        self.root.geometry("1300x750")
        
        self.manager = ExifManager() 
        self.donnees_fichiers = [] 
        self._setup_ui()

    def _setup_ui(self):
        # --- Haut ---
        frame_top = tk.Frame(self.root, pady=10, padx=10, bg="#f0f0f0")
        frame_top.pack(fill="x")
        btn_style = {"padx": 10, "pady": 5}

        tk.Button(frame_top, text="📂 Dossier", command=self.charger_dossier, bg="#e1f5fe", **btn_style).pack(side="left", padx=5)
        tk.Label(frame_top, text="|", bg="#f0f0f0").pack(side="left", padx=5)

        self.btn_apply_name = tk.Button(frame_top, text="📅 Date (Nom)", state="disabled", command=lambda: self.appliquer_regle("filename"), **btn_style)
        self.btn_apply_name.pack(side="left", padx=2)
        
        self.btn_save_dates = tk.Button(frame_top, text="💾 Sauver Dates", bg="#81c784", fg="black", state="disabled", command=lambda: self.ecran_confirmation("date"), **btn_style)
        self.btn_save_dates.pack(side="left", padx=5)

        tk.Label(frame_top, text="|", bg="#f0f0f0").pack(side="left", padx=5)

        # Bouton GPS amélioré
        self.btn_gps = tk.Button(frame_top, text="🌍 Chercher un Lieu", state="disabled", command=self.definir_gps, **btn_style)
        self.btn_gps.pack(side="left", padx=2)

        self.btn_save_gps = tk.Button(frame_top, text="💾 Sauver GPS", bg="#81c784", fg="black", state="disabled", command=lambda: self.ecran_confirmation("gps"), **btn_style)
        self.btn_save_gps.pack(side="left", padx=5)

        tk.Label(frame_top, text="|", bg="#f0f0f0").pack(side="left", padx=5)

        self.btn_simul_rename = tk.Button(frame_top, text="ABC Simuler Noms", state="disabled", command=self.simuler_renommage, **btn_style)
        self.btn_simul_rename.pack(side="left", padx=2)

        self.btn_apply_rename = tk.Button(frame_top, text="✏️ RENOMMER", bg="#ffb74d", fg="black", state="disabled", command=lambda: self.ecran_confirmation("rename"), **btn_style)
        self.btn_apply_rename.pack(side="left", padx=5)

        # --- Tableau ---
        frame_list = tk.Frame(self.root)
        frame_list.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("Nom", "DateExif", "NouvelleDate", "GPS", "FuturGPS", "FuturNom")
        self.tree = ttk.Treeview(frame_list, columns=cols, show="headings", selectmode="extended")
        
        self.tree.heading("Nom", text="Fichier")
        self.tree.heading("DateExif", text="Date Actuelle")
        self.tree.heading("NouvelleDate", text="Date Projetée")
        self.tree.heading("GPS", text="GPS Actuel")
        self.tree.heading("FuturGPS", text="Nouveau GPS")
        self.tree.heading("FuturNom", text="Renommage")

        self.tree.column("Nom", width=200)
        self.tree.column("DateExif", width=130)
        self.tree.column("NouvelleDate", width=130)
        self.tree.column("GPS", width=70)
        self.tree.column("FuturGPS", width=150)
        self.tree.column("FuturNom", width=200)
        
        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.tag_configure("manquant", foreground="red")
        self.tree.tag_configure("modifie", foreground="blue", font=("Arial", 9, "bold"))
        self.tree.tag_configure("gps_add", foreground="purple", font=("Arial", 9, "bold"))
        self.tree.bind("<Double-1>", self.edition_manuelle)
        
        self.lbl_statut = tk.Label(self.root, text="Prêt", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.lbl_statut.pack(side=tk.BOTTOM, fill=tk.X)

    def charger_dossier(self):
        dossier = filedialog.askdirectory()
        if not dossier: return
        self.lbl_statut.config(text="Scan en cours...")
        self.root.update()
        res = self.manager.scanner_dossier(dossier)
        if isinstance(res, dict) and "erreur" in res:
            messagebox.showerror("Erreur", res["erreur"])
            return
        self.donnees_fichiers = res
        self.rafraichir_liste()
        for btn in [self.btn_apply_name, self.btn_save_dates, self.btn_simul_rename, self.btn_gps]:
            btn.config(state="normal")
        self.lbl_statut.config(text=f"{len(res)} fichiers chargés.")

    def rafraichir_liste(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for f in self.donnees_fichiers:
            tags = []
            if not f["date_exif"]: tags.append("manquant")
            if f["date_proposee"] != f["date_exif"]: tags.append("modifie")
            if f["gps_futur"]: tags.append("gps_add")
            values = (
                f["nom"],
                f["date_exif"] if f["date_exif"] else "MANQUANT",
                f["date_proposee"] if f["date_proposee"] else "-",
                f["gps_actuel"],
                f["gps_futur"],
                f["nouveau_nom"]
            )
            self.tree.insert("", "end", iid=f["chemin"], values=values, tags=tags)

    def appliquer_regle(self, source):
        selected_items = self.tree.selection()
        if not selected_items: return
        for chemin in selected_items:
            f = next((x for x in self.donnees_fichiers if x["chemin"] == chemin), None)
            if f and source == "filename" and f["date_filename"]:
                 f["date_proposee"] = f["date_filename"]
        self.rafraichir_liste()

    def definir_gps(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Sélectionne d'abord les photos concernées.")
            return

        # 1. Demander à l'utilisateur
        entree = simpledialog.askstring("Recherche Lieu", 
                                        "Entre un nom de ville, une adresse ou un lieu touristique :\n(ex: 'Bordeaux', 'Central Park', '10 Rue de la Paix Paris')")
        if not entree: return

        # 2. Vérifier si c'est déjà des coordonnées ou une recherche texte
        coords_finales = None
        
        # Est-ce que ça ressemble à "48.5, 2.3" ?
        if "," in entree and any(c.isdigit() for c in entree):
             coords_finales = entree
        else:
            # C'est du texte -> On lance la recherche
            self.lbl_statut.config(text=f"Recherche de '{entree}' sur internet...")
            self.root.update()
            
            coords_trouvees, erreur = self.manager.trouver_coordonnees(entree)
            
            if erreur:
                messagebox.showerror("Erreur", erreur)
                self.lbl_statut.config(text="Erreur recherche.")
                return
            
            if coords_trouvees:
                coords_finales = coords_trouvees
                messagebox.showinfo("Trouvé !", f"Lieu trouvé : {entree}\nCoordonnées : {coords_finales}")
            else:
                 messagebox.showwarning("Introuvable", "Ce lieu n'a pas été trouvé. Essaie d'être plus précis (Ajoute le pays).")
                 self.lbl_statut.config(text="Lieu introuvable.")
                 return

        # 3. Appliquer
        if coords_finales:
            count = 0
            for chemin in selected_items:
                f = next((x for x in self.donnees_fichiers if x["chemin"] == chemin), None)
                if f:
                    f["gps_futur"] = coords_finales
                    count += 1
            self.rafraichir_liste()
            self.btn_save_gps.config(state="normal")
            self.lbl_statut.config(text=f"GPS appliqué à {count} fichiers (en attente de sauvegarde).")

    def simuler_renommage(self):
        noms_generes = [] 
        count = 0
        for f in self.donnees_fichiers:
            date_ref = f["date_proposee"]
            if date_ref and len(date_ref) == 19:
                date_clean = date_ref.replace(":", "-").replace(" ", "_")
                ext = os.path.splitext(f["nom"])[1]
                base_name = f"{date_clean}"
                nouveau_nom = f"{base_name}{ext}"
                dossier = os.path.dirname(f["chemin"])
                compteur = 1
                while (nouveau_nom in noms_generes) or (os.path.exists(os.path.join(dossier, nouveau_nom)) and nouveau_nom != f["nom"]):
                    nouveau_nom = f"{base_name}_{compteur}{ext}"
                    compteur += 1
                if nouveau_nom != f["nom"]:
                    f["nouveau_nom"] = nouveau_nom
                    noms_generes.append(nouveau_nom)
                    count += 1
                else: f["nouveau_nom"] = ""
            else: f["nouveau_nom"] = ""
        self.rafraichir_liste()
        self.btn_apply_rename.config(state="normal")
        messagebox.showinfo("Simulation", f"{count} fichiers seront renommés.")

    def edition_manuelle(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        f = next((x for x in self.donnees_fichiers if x["chemin"] == item_id), None)
        val = f["date_proposee"] if f["date_proposee"] else "2023:01:01 12:00:00"
        nouvelle = simpledialog.askstring("Date", f"Modifier : {f['nom']}", initialvalue=val)
        if nouvelle and len(nouvelle) == 19:
            f["date_proposee"] = nouvelle
            self.rafraichir_liste()

    def ecran_confirmation(self, action_type):
        mods = []
        msg_titre = ""
        if action_type == "date":
            mods = [f for f in self.donnees_fichiers if f["date_proposee"] != f["date_exif"]]
            msg_titre = "Sauvegarder Dates"
        elif action_type == "gps":
            mods = [f for f in self.donnees_fichiers if f["gps_futur"]]
            msg_titre = "Sauvegarder GPS"
        elif action_type == "rename":
            mods = [f for f in self.donnees_fichiers if f["nouveau_nom"]]
            msg_titre = "Renommer Fichiers"
        if not mods: return messagebox.showinfo("Info", "Rien à faire.")
        rep = messagebox.askyesno(msg_titre, f"Tu vas appliquer '{action_type}' sur {len(mods)} fichiers.\nContinuer ?")
        if rep: self.lancer_thread(mods, action_type)

    def lancer_thread(self, items, action_type):
        top = tk.Toplevel(self.root)
        top.title("Traitement...")
        top.geometry("400x150")
        lbl = tk.Label(top, text="Travail en cours...")
        lbl.pack(pady=10)
        progress = ttk.Progressbar(top, length=300, mode="determinate")
        progress.pack(pady=10)
        def update_prog(cur, tot):
            self.root.after(0, lambda: progress.configure(value=(cur/tot)*100))
        def thread_target():
            if action_type == "date":
                data = [(x["chemin"], x["date_proposee"]) for x in items]
                s, e = self.manager.sauvegarder_dates(data, update_prog)
                msg = f"Dates mises à jour.\nSuccès: {s}"
            elif action_type == "gps":
                data = [(x["chemin"], x["gps_futur"]) for x in items]
                s, e = self.manager.sauvegarder_gps(data, update_prog)
                msg = f"GPS mis à jour.\nSuccès: {s}"
            elif action_type == "rename":
                data = [(x["chemin"], x["nouveau_nom"]) for x in items]
                s, e = self.manager.renommer_physiquement(data, update_prog)
                msg = f"Fichiers renommés.\nSuccès: {s}"
            self.root.after(0, lambda: self.fin_traitement(top, msg))
        threading.Thread(target=thread_target, daemon=True).start()

    def fin_traitement(self, top, msg):
        top.destroy()
        messagebox.showinfo("Terminé", msg)
        self.donnees_fichiers = [] 
        self.rafraichir_liste()
        self.lbl_statut.config(text="Traitement terminé.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoApp(root)
    root.mainloop()