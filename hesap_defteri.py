import requests
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

CURRENT_VERSION = "1.0.0"
VERSION_URL = "https://raw.githubusercontent.com/belaliomer/hesap_defteri_update/main/version.txt"
PY_URL = "https://raw.githubusercontent.com/belaliomer/hesap_defteri_update/main/hesap_defteri.py"

def check_update():
    try:
        r = requests.get(VERSION_URL)
        r.raise_for_status()
        latest_version = r.text.strip()
        if latest_version != CURRENT_VERSION:
            show_update_popup(latest_version)
    except Exception as e:
        print(f"Güncelleme kontrol hatası: {e}")

def show_update_popup(new_version):
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle

    if messagebox.askyesno(
        title="Güncelleme Mevcut",
        message=f"Yeni sürüm mevcut: {new_version}\nGüncellemek ister misiniz?",
        icon="info"
    ):
        download_and_run_py()
    root.destroy()

def download_and_run_py():
    try:
        temp_path = os.path.join(os.getcwd(), "update_hesap_defteri.py")
        with requests.get(PY_URL, stream=True) as r:
            r.raise_for_status()
            with open(temp_path, 'wb') as f:
                f.write(r.content)

        # Yeni .py dosyasını çalıştır
        subprocess.Popen([sys.executable, temp_path])
        sys.exit(0)
    except Exception as e:
        print(f"Güncelleme indirilemedi: {e}")

if __name__ == "__main__":
    check_update()
    # Buraya mevcut programın ana kodunu ekle
