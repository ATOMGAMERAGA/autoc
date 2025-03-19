import customtkinter as ctk
import pyautogui
import threading
import keyboard
import time
import random
import requests
import os
import sys
import webbrowser

# CustomTkinter ayarları: Varsayılan olarak Windows 11 görünümünü ayarlıyoruz.
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")  # Windows 11'e benzer tema

class AutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AutoClicker - Gelişmiş Arayüz")
        self.geometry("600x700")
        self.resizable(True, True)

        # Uygulama genel değişkenleri
        self.current_version = "0.3"
        self.is_running = False
        self.click_thread = None
        self.hotkey = "f6"  # Varsayılan kısayol
        self.fullscreen = False

        # Değişkenler
        self.click_type = ctk.StringVar(value="left")
        self.interval_value = ctk.StringVar(value="100")
        self.interval_type = ctk.StringVar(value="ms")
        self.random_interval = ctk.BooleanVar(value=False)
        self.min_interval = ctk.StringVar(value="80")
        self.max_interval = ctk.StringVar(value="150")
        self.delay = ctk.StringVar(value="0")
        self.click_count = ctk.StringVar(value="0")
        self.pos_mode = ctk.StringVar(value="current")
        self.custom_x = ctk.StringVar(value="0")
        self.custom_y = ctk.StringVar(value="0")

        # Tema seçenekleri (default: Windows 11)
        self.available_themes = ["Windows 11", "Klasik", "Modern", "Azure Dark"]

        # Global kısayol ekle
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)

        # Ana çerçeveleri oluştur
        self.create_widgets()
        self.check_for_updates()

    def create_widgets(self):
        # Üst bilgi paneli: Uygulama bilgisi/güncelleme durumu
        info_frame = ctk.CTkFrame(self, height=40, corner_radius=10)
        info_frame.pack(pady=(10, 0), padx=10, fill="x")
        self.info_label = ctk.CTkLabel(info_frame, text=f"Sürüm: {self.current_version}", font=("Segoe UI", 12))
        self.info_label.pack(pady=5, padx=10)

        # Ana içerik alanı
        content_frame = ctk.CTkFrame(self, corner_radius=10)
        content_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Tıklama Seçenekleri ---
        options_frame = ctk.CTkFrame(content_frame, height=120, corner_radius=10)
        options_frame.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(options_frame, text="Tıklama Seçenekleri", font=("Segoe UI", 14, "bold")).pack(pady=(5,0))

        type_frame = ctk.CTkFrame(options_frame, corner_radius=10)
        type_frame.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(type_frame, text="Tıklama Türü:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkRadioButton(type_frame, text="Sol Tık", variable=self.click_type, value="left", corner_radius=8).grid(row=0, column=1, padx=5)
        ctk.CTkRadioButton(type_frame, text="Sağ Tık", variable=self.click_type, value="right", corner_radius=8).grid(row=0, column=2, padx=5)
        ctk.CTkRadioButton(type_frame, text="Çift Tık", variable=self.click_type, value="double", corner_radius=8).grid(row=0, column=3, padx=5)

        # Aralık Ayarları
        interval_frame = ctk.CTkFrame(options_frame, corner_radius=10)
        interval_frame.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(interval_frame, text="Tıklama Aralığı:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkEntry(interval_frame, textvariable=self.interval_value, width=80, corner_radius=8).grid(row=0, column=1, padx=5)
        self.interval_combo = ctk.CTkOptionMenu(interval_frame, variable=self.interval_type, values=["ms", "saniye", "dakika"])
        self.interval_combo.grid(row=0, column=2, padx=5)
        self.random_check = ctk.CTkCheckBox(interval_frame, text="Rastgele Aralık", variable=self.random_interval, command=self.toggle_random_interval, corner_radius=8)
        self.random_check.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(interval_frame, text="Min:").grid(row=1, column=1, padx=5, sticky="e")
        self.min_entry = ctk.CTkEntry(interval_frame, textvariable=self.min_interval, width=60, corner_radius=8, state="disabled")
        self.min_entry.grid(row=1, column=2, padx=5, sticky="w")
        ctk.CTkLabel(interval_frame, text="Max:").grid(row=1, column=3, padx=5, sticky="e")
        self.max_entry = ctk.CTkEntry(interval_frame, textvariable=self.max_interval, width=60, corner_radius=8, state="disabled")
        self.max_entry.grid(row=1, column=4, padx=5, sticky="w")

        # --- Ek Özellikler ---
        extra_frame = ctk.CTkFrame(content_frame, height=80, corner_radius=10)
        extra_frame.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(extra_frame, text="Ek Özellikler", font=("Segoe UI", 14, "bold")).pack(pady=(5,0))
        extras = ctk.CTkFrame(extra_frame, corner_radius=10)
        extras.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(extras, text="Başlangıç Gecikmesi (s):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkEntry(extras, textvariable=self.delay, width=80, corner_radius=8).grid(row=0, column=1, padx=5)
        ctk.CTkLabel(extras, text="Tıklama Sayısı (0 = sınırsız):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkEntry(extras, textvariable=self.click_count, width=80, corner_radius=8).grid(row=0, column=3, padx=5)

        # --- Tıklama Konumu ---
        pos_frame = ctk.CTkFrame(content_frame, height=100, corner_radius=10)
        pos_frame.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(pos_frame, text="Tıklama Konumu", font=("Segoe UI", 14, "bold")).pack(pady=(5,0))
        pos_inner = ctk.CTkFrame(pos_frame, corner_radius=10)
        pos_inner.pack(pady=5, padx=5, fill="x")
        ctk.CTkRadioButton(pos_inner, text="Mevcut Fare Pozisyonu", variable=self.pos_mode, value="current", command=self.toggle_custom_position, corner_radius=8).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkRadioButton(pos_inner, text="Özel Koordinat", variable=self.pos_mode, value="custom", command=self.toggle_custom_position, corner_radius=8).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(pos_inner, text="X:").grid(row=1, column=0, padx=5, sticky="e")
        self.x_entry = ctk.CTkEntry(pos_inner, textvariable=self.custom_x, width=80, corner_radius=8, state="disabled")
        self.x_entry.grid(row=1, column=1, padx=5, sticky="w")
        ctk.CTkLabel(pos_inner, text="Y:").grid(row=1, column=2, padx=5, sticky="e")
        self.y_entry = ctk.CTkEntry(pos_inner, textvariable=self.custom_y, width=80, corner_radius=8, state="disabled")
        self.y_entry.grid(row=1, column=3, padx=5, sticky="w")
        ctk.CTkButton(pos_inner, text="Fare Konumunu Al", command=self.pick_location, corner_radius=8).grid(row=1, column=4, padx=10)

        # --- Tema Seçimi ---
        theme_frame = ctk.CTkFrame(content_frame, height=80, corner_radius=10)
        theme_frame.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(theme_frame, text="Tema Seçimi", font=("Segoe UI", 14, "bold")).pack(pady=(5,0))
        theme_inner = ctk.CTkFrame(theme_frame, corner_radius=10)
        theme_inner.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(theme_inner, text="Tema:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.theme_var = ctk.StringVar(value=self.available_themes[0])  # Varsayılan: Windows 11
        self.theme_option = ctk.CTkOptionMenu(theme_inner, variable=self.theme_var, values=self.available_themes)
        self.theme_option.grid(row=0, column=1, padx=5)
        ctk.CTkButton(theme_inner, text="Uygula", command=self.change_theme, corner_radius=8).grid(row=0, column=2, padx=5)

        # --- Kısayol Ayarları ---
        hotkey_frame = ctk.CTkFrame(content_frame, height=80, corner_radius=10)
        hotkey_frame.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(hotkey_frame, text="Kısayol Ayarları", font=("Segoe UI", 14, "bold")).pack(pady=(5,0))
        hotkey_inner = ctk.CTkFrame(hotkey_frame, corner_radius=10)
        hotkey_inner.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(hotkey_inner, text="Başlat/Durdur Tuşu:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.hotkey_label = ctk.CTkLabel(hotkey_inner, text=f"(Şu an: {self.hotkey.upper()})")
        self.hotkey_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkButton(hotkey_inner, text="Değiştir", command=self.prompt_hotkey, corner_radius=8).grid(row=0, column=2, padx=5)

        # --- Kontrol Butonları ---
        control_frame = ctk.CTkFrame(content_frame, height=60, corner_radius=10)
        control_frame.pack(pady=5, padx=5, fill="x")
        self.start_button = ctk.CTkButton(control_frame, text=f"Başlat ({self.hotkey.upper()})", command=self.start_clicking, corner_radius=8)
        self.start_button.pack(side="left", expand=True, fill="x", padx=5, pady=5)
        self.stop_button = ctk.CTkButton(control_frame, text="Durdur", command=self.stop_clicking, state="disabled", corner_radius=8)
        self.stop_button.pack(side="right", expand=True, fill="x", padx=5, pady=5)

        # --- Ek Butonlar (Yardım & Tam Ekran) ---
        extra_buttons_frame = ctk.CTkFrame(content_frame, height=40, corner_radius=10)
        extra_buttons_frame.pack(pady=5, padx=5, fill="x")
        self.help_button = ctk.CTkButton(extra_buttons_frame, text="Yardım", command=self.open_help, corner_radius=8)
        self.help_button.pack(side="left", expand=True, fill="x", padx=5)
        self.fullscreen_button = ctk.CTkButton(extra_buttons_frame, text="Tam Ekran", command=self.toggle_fullscreen, corner_radius=8)
        self.fullscreen_button.pack(side="left", expand=True, fill="x", padx=5)

        # Alt durum çubuğu
        self.status_var = ctk.StringVar(value="Hazır")
        self.status_label = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w", height=20)
        self.status_label.pack(side="bottom", fill="x", padx=10, pady=(0,10))

    def toggle_random_interval(self):
        state = "normal" if self.random_interval.get() else "disabled"
        self.min_entry.configure(state=state)
        self.max_entry.configure(state=state)

    def toggle_custom_position(self):
        state = "normal" if self.pos_mode.get() == "custom" else "disabled"
        self.x_entry.configure(state=state)
        self.y_entry.configure(state=state)

    def pick_location(self):
        x, y = pyautogui.position()
        self.custom_x.set(str(x))
        self.custom_y.set(str(y))
        self.pos_mode.set("custom")
        self.toggle_custom_position()
        self.status_var.set(f"Konum alındı: X={x}, Y={y}")

    def change_theme(self):
        new_theme = self.theme_var.get()
        try:
            if new_theme == "Windows 11":
                ctk.set_appearance_mode("light")
                ctk.set_default_color_theme("blue")
            elif new_theme == "Klasik":
                ctk.set_appearance_mode("light")
                ctk.set_default_color_theme("green")
            elif new_theme == "Modern":
                ctk.set_appearance_mode("dark")
                ctk.set_default_color_theme("dark-blue")
            elif new_theme == "Azure Dark":
                ctk.set_appearance_mode("dark")
                # Azure Dark temasını özel bir JSON dosyası ile kullanmak isterseniz:
                # ctk.set_default_color_theme("azure_dark.json")
                ctk.set_default_color_theme("dark-blue")
            self.status_var.set(f"Tema '{new_theme}' olarak uygulandı.")
        except Exception as e:
            self.status_var.set(f"Tema değiştirilemedi: {str(e)}")

    def prompt_hotkey(self):
        top = ctk.CTkToplevel(self)
        top.title("Kısayol Değiştir")
        top.geometry("300x100")
        ctk.CTkLabel(top, text="Yeni kısayol tuşuna basın...").pack(pady=10)

        def on_key_press(event):
            new_hotkey = event.keysym
            try:
                keyboard.remove_hotkey(self.hotkey)
            except:
                pass
            self.hotkey = new_hotkey.lower()
            keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
            self.start_button.configure(text=f"Başlat ({self.hotkey.upper()})")
            self.hotkey_label.configure(text=f"(Şu an: {self.hotkey.upper()})")
            self.status_var.set(f"Kısayol tuşu {self.hotkey.upper()} olarak ayarlandı.")
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
            try:
                delay_sec = float(self.delay.get())
            except ValueError:
                self.status_var.set("Geçerli bir gecikme süresi giriniz.")
                return
            try:
                total_clicks = int(self.click_count.get())
            except ValueError:
                self.status_var.set("Geçerli bir tıklama sayısı giriniz.")
                return

            if self.random_interval.get():
                try:
                    min_val = float(self.min_interval.get())
                    max_val = float(self.max_interval.get())
                    if min_val > max_val:
                        raise ValueError("Min aralık, max aralıktan büyük olamaz.")
                except ValueError as ve:
                    self.status_var.set(f"Rastgele aralık değeri hatası: {ve}")
                    return
                get_interval = lambda: random.uniform(min_val, max_val)
            else:
                try:
                    interval = float(self.interval_value.get())
                except ValueError:
                    self.status_var.set("Geçerli bir aralık değeri giriniz.")
                    return
                get_interval = lambda: interval

            unit = self.interval_type.get()
            multiplier = 1
            if unit == "saniye":
                multiplier = 1000
            elif unit == "dakika":
                multiplier = 60000

            if delay_sec > 0:
                self.status_var.set(f"{delay_sec} saniye sonra başlıyor...")
                time.sleep(delay_sec)

            self.is_running = True
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.status_var.set("Çalışıyor...")

            self.click_thread = threading.Thread(
                target=self.clicking_loop,
                args=(get_interval, multiplier, total_clicks)
            )
            self.click_thread.daemon = True
            self.click_thread.start()

        except Exception as e:
            self.status_var.set(str(e))
            self.stop_clicking()

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
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
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
                    if ctk.CTkMessageBox.askyesno("Güncelleme Mevcut",
                        f"Yeni sürüm: {latest_version}\nŞu anki sürüm: {self.current_version}\n\nGüncellemek ister misiniz?"):
                        self.update_application(latest_version)
                else:
                    self.status_var.set(f"En son sürümü kullanıyorsunuz: {self.current_version}")
            else:
                self.status_var.set("Güncelleme kontrolü başarısız oldu.")
        except Exception as e:
            self.status_var.set(f"Güncelleme kontrolü başarısız: {str(e)}")

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
                ctk.CTkMessageBox.showinfo("Güncelleme Tamamlandı",
                    f"Uygulama sürüm {new_version} olarak güncellendi.\nDeğişikliklerin etkili olması için uygulamayı yeniden başlatın.")
                self.after(1000, self.destroy)
            else:
                raise Exception(f"İndirme başarısız oldu: {response.status_code}")
        except Exception as e:
            ctk.CTkMessageBox.showerror("Güncelleme Hatası", str(e))
            self.status_var.set("Güncelleme başarısız oldu")

    def open_help(self):
        webbrowser.open("https://github.com/ATOMGAMERAGA/autoc")

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)
        if self.fullscreen:
            self.fullscreen_button.configure(text="Normal Ekran")
        else:
            self.fullscreen_button.configure(text="Tam Ekran")

if __name__ == "__main__":
    pyautogui.alert(
        "Bu uygulama, ekranınızda otomatik tıklamalar yapmak için izin gerektirir.\nDevam etmek için 'OK' tuşuna basın.",
        "Ekran Erişim İzni"
    )
    app = AutoClickerApp()
    app.mainloop()