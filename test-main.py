import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import keyboard
import time
import random
import requests
import os
import sys
import webbrowser

# ---------- Sun Valley Teması İçin sv_ttk ----------
try:
    import sv_ttk
    sv_ttk.set_theme("dark")
    default_theme = "sv_dark"  # Tema mapping için kullanılacak isim
except ImportError:
    messagebox.showerror("Tema Hatası", "sv_ttk paketi yüklenmedi!\n(Pip ile 'pip install sv_ttk' komutunu kullanın.)")
    default_theme = "win11_custom"  # Alternatif tema

# ---------- Diğer Tema Ayarları ----------
def create_win11_theme(style):
    style.theme_create("win11_custom", parent="clam", settings={
        ".": {"configure": {"background": "#f3f3f3", "foreground": "#000000", "font": ("Segoe UI", 10)}},
        "TButton": {"configure": {"padding": 6, "relief": "flat", "background": "#0078D7", "foreground": "white"},
                     "map": {"background": [("active", "#005A9E")]}},
        "TLabel": {"configure": {"background": "#f3f3f3"}},
        "TFrame": {"configure": {"background": "#f3f3f3"}},
        "TLabelframe": {"configure": {"background": "#f3f3f3", "foreground": "#0078D7"}},
        "TLabelframe.Label": {"configure": {"font": ("Segoe UI", 10, "bold")}},
        "TEntry": {"configure": {"padding": 4}},
        "TCombobox": {"configure": {"padding": 4}},
    })

def create_classic_theme(style):
    style.theme_create("classic_custom", parent="clam", settings={
        ".": {"configure": {"background": "#d9d9d9", "foreground": "#000000", "font": ("Arial", 9)}},
        "TButton": {"configure": {"padding": 4, "relief": "raised", "background": "#c0c0c0", "foreground": "black"},
                     "map": {"background": [("active", "#a0a0a0")]}},
        "TLabel": {"configure": {"background": "#d9d9d9"}},
        "TFrame": {"configure": {"background": "#d9d9d9"}},
        "TLabelframe": {"configure": {"background": "#d9d9d9", "foreground": "#00008B"}},
        "TLabelframe.Label": {"configure": {"font": ("Arial", 9, "bold")}},
        "TEntry": {"configure": {"padding": 2}},
        "TCombobox": {"configure": {"padding": 2}},
    })

def create_modern_theme(style):
    style.theme_create("modern_custom", parent="clam", settings={
        ".": {"configure": {"background": "#2b2b2b", "foreground": "#ffffff", "font": ("Verdana", 10)}},
        "TButton": {"configure": {"padding": 6, "relief": "flat", "background": "#3c3f41", "foreground": "#ffffff"},
                     "map": {"background": [("active", "#555759")]}},
        "TLabel": {"configure": {"background": "#2b2b2b"}},
        "TFrame": {"configure": {"background": "#2b2b2b"}},
        "TLabelframe": {"configure": {"background": "#2b2b2b", "foreground": "#ffffff"}},
        "TLabelframe.Label": {"configure": {"font": ("Verdana", 10, "bold"), "foreground": "#ffffff"}},
        "TEntry": {"configure": {"padding": 4, "fieldbackground": "#5c5c5c", "foreground": "#ffffff"}},
        "TCombobox": {"configure": {"padding": 4, "background": "#5c5c5c", "foreground": "#ffffff"}},
    })

def create_azure_dark_theme(style):
    style.theme_create("azure_dark_custom", parent="clam", settings={
        ".": {"configure": {"background": "#323232", "foreground": "#e0e0e0", "font": ("Segoe UI", 10)}},
        "TButton": {"configure": {"padding": 6, "relief": "flat", "background": "#0078D7", "foreground": "#ffffff"},
                     "map": {"background": [("active", "#005A9E")]}},
        "TLabel": {"configure": {"background": "#323232"}},
        "TFrame": {"configure": {"background": "#323232"}},
        "TLabelframe": {"configure": {"background": "#323232", "foreground": "#0078D7"}},
        "TLabelframe.Label": {"configure": {"font": ("Segoe UI", 10, "bold")}},
        "TEntry": {"configure": {"padding": 4, "fieldbackground": "#505050", "foreground": "#e0e0e0"}},
        "TCombobox": {"configure": {"padding": 4, "fieldbackground": "#505050", "foreground": "#e0e0e0"}},
    })

def setup_style(root):
    style = ttk.Style(root)
    try:
        style.theme_use(default_theme)
    except tk.TclError:
        create_win11_theme(style)
        style.theme_use("win11_custom")
    create_classic_theme(style)
    create_modern_theme(style)
    create_azure_dark_theme(style)
    return style

# ---------- Uygulama Sınıfı ----------
class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker - Gelişmiş Arayüz")
        self.root.geometry("600x700")
        self.root.resizable(True, True)

        self.style = setup_style(root)

        # Tema seçenekleri (Sun Valley varsayılan)
        self.available_themes = ["Sun Valley", "Windows 11", "Klasik", "Modern", "Azure Dark"]
        self.theme_mapping = {
            "Sun Valley": default_theme,
            "Windows 11": "win11_custom",
            "Klasik": "classic_custom",
            "Modern": "modern_custom",
            "Azure Dark": "azure_dark_custom"
        }

        self.current_version = "0.4"
        self.is_running = False
        self.click_thread = None
        self.hotkey = "f6"
        self.fullscreen = False

        # Değişkenler
        self.click_type = tk.StringVar(value="left")
        self.interval_value = tk.StringVar(value="100")
        # Burada interval tipleri arasında "ms", "saniye", "dakika" yanında "cps" da ekleniyor.
        self.interval_type = tk.StringVar(value="ms")
        self.random_interval = tk.BooleanVar(value=False)
        self.min_interval = tk.StringVar(value="80")
        self.max_interval = tk.StringVar(value="150")
        self.delay = tk.StringVar(value="0")
        self.click_count = tk.StringVar(value="0")
        self.pos_mode = tk.StringVar(value="current")
        self.custom_x = tk.StringVar(value="0")
        self.custom_y = tk.StringVar(value="0")

        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)

        self.create_widgets()
        self.check_for_updates()

    def create_widgets(self):
        # Üst bilgi bölümü
        info_frame = ttk.LabelFrame(self.root, text="Güncelleme Bilgisi")
        info_frame.place(x=10, y=10, width=580, height=50)
        self.info_label = ttk.Label(info_frame, text=f"Sürüm: {self.current_version}", font=("Segoe UI", 12))
        self.info_label.pack(padx=10, pady=5)

        # Tıklama seçenekleri
        options_frame = ttk.LabelFrame(self.root, text="Tıklama Seçenekleri")
        options_frame.place(x=10, y=70, width=580, height=100)
        ttk.Label(options_frame, text="Tıklama Türü:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(options_frame, text="Sol Tık", variable=self.click_type, value="left").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(options_frame, text="Sağ Tık", variable=self.click_type, value="right").grid(row=0, column=2, padx=5)
        ttk.Radiobutton(options_frame, text="Çift Tık", variable=self.click_type, value="double").grid(row=0, column=3, padx=5)

        ttk.Label(options_frame, text="Tıklama Aralığı:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(options_frame, textvariable=self.interval_value, width=10).grid(row=1, column=1, padx=5)
        # Combobox değerlerine "cps" de eklendi.
        interval_types = ttk.Combobox(options_frame, textvariable=self.interval_type, width=10, state="readonly")
        interval_types['values'] = ("ms", "saniye", "dakika", "cps")
        interval_types.grid(row=1, column=2, padx=5)
        ttk.Checkbutton(options_frame, text="Rastgele Aralık", variable=self.random_interval,
                        command=self.toggle_random_interval).grid(row=2, column=0, padx=5, pady=5)
        ttk.Label(options_frame, text="Min:").grid(row=2, column=1, sticky="e")
        self.min_entry = ttk.Entry(options_frame, textvariable=self.min_interval, width=8, state="disabled")
        self.min_entry.grid(row=2, column=2, padx=5)
        ttk.Label(options_frame, text="Max:").grid(row=2, column=3, sticky="e")
        self.max_entry = ttk.Entry(options_frame, textvariable=self.max_interval, width=8, state="disabled")
        self.max_entry.grid(row=2, column=4, padx=5)

        # Ek özellikler
        extra_frame = ttk.LabelFrame(self.root, text="Ek Özellikler")
        extra_frame.place(x=10, y=180, width=580, height=80)
        ttk.Label(extra_frame, text="Başlangıç Gecikmesi (s):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(extra_frame, textvariable=self.delay, width=8).grid(row=0, column=1, padx=5)
        ttk.Label(extra_frame, text="Tıklama Sayısı (0 = sınırsız):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(extra_frame, textvariable=self.click_count, width=8).grid(row=0, column=3, padx=5)

        # Tıklama konumu
        pos_frame = ttk.LabelFrame(self.root, text="Tıklama Konumu")
        pos_frame.place(x=10, y=270, width=580, height=80)
        ttk.Radiobutton(pos_frame, text="Mevcut Fare Pozisyonu", variable=self.pos_mode, value="current",
                        command=self.toggle_custom_position).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(pos_frame, text="Özel Koordinat", variable=self.pos_mode, value="custom",
                        command=self.toggle_custom_position).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(pos_frame, text="X:").grid(row=1, column=0, padx=5, sticky="e")
        self.x_entry = ttk.Entry(pos_frame, textvariable=self.custom_x, width=8, state="disabled")
        self.x_entry.grid(row=1, column=1, padx=5, sticky="w")
        ttk.Label(pos_frame, text="Y:").grid(row=1, column=2, padx=5, sticky="e")
        self.y_entry = ttk.Entry(pos_frame, textvariable=self.custom_y, width=8, state="disabled")
        self.y_entry.grid(row=1, column=3, padx=5, sticky="w")
        ttk.Button(pos_frame, text="Fare Konumunu Al", command=self.pick_location).grid(row=1, column=4, padx=10)

        # Tema seçimi
        theme_frame = ttk.LabelFrame(self.root, text="Tema Seçimi")
        theme_frame.place(x=10, y=360, width=580, height=70)
        ttk.Label(theme_frame, text="Tema:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.theme_var = tk.StringVar(value=self.available_themes[0])
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=self.available_themes, state="readonly")
        theme_combo.grid(row=0, column=1, padx=5)
        ttk.Button(theme_frame, text="Uygula", command=self.change_theme).grid(row=0, column=2, padx=5)

        # Kısayol ayarları
        hotkey_frame = ttk.LabelFrame(self.root, text="Kısayol Tuşu")
        hotkey_frame.place(x=10, y=440, width=580, height=70)
        ttk.Label(hotkey_frame, text="Başlat/Durdur Tuşu:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(hotkey_frame, text=f"(Şu an: {self.hotkey.upper()})").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(hotkey_frame, text="Değiştir", command=self.prompt_hotkey).grid(row=0, column=2, padx=5)

        # Kontrol butonları
        control_frame = ttk.Frame(self.root)
        control_frame.place(x=10, y=520, width=580, height=60)
        self.start_button = ttk.Button(control_frame, text=f"Başlat ({self.hotkey.upper()})", command=self.start_clicking)
        self.start_button.pack(side="left", expand=True, fill="x", padx=5)
        self.stop_button = ttk.Button(control_frame, text="Durdur", command=self.stop_clicking, state="disabled")
        self.stop_button.pack(side="right", expand=True, fill="x", padx=5)

        # Durum çubuğu
        self.status_var = tk.StringVar(value="Hazır")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.place(x=0, y=650, width=600, height=20)

    def toggle_random_interval(self):
        state = "normal" if self.random_interval.get() else "disabled"
        self.min_entry.config(state=state)
        self.max_entry.config(state=state)

    def toggle_custom_position(self):
        state = "normal" if self.pos_mode.get() == "custom" else "disabled"
        self.x_entry.config(state=state)
        self.y_entry.config(state=state)

    def pick_location(self):
        x, y = pyautogui.position()
        self.custom_x.set(str(x))
        self.custom_y.set(str(y))
        self.pos_mode.set("custom")
        self.toggle_custom_position()
        self.status_var.set(f"Konum alındı: X={x}, Y={y}")

    def change_theme(self):
        new_theme = self.theme_var.get()
        mapped_theme = self.theme_mapping.get(new_theme, default_theme)
        try:
            ttk.Style().theme_use(mapped_theme)
            self.status_var.set(f"Tema '{new_theme}' olarak uygulandı.")
        except tk.TclError as e:
            messagebox.showerror("Hata", f"Tema değiştirilemedi: {e}")

    def prompt_hotkey(self):
        top = tk.Toplevel(self.root)
        top.title("Kısayol Değiştir")
        top.geometry("300x100")
        ttk.Label(top, text="Yeni kısayol tuşuna basın...").pack(pady=10)

        def on_key_press(event):
            new_hotkey = event.keysym
            try:
                keyboard.remove_hotkey(self.hotkey)
            except:
                pass
            self.hotkey = new_hotkey.lower()
            keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
            self.start_button.config(text=f"Başlat ({self.hotkey.upper()})")
            top.destroy()

        top.bind("<Key>", on_key_press)
        top.focus_force()

    def toggle_clicking(self):
        if self.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        if self.is_running:
            return
        try:
            delay_sec = float(self.delay.get())
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir gecikme süresi giriniz.")
            return
        try:
            total_clicks = int(self.click_count.get())
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir tıklama sayısı giriniz.")
            return

        # CPS seçeneği için ayrı hesaplama yapılıyor.
        unit = self.interval_type.get()
        if unit == "cps":
            try:
                cps_value = float(self.interval_value.get())
                if cps_value <= 0:
                    raise ValueError("CPS 0 veya negatif olamaz.")
                # Tıklama aralığı saniye cinsinden = 1 / cps
                interval_seconds = 1.0 / cps_value
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir CPS değeri giriniz.")
                return
            get_interval = lambda: interval_seconds
            multiplier = 1  # Artık hesaplamaya gerek yok.
        else:
            if self.random_interval.get():
                try:
                    min_val = float(self.min_interval.get())
                    max_val = float(self.max_interval.get())
                    if min_val > max_val:
                        raise ValueError("Min aralık, max aralıktan büyük olamaz.")
                except ValueError as ve:
                    messagebox.showerror("Hata", f"Rastgele aralık değeri hatası: {ve}")
                    return
                get_interval = lambda: random.uniform(min_val, max_val)
            else:
                try:
                    interval = float(self.interval_value.get())
                except ValueError:
                    messagebox.showerror("Hata", "Geçerli bir aralık değeri giriniz.")
                    return
                get_interval = lambda: interval

            multiplier = 1
            if unit == "saniye":
                multiplier = 1000
            elif unit == "dakika":
                multiplier = 60000

        if delay_sec > 0:
            self.status_var.set(f"{delay_sec} saniye sonra başlıyor...")
            time.sleep(delay_sec)

        self.is_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_var.set("Çalışıyor...")

        self.click_thread = threading.Thread(
            target=self.clicking_loop,
            args=(get_interval, multiplier, total_clicks)
        )
        self.click_thread.daemon = True
        self.click_thread.start()

    def clicking_loop(self, get_interval, multiplier, total_clicks):
        clicks_done = 0
        try:
            while self.is_running:
                if self.pos_mode.get() == "custom":
                    try:
                        x = int(self.custom_x.get())
                        y = int(self.custom_y.get())
                    except ValueError:
                        self.status_var.set("Özel koordinatlar geçersiz, mevcut pozisyon kullanılacak.")
                        x, y = pyautogui.position()
                else:
                    x, y = pyautogui.position()

                if self.click_type.get() == "left":
                    pyautogui.click(x=x, y=y)
                elif self.click_type.get() == "right":
                    pyautogui.rightClick(x=x, y=y)
                elif self.click_type.get() == "double":
                    pyautogui.doubleClick(x=x, y=y)

                clicks_done += 1
                if total_clicks != 0 and clicks_done >= total_clicks:
                    break

                interval = get_interval() * multiplier / 1000.0
                if interval < 0.01:
                    interval = 0.01
                time.sleep(interval)
        except Exception as e:
            self.status_var.set(str(e))
        finally:
            self.stop_clicking()

    def stop_clicking(self):
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_var.set("Durduruldu")
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join(1.0)

    def check_for_updates(self):
        try:
            self.status_var.set("Güncellemeler kontrol ediliyor...")
            version_url = "https://raw.githubusercontent.com/ATOMGAMERAGA/autoc/main/VERSION.txt"
            response = requests.get(version_url, timeout=5)
            if response.status_code == 200:
                latest_version = response.text.strip()
                if latest_version > self.current_version:
                    if messagebox.askyesno("Güncelleme Mevcut",
                                           f"Yeni sürüm: {latest_version}\nŞu anki sürüm: {self.current_version}\n\nGüncellemek ister misiniz?"):
                        self.update_application(latest_version)
                else:
                    self.status_var.set(f"En son sürümü kullanıyorsunuz: {self.current_version}")
            else:
                self.status_var.set("Güncelleme kontrolü başarısız oldu.")
        except Exception as e:
            self.status_var.set(f"Güncelleme kontrolü başarısız: {e}")

    def update_application(self, new_version):
        try:
            self.status_var.set("Uygulama güncelleniyor...")
            script_url = "https://raw.githubusercontent.com/ATOMGAMERAGA/autoc/main/test-main.py"
            response = requests.get(script_url, timeout=10)
            if response.status_code == 200:
                if getattr(sys, 'frozen', False):
                    application_path = os.path.dirname(sys.executable)
                    script_path = os.path.join(application_path, "test-main.py")
                else:
                    script_path = os.path.abspath(__file__)
                backup_path = script_path + ".bak"
                try:
                    os.rename(script_path, backup_path)
                except:
                    pass
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                with open(os.path.join(os.path.dirname(script_path), "VERSION.txt"), "w") as f:
                    f.write(new_version)
                messagebox.showinfo("Güncelleme Tamamlandı",
                                    f"Uygulama sürüm {new_version} olarak güncellendi.\nDeğişikliklerin etkili olması için uygulamayı yeniden başlatın.")
                self.root.after(1000, self.root.destroy)
            else:
                raise Exception(f"İndirme başarısız oldu: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Güncelleme Hatası", e)
            self.status_var.set("Güncelleme başarısız oldu")

    def open_help(self):
        webbrowser.open("https://github.com/ATOMGAMERAGA/autoc")

if __name__ == "__main__":
    pyautogui.alert(
        "Bu uygulama, ekranınızda otomatik tıklamalar yapmak için izin gerektirir.\nDevam etmek için 'OK' tuşuna basın.",
        "Ekran Erişim İzni"
    )
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()