import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import requests
import os
import sys

# ---------- Sürüm kontrol ----------
VERSION = "1.0.0"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/belaliomer/hesap_defteri_update/main/version.txt"
GITHUB_CODE_URL = "https://raw.githubusercontent.com/belaliomer/hesap_defteri_update/main/hesap_defteri.py"

def check_update():
    try:
        resp = requests.get(GITHUB_VERSION_URL, timeout=5)
        resp.raise_for_status()
        latest_version = resp.text.strip()
        if latest_version > VERSION:
            if messagebox.askyesno("Güncelleme Var", f"Yeni sürüm mevcut: {latest_version}\nŞu anki sürüm: {VERSION}\nGüncellemek ister misiniz?"):
                # GitHub'dan yeni kodu indir
                code_resp = requests.get(GITHUB_CODE_URL)
                code_resp.raise_for_status()
                with open(sys.argv[0], "w", encoding="utf-8") as f:
                    f.write(code_resp.text)
                messagebox.showinfo("Güncelleme Tamam", "Program güncellendi, yeniden başlatılıyor...")
                os.execl(sys.executable, sys.executable, *sys.argv)  # kendini yeniden başlat
    except Exception as e:
        print("Update check failed:", e)

# ---------- GUI ve hesap kodu burada başlıyor ----------

# scipy optional for triangle wave; fallback if not available
try:
    from scipy import signal
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False

def triangle_wave(freq, t):
    if _HAS_SCIPY:
        return signal.sawtooth(2 * np.pi * freq * t, 0.5)
    period = 1.0 / freq
    phase = (t % period) / period
    tri = np.where(phase < 0.5, 4 * phase - 1, 3 - 4 * phase)
    return tri

def calc_timer_from_inputs(f_clk, f_pwm, psc_fix, arr_fix, psc_val_str, arr_val_str):
    try:
        f_clk = float(f_clk)
        f_pwm = float(f_pwm)
    except:
        raise ValueError("f_clk veya f_pwm sayısal değil")
    if f_pwm <= 0:
        raise ValueError("PWM frekansı pozitif olmalı")
    if psc_fix and not arr_fix:
        PSC_calc = int(float(psc_val_str))
        ARR_calc = int(max(0, round(f_clk / ((PSC_calc + 1) * f_pwm) - 1)))
    elif arr_fix and not psc_fix:
        ARR_calc = int(float(arr_val_str))
        PSC_calc = int(max(0, round(f_clk / ((ARR_calc + 1) * f_pwm) - 1)))
    else:
        PSC_calc = 0
        ARR_calc = int(max(0, round(f_clk / ((PSC_calc + 1) * f_pwm) - 1)))
    return PSC_calc, ARR_calc

# ---------- Pencere ve stil ----------
root = tk.Tk()
root.title("Elektronik Hesap Makinesi - Boost/Buck/Flyback")
root.geometry("1250x820")

FONT_BASE = 13
LABEL_FONT = ("Segoe UI", FONT_BASE)
TITLE_FONT = ("Segoe UI", FONT_BASE+1, "bold")
MONO_FONT = ("Consolas", FONT_BASE)

style = ttk.Style()
style.configure("TNotebook.Tab", font=("Segoe UI", FONT_BASE+1))

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=8, pady=6)

# helper to create matplotlib canvas
def make_canvas(master, figsize=(8,4.5)):
    fig = plt.Figure(figsize=figsize, dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=master)
    canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True)
    return fig, canvas

# ---------- BOOST SEKME ----------
# (Boost, Buck, Flyback GUI ve hesap fonksiyonları buraya aynen geçecek)
# ... [Burada önceki boost/buck/flyback GUI ve hesap kodunuz olacak]

# ---------- Başta güncelleme kontrol ----------
root.after(100, check_update)  # GUI başladıktan kısa süre sonra kontrol et

root.mainloop()
