import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sys
import os
import tempfile

# requests only used for update check/download; if not installed, update is skipped
try:
    import requests
    _HAS_REQUESTS = True
except Exception:
    _HAS_REQUESTS = False

# ---------- GÜNCELLEME AYARLARI (burayı kendi raw URL'inle değiştir) ----------
GITHUB_RAW_URL = "https://raw.githubusercontent.com/yourusername/yourrepo/main/browni_kodu.py"
# ---------- GÜNCELLEME FONKSİYONLARI ----------
def _show_update_prompt_and_act(latest_code_text):
    # show prompt using a temporary hidden Tk root (safe even before main GUI)
    tmp = tk.Tk()
    tmp.withdraw()
    try:
        answer = messagebox.askyesno("Güncelleme Var", "Yeni sürüm bulundu. Güncellemek ister misiniz?")
        if answer:
            # write to temporary file and run it
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".py", prefix="browni_update_")
            tmp_file.write(latest_code_text.encode("utf-8"))
            tmp_file.close()
            # try to run the new script and then exit
            try:
                if sys.platform.startswith("win"):
                    os.startfile(tmp_file.name)
                else:
                    # on POSIX, spawn via python
                    os.execv(sys.executable, [sys.executable, tmp_file.name])
            except Exception:
                # fallback: try subprocess
                try:
                    import subprocess
                    subprocess.Popen([sys.executable, tmp_file.name])
                except Exception:
                    pass
            finally:
                tmp.destroy()
                sys.exit(0)
    except Exception:
        tmp.destroy()

def check_and_offer_update():
    if not _HAS_REQUESTS:
        return
    try:
        r = requests.get(GITHUB_RAW_URL, timeout=6)
        if r.status_code == 200:
            latest = r.text
            # simple difference check: if remote differs from local file content, propose update
            try:
                with open(__file__, "r", encoding="utf-8") as f:
                    local = f.read()
                if latest != local:
                    _show_update_prompt_and_act(latest)
            except Exception:
                # if reading __file__ fails, still offer update
                _show_update_prompt_and_act(latest)
    except Exception:
        # network/error -> ignore silently
        return

# Run the update check before starting the main GUI loop (but after imports)
try:
    # call update check once; if no requests or network fails, nothing happens
    if _HAS_REQUESTS:
        # Use a hidden temporary Tk to allow messagebox on platforms where needed
        # Note: if running in contexts without display, this may raise; so wrap
        try:
            check_and_offer_update()
        except Exception:
            pass
except Exception:
    pass

# ---------- burada itibaren "browni kodu" birebir başlıyor ----------
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# scipy optional for triangle wave; fallback if not available
try:
    from scipy import signal
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False

# ---------- yardımcı fonksiyonlar ----------
def triangle_wave(freq, t):
    """Return triangle wave in range [-1,1] for frequency freq (Hz) at times t (seconds).
       Uses scipy.signal.sawtooth if available, otherwise piecewise linear."""
    if _HAS_SCIPY:
        return signal.sawtooth(2 * np.pi * freq * t, 0.5)
    # fallback
    period = 1.0 / freq
    phase = (t % period) / period  # 0..1
    # symmetric triangle -1..1
    tri = np.where(phase < 0.5, 4 * phase - 1, 3 - 4 * phase)
    return tri

def calc_timer_from_inputs(f_clk, f_pwm, psc_fix, arr_fix, psc_val_str, arr_val_str):
    """Return integer PSC_calc, ARR_calc based on choices. PSC minimized (0) if none fixed."""
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
frame_boost = ttk.Frame(notebook)
notebook.add(frame_boost, text="Boost")

left_b = tk.Frame(frame_boost); left_b.pack(side="left", fill="y", padx=10, pady=8)
right_b = tk.Frame(frame_boost); right_b.pack(side="right", fill="y", padx=10, pady=8)
fig_frame_b = tk.Frame(frame_boost); fig_frame_b.pack(side="bottom", fill="both", expand=True, padx=10, pady=6)

tk.Label(left_b, text="Boost - Giriş Parametreleri", font=TITLE_FONT).pack(anchor="w", pady=(0,6))
def add_entry(parent, label, default):
    tk.Label(parent, text=label, font=LABEL_FONT).pack(anchor="w")
    e = tk.Entry(parent, font=LABEL_FONT)
    e.insert(0, str(default))
    e.pack(anchor="w", pady=(0,6))
    return e

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

# timer controls
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

# ---------- BUCK SEKME (DEFAULTLAR GÜNCELLENDİ) ----------
frame_buck = ttk.Frame(notebook)
notebook.add(frame_buck, text="Buck")

left_k = tk.Frame(frame_buck); left_k.pack(side="left", fill="y", padx=10, pady=8)
right_k = tk.Frame(frame_buck); right_k.pack(side="right", fill="y", padx=10, pady=8)
fig_frame_k = tk.Frame(frame_buck); fig_frame_k.pack(side="bottom", fill="both", expand=True, padx=10, pady=6)

tk.Label(left_k, text="Buck - Giriş Parametreleri", font=TITLE_FONT).pack(anchor="w", pady=(0,6))
entry_k_vin = add_entry(left_k, "Vin (V):", 12)          # changed
entry_k_vout = add_entry(left_k, "Vout (V):", 5)         # changed
entry_k_f = add_entry(left_k, "Frekans (kHz):", 50)      # changed
entry_k_L = add_entry(left_k, "L (µH):", 100)            # changed
entry_k_C = add_entry(left_k, "Cout (µF):", 100)         # changed
entry_k_ripI = add_entry(left_k, "Tolerans ΔI (A):", 0.1) # changed (100 mA)
entry_k_ripV = add_entry(left_k, "Tolerans ΔV (V):", 0.1) # changed (0.1 V)

tk.Label(left_k, text="Yük Akımı (A):", font=LABEL_FONT).pack(anchor="w")
slider_k_Iout = tk.Scale(left_k, from_=0.01, to=1.0, resolution=0.01, orient="horizontal", length=260, font=LABEL_FONT)
slider_k_Iout.set(0.5)
slider_k_Iout.pack(anchor="w", pady=(0,8))

tk.Label(left_k, text="Timer Ayarları (PSC/ARR)", font=TITLE_FONT).pack(anchor="w", pady=(6,6))
entry_k_fclk = add_entry(left_k, "f_clk (Hz):", 72000000)
var_k_PSC_fix = tk.BooleanVar()
tk.Checkbutton(left_k, text="PSC Sabit Tut", variable=var_k_PSC_fix, font=LABEL_FONT).pack(anchor="w")
entry_k_PSC = tk.Entry(left_k, font=LABEL_FONT); entry_k_PSC.pack(anchor="w", pady=(0,6))
var_k_ARR_fix = tk.BooleanVar()
tk.Checkbutton(left_k, text="ARR Sabit Tut", variable=var_k_ARR_fix, font=LABEL_FONT).pack(anchor="w")
entry_k_ARR = tk.Entry(left_k, font=LABEL_FONT); entry_k_ARR.pack(anchor="w", pady=(0,10))

btn_k_calc = tk.Button(left_k, text="Hesapla (Buck)", font=LABEL_FONT)
btn_k_calc.pack(pady=(6,12))

tk.Label(right_k, text="Buck - Sonuçlar", font=TITLE_FONT).pack(anchor="w")
out_k_text = tk.Text(right_k, width=50, height=28, font=MONO_FONT)
out_k_text.pack()

fig_k, canvas_k = make_canvas(fig_frame_k)

# ---------- FLYBACK SEKME ----------
frame_f = ttk.Frame(notebook)
notebook.add(frame_f, text="Flyback")

left_f = tk.Frame(frame_f); left_f.pack(side="left", fill="y", padx=10, pady=8)
right_f = tk.Frame(frame_f); right_f.pack(side="right", fill="y", padx=10, pady=8)
fig_frame_f = tk.Frame(frame_f); fig_frame_f.pack(side="bottom", fill="both", expand=True, padx=10, pady=6)

tk.Label(left_f, text="Flyback - Giriş Parametreleri", font=TITLE_FONT).pack(anchor="w", pady=(0,6))
entry_f_vin = add_entry(left_f, "Vin (V):", 28)
entry_f_vout = add_entry(left_f, "Vout (V):", 82)
entry_f_f = add_entry(left_f, "Frekans (kHz):", 50)
entry_f_Lm = add_entry(left_f, "Lm (µH) (primer):", 100)
entry_f_nsnp = add_entry(left_f, "Ns/Np (sec/prim):", 1.0)
entry_f_Iout = add_entry(left_f, "Iout (A):", 10.0)
entry_f_ripI = add_entry(left_f, "Tolerans ΔI (%):", 30)
entry_f_ripV = add_entry(left_f, "Tolerans ΔV (%):", 5)

btn_f_calc = tk.Button(left_f, text="Hesapla (Flyback)", font=LABEL_FONT)
btn_f_calc.pack(pady=(8,12))

tk.Label(right_f, text="Flyback - Sonuçlar", font=TITLE_FONT).pack(anchor="w")
out_f_text = tk.Text(right_f, width=50, height=28, font=MONO_FONT)
out_f_text.pack()

fig_f, canvas_f = make_canvas(fig_frame_f)

# ---------- Hesaplama fonksiyonları ----------
def do_boost_calc():
    try:
        Vin = float(entry_b_vin.get()); Vout = float(entry_b_vout.get())
        freq = float(entry_b_f.get()) * 1e3
        L = float(entry_b_L.get()) * 1e-6
        C = float(entry_b_C.get()) * 1e-6
        ripI_pct = float(entry_b_ripI.get()) / 100.0
        ripV_pct = float(entry_b_ripV.get()) / 100.0
        Iout = float(slider_b_Iout.get())

        if Vout <= Vin:
            messagebox.showerror("Hata", "Boost için Vout > Vin olmalı.")
            return

        D = 1.0 - Vin / Vout
        delta_IL = (Vin * D) / (L * freq)
        delta_Vout = delta_IL / (8.0 * freq * C)
        IL_avg = Iout / (1.0 - D)
        IL_min = IL_avg - delta_IL/2.0
        mode = "CCM" if IL_min > 0 else "DCM"

        # önerilen min L,C
        delta_IL_max = ripI_pct * Iout
        delta_V_max = ripV_pct * Vout
        L_min = (Vin * D) / (delta_IL_max * freq) if delta_IL_max > 0 else float('inf')
        C_min = delta_IL_max / (8.0 * freq * delta_V_max) if delta_V_max > 0 else float('inf')

        # timer
        PSC_calc, ARR_calc = calc_timer_from_inputs(entry_b_fclk.get(), freq, var_b_PSC_fix.get(), var_b_ARR_fix.get(), entry_b_PSC.get(), entry_b_ARR.get())
        entry_b_PSC.delete(0, tk.END); entry_b_PSC.insert(0, str(PSC_calc))
        entry_b_ARR.delete(0, tk.END); entry_b_ARR.insert(0, str(ARR_calc))

        # sonuç yaz
        out_b_text.configure(state="normal"); out_b_text.delete("1.0", tk.END)
        out_b_text.insert(tk.END, f"--- Girilen (Boost) ---\n")
        out_b_text.insert(tk.END, f"Vin={Vin} V, Vout={Vout} V, f={freq/1e3} kHz\n")
        out_b_text.insert(tk.END, f"L={L*1e6:.1f} µH, Cout={C*1e6:.1f} µF, Iout={Iout:.3f} A\n\n")
        out_b_text.insert(tk.END, f"Duty D = {D:.5f}\n")
        out_b_text.insert(tk.END, f"IL(avg) ≈ {IL_avg:.3f} A\n")
        out_b_text.insert(tk.END, f"ΔIL (ideal anlık) = {delta_IL:.3f} A\n")
        out_b_text.insert(tk.END, f"ΔVout (approx) = {delta_Vout:.5f} V\n")
        out_b_text.insert(tk.END, f"Çalışma modu: {mode}\n\n")
        out_b_text.insert(tk.END, f"Önerilen minimum L = {L_min*1e6:.2f} µH\n")
        out_b_text.insert(tk.END, f"Önerilen minimum C = {C_min*1e6:.2f} µF\n\n")
        out_b_text.insert(tk.END, "Dipnot (AMC sensor önerileri):\n")
        out_b_text.insert(tk.END, " - AMC1350 için: voltage divider 330k & 10k.\n")
        out_b_text.insert(tk.END, " - AMC1200 için: voltage divider 330k & 470Ω.\n")
        out_b_text.insert(tk.END, "\n(Not: ΔIL anlık duty sıçramaları içindir; PID/soft-start gerçek ripple'ı düşürür.)\n")
        out_b_text.configure(state="disabled")

        # grafik
        fig_b.clf()
        ax1 = fig_b.add_subplot(211); ax2 = fig_b.add_subplot(212)
        t = np.linspace(0, 4.0 / freq, 600)  # seconds
        tri = triangle_wave(freq, t)
        IL_wave = IL_avg + (delta_IL / 2.0) * tri
        Vout_wave = Vout + (delta_Vout / 2.0) * tri

        ax1.plot(t * 1e6, IL_wave); ax1.set_title("Bobin Akımı (IL) - Boost", fontsize=FONT_BASE+1); ax1.set_ylabel("A", fontsize=FONT_BASE); ax1.grid(True)
        ax2.plot(t * 1e6, Vout_wave, color="red"); ax2.set_title("Çıkış Gerilimi (Vout) - Boost", fontsize=FONT_BASE+1); ax2.set_ylabel("V", fontsize=FONT_BASE); ax2.set_xlabel("Zaman (µs)", fontsize=FONT_BASE); ax2.grid(True)

        fig_b.tight_layout(); canvas_b.draw()

    except Exception as e:
        messagebox.showerror("Hata (Boost)", str(e))


def do_buck_calc():
    try:
        Vin = float(entry_k_vin.get()); Vout = float(entry_k_vout.get())
        freq = float(entry_k_f.get()) * 1e3
        L = float(entry_k_L.get()) * 1e-6
        C = float(entry_k_C.get()) * 1e-6
        ripI_val = float(entry_k_ripI.get())
        ripV_val = float(entry_k_ripV.get())
        Iout = float(slider_k_Iout.get())

        if Vout >= Vin:
            messagebox.showerror("Hata", "Buck için Vout < Vin olmalı.")
            return

        D = Vout / Vin
        delta_IL = (Vin - Vout) * D / (L * freq)
        delta_Vout = delta_IL / (8.0 * freq * C)
        IL_avg = Iout
        IL_min = IL_avg - delta_IL / 2.0
        mode = "CCM" if IL_min > 0 else "DCM"

        # önerilen
        delta_IL_max = ripI_val
        delta_V_max = ripV_val
        L_min = (Vin - Vout) * D / (delta_IL_max * freq) if delta_IL_max > 0 else float('inf')
        C_min = delta_IL_max / (8.0 * freq * delta_V_max) if delta_V_max > 0 else float('inf')

        PSC_calc, ARR_calc = calc_timer_from_inputs(entry_k_fclk.get(), freq, var_k_PSC_fix.get(), var_k_ARR_fix.get(), entry_k_PSC.get(), entry_k_ARR.get())
        entry_k_PSC.delete(0, tk.END); entry_k_PSC.insert(0, str(PSC_calc))
        entry_k_ARR.delete(0, tk.END); entry_k_ARR.insert(0, str(ARR_calc))

        out_k_text.configure(state="normal"); out_k_text.delete("1.0", tk.END)
        out_k_text.insert(tk.END, f"--- Girilen (Buck) ---\n")
        out_k_text.insert(tk.END, f"Vin={Vin} V, Vout={Vout} V, f={freq/1e3} kHz\n")
        out_k_text.insert(tk.END, f"L={L*1e6:.1f} µH, Cout={C*1e6:.1f} µF, Iout={Iout:.3f} A\n\n")
        out_k_text.insert(tk.END, f"Duty D = {D:.5f}\n")
        out_k_text.insert(tk.END, f"IL(avg) = {IL_avg:.3f} A\n")
        out_k_text.insert(tk.END, f"ΔIL (ideal) = {delta_IL:.3f} A\n")
        out_k_text.insert(tk.END, f"ΔVout (approx) = {delta_Vout:.5f} V\n")
        out_k_text.insert(tk.END, f"Çalışma modu: {mode}\n\n")
        out_k_text.insert(tk.END, f"Önerilen minimum L = {L_min*1e6:.2f} µH\n")
        out_k_text.insert(tk.END, f"Önerilen minimum C = {C_min*1e6:.2f} µF\n")
        out_k_text.configure(state="disabled")

        # grafik
        fig_k.clf()
        ax1 = fig_k.add_subplot(211); ax2 = fig_k.add_subplot(212)
        t = np.linspace(0, 4.0 / freq, 600)
        tri = triangle_wave(freq, t)
        IL_wave = IL_avg + (delta_IL / 2.0) * tri
        Vout_wave = Vout + (delta_Vout / 2.0) * tri

        ax1.plot(t * 1e6, IL_wave); ax1.set_title("Bobin Akımı (IL) - Buck", fontsize=FONT_BASE+1); ax1.set_ylabel("A", fontsize=FONT_BASE); ax1.grid(True)
        ax2.plot(t * 1e6, Vout_wave, color="red"); ax2.set_title("Çıkış Gerilimi (Vout) - Buck", fontsize=FONT_BASE+1); ax2.set_ylabel("V", fontsize=FONT_BASE); ax2.set_xlabel("Zaman (µs)", fontsize=FONT_BASE); ax2.grid(True)

        fig_k.tight_layout(); canvas_k.draw()

    except Exception as e:
        messagebox.showerror("Hata (Buck)", str(e))


def do_fly_calc():
    try:
        Vin = float(entry_f_vin.get()); Vout = float(entry_f_vout.get())
        freq = float(entry_f_f.get()) * 1e3
        Lm = float(entry_f_Lm.get()) * 1e-6
        nsnp = float(entry_f_nsnp.get())
        Iout = float(entry_f_Iout.get())
        ripI_pct = float(entry_f_ripI.get()) / 100.0
        ripV_pct = float(entry_f_ripV.get()) / 100.0

        denom = Vout + (Vin * (1.0 / nsnp)) if nsnp != 0 else None
        if denom is None or denom == 0:
            messagebox.showerror("Hata", "Geçersiz Ns/Np değeri.")
            return
        D = Vout / denom
        D = max(1e-6, min(0.999999, D))
        Pout = Vout * Iout
        Fs = freq
        if Lm <= 0:
            Ipk = float('inf')
            delta_I_m = float('inf')
        else:
            Ipk = np.sqrt(max(0.0, 2.0 * Pout / (Lm * Fs)))
            delta_I_m = (Vin * D) / (Lm * Fs)

        eff = 0.9
        Iin = Pout / (Vin * eff) if Vin > 0 else 0.0
        Iavg = Iin
        IL_min = Iavg - delta_I_m / 2.0
        mode = "CCM" if IL_min > 0 else "DCM"
        nsnp_req = (Vout * (1.0 - D)) / (Vin * D) if D != 0 else float('inf')

        out_f_text.configure(state="normal"); out_f_text.delete("1.0", tk.END)
        out_f_text.insert(tk.END, f"--- Girilen (Flyback) ---\n")
        out_f_text.insert(tk.END, f"Vin={Vin} V, Vout={Vout} V, f={freq/1e3} kHz\n")
        out_f_text.insert(tk.END, f"Lm={Lm*1e6:.1f} µH, Ns/Np (girilen)={nsnp:.3f}, Iout={Iout:.3f} A\n\n")
        out_f_text.insert(tk.END, f"Duty ~ {D:.5f}\n")
        out_f_text.insert(tk.END, f"Önerilen Ns/Np (hesap) = {nsnp_req:.4f}\n")
        out_f_text.insert(tk.END, f"Ipk (approx) = {Ipk:.3f} A\n")
        out_f_text.insert(tk.END, f"Primer magnetizing ΔI (approx) = {delta_I_m:.3f} A\n")
        out_f_text.insert(tk.END, f"Ortalama primer I ≈ {Iavg:.3f} A\n")
        out_f_text.insert(tk.END, f"Çalışma modu: {mode}\n\n")
        out_f_text.insert(tk.END, "(Not: Flyback hesapları ideal, gerçekte diyot düşümü, verim, çekirdek özellikleri önemlidir.)\n")
        out_f_text.configure(state="disabled")

        # grafik
        fig_f.clf()
        ax1 = fig_f.add_subplot(211); ax2 = fig_f.add_subplot(212)
        t = np.linspace(0, 4.0 / freq, 600)
        tri = triangle_wave(freq, t)
        IL_wave = Iavg + (delta_I_m / 2.0) * tri
        Vsec_wave = Vout * np.ones_like(t)

        ax1.plot(t * 1e6, IL_wave); ax1.set_title("Primer Bobin Akımı (approx) - Flyback", fontsize=FONT_BASE+1); ax1.set_ylabel("A", fontsize=FONT_BASE); ax1.grid(True)
        ax2.plot(t * 1e6, Vsec_wave, color="green"); ax2.set_title("Sekonder Gerilim (approx) - Flyback", fontsize=FONT_BASE+1); ax2.set_ylabel("V", fontsize=FONT_BASE); ax2.set_xlabel("Zaman (µs)", fontsize=FONT_BASE); ax2.grid(True)

        fig_f.tight_layout(); canvas_f.draw()

    except Exception as e:
        messagebox.showerror("Hata (Flyback)", str(e))

# butonlara bağla
btn_b_calc.config(command=do_boost_calc)
btn_k_calc.config(command=do_buck_calc)
btn_f_calc.config(command=do_fly_calc)

# başta hepsi için bir hesap çalıştır (varsayılanları göster)
do_boost_calc()
do_buck_calc()
do_fly_calc()

root.mainloop()
