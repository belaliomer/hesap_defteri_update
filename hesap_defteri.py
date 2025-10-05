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
                code_resp = requests.get(GITHUB_CODE_URL)
                code_resp.raise_for_status()
                with open(sys.argv[0], "w", encoding="utf-8") as f:
                    f.write(code_resp.text)
                messagebox.showinfo("Güncelleme Tamam", "Program güncellendi, yeniden başlatılıyor...")
                os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        print("Update check failed:", e)

# ---------- scipy optional for triangle wave ----------
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

def make_canvas(master, figsize=(8,4.5)):
    fig = plt.Figure(figsize=figsize, dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=master)
    canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True)
    return fig, canvas

def add_entry(parent, label, default):
    tk.Label(parent, text=label, font=LABEL_FONT).pack(anchor="w")
    e = tk.Entry(parent, font=LABEL_FONT)
    e.insert(0, str(default))
    e.pack(anchor="w", pady=(0,6))
    return e

# ---------- BOOST SEKME ----------
frame_boost = ttk.Frame(notebook)
notebook.add(frame_boost, text="Boost")
left_b = tk.Frame(frame_boost); left_b.pack(side="left", fill="y", padx=10, pady=8)
right_b = tk.Frame(frame_boost); right_b.pack(side="right", fill="y", padx=10, pady=8)
fig_frame_b = tk.Frame(frame_boost); fig_frame_b.pack(side="bottom", fill="both", expand=True, padx=10, pady=6)

tk.Label(left_b, text="Boost - Giriş Parametreleri", font=TITLE_FONT).pack(anchor="w", pady=(0,6))
entry_b_vin = add_entry(left_b, "Vin (V):", 28)
entry_b_vout = add_entry(left_b, "Vout (V):", 82)
entry_b_f = add_entry(left_b, "Frekans (kHz):", 8)
entry_b_L = add_entry(left_b, "L (µH):", 33)
entry_b_C = add_entry(left_b, "Cout (µF):", 470)
entry_b_ripI = add_entry(left_b, "Tolerans ΔI (%):", 20)
entry_b_ripV = add_entry(left_b, "Tolerans ΔV (%):", 1)

tk.Label(left_b, text="Yük Akımı (A):", font=LABEL_FONT).pack(anchor="w")
slider_b_Iout = tk.Scale(left_b, from_=0.1, to=20.0, resolution=0.1, orient="horizontal", length=260, font=LABEL_FONT)
slider_b_Iout.set(10.0)
slider_b_Iout.pack(anchor="w", pady=(0,8))

tk.Label(left_b, text="Timer Ayarları (PSC/ARR)", font=TITLE_FONT).pack(anchor="w", pady=(6,6))
entry_b_fclk = add_entry(left_b, "f_clk (Hz):", 72000000)
var_b_PSC_fix = tk.BooleanVar()
tk.Checkbutton(left_b, text="PSC Sabit Tut", variable=var_b_PSC_fix, font=LABEL_FONT).pack(anchor="w")
entry_b_PSC = tk.Entry(left_b, font=LABEL_FONT); entry_b_PSC.pack(anchor="w", pady=(0,6))
var_b_ARR_fix = tk.BooleanVar()
tk.Checkbutton(left_b, text="ARR Sabit Tut", variable=var_b_ARR_fix, font=LABEL_FONT).pack(anchor="w")
entry_b_ARR = tk.Entry(left_b, font=LABEL_FONT); entry_b_ARR.pack(anchor="w", pady=(0,10))

btn_b_calc = tk.Button(left_b, text="Hesapla (Boost)", font=LABEL_FONT)
btn_b_calc.pack(pady=(6,12))
tk.Label(right_b, text="Boost - Sonuçlar", font=TITLE_FONT).pack(anchor="w")
out_b_text = tk.Text(right_b, width=50, height=28, font=MONO_FONT)
out_b_text.pack()
fig_b, canvas_b = make_canvas(fig_frame_b)

# ---------- BUCK SEKME ----------
frame_buck = ttk.Frame(notebook)
notebook.add(frame_buck, text="Buck")
left_k = tk.Frame(frame_buck); left_k.pack(side="left", fill="y", padx=10, pady=8)
right_k = tk.Frame(frame_buck); right_k.pack(side="right", fill="y", padx=10, pady=8)
fig_frame_k = tk.Frame(frame_buck); fig_frame_k.pack(side="bottom", fill="both", expand=True, padx=10, pady=6)

tk.Label(left_k, text="Buck - Giriş Parametreleri", font=TITLE_FONT).pack(anchor="w", pady=(0,6))
entry_k_vin = add_entry(left_k, "Vin (V):", 12)
entry_k_vout = add_entry(left_k, "Vout (V):", 5)
entry_k_f = add_entry(left_k, "Frekans (kHz):", 50)
entry_k_L = add_entry(left_k, "L (µH):", 100)
entry_k_C = add_entry(left_k, "Cout (µF):", 100)
entry_k_ripI = add_entry(left_k, "Tolerans ΔI (A):", 0.1)
entry_k_ripV = add_entry(left_k, "Tolerans ΔV (V):", 0.1)

tk.Label(left_k, text="Yük Akımı (A):", font=LABEL_FONT).pack(anchor="w")
slider_k_Iout = tk.Scale(left_k, from_=0.01, to=1.0, resolution=0.01, orient="horizontal", length=260, font=LABEL_FONT)
slider_k_Iout.set(0.5)
slider_k_Iout.pack(anchor="w", pady=(0
