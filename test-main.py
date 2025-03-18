import tkinter as tk
from tkinter import ttk, messagebox, font
import pyautogui
import threading
import keyboard
import time
import random
import requests
import os
import sys

def setup_style(root):
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', background='#f3f3f3', foreground='#333333', font=('Segoe UI', 10))
    style.configure('TButton', padding=6, relief='flat', background='#0078D7', foreground='white')
    style.map('TButton', background=[('active', '#005A9E')])
    style.configure('TLabel', background='#f3f3f3')
    style.configure('TFrame', background='#f3f3f3')
    style.configure('TLabelframe', background='#f3f3f3', foreground='#0078D7')
    style.configure('TLabelframe.Label', font=('Segoe UI', 10, 'bold'))
    style.configure('TEntry', padding=4)
    style.configure('TCombobox', padding=4)
    return style

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker")
        self.root.geometry("450x600")
        self.root.resizable(False, False)
        self.current_version = "0.3"
        self.is_running = False
        self.click_thread = None
        self.hotkey = "f8"  # Varsayılan kısayol
        
        # Stil ayarlarını uyguluyoruz
        setup_style(root)
        self.available_themes = ['clam', 'alt', 'default', 'classic']
        self.create_widgets()
        
        # Global kısayol ataması
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
        self.check_for_updates()
    
    def create_widgets(self):
        # Tıklama Seçenekleri
        options_frame = ttk.LabelFrame(self.root, text="Tıklama Seçenekleri")
        options_frame.pack(padx=15, pady=10, fill="x")
        
        ttk.Label(options_frame, text="Tıklama Türü:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.click_type = tk.StringVar(value="left")
        ttk.Radiobutton(options_frame, text="Sol Tık", variable=self.click_type, value="left").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(options_frame, text="Sağ Tık", variable=self.click_type, value="right").grid(row=0, column=2, padx=5)
        ttk.Radiobutton(options_frame, text="Çift Tık", variable=self.click_type, value="double").grid(row=0, column=3, padx=5)
        
        # Tıklama Aralığı
        ttk.Label(options_frame, text="Tıklama Aralığı:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.interval_value = tk.StringVar(value="100")
        ttk.Entry(options_frame, textvariable=self.interval_value, width=10).grid(row=1, column=1, padx=5)
        self.interval_type = tk.StringVar(value="ms")
        interval_types = ttk.Combobox(options_frame, textvariable=self.interval_type, width=10, state="readonly")
        interval_types['values'] = ('ms', 'saniye', 'dakika')
        interval_types.grid(row=1, column=2, padx=5)
        
        # Rastgele Aralık Seçeneği
        self.random_interval = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Rastgele Aralık", variable=self.random_interval,
                        command=self.toggle_random_interval).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.min_interval = tk.StringVar(value="80")
        self.max_interval = tk.StringVar(value="150")
        self.min_entry = ttk.Entry(options_frame, textvariable=self.min_interval, width=8, state="disabled")
        self.max_entry = ttk.Entry(options_frame, textvariable=self.max_interval, width=8, state="disabled")
        ttk.Label(options_frame, text="Min:").grid(row=2, column=1, padx=5)
        self.min_entry.grid(row=2, column=2, padx=5)
        ttk.Label(options_frame, text="Max:").grid(row=2, column=3, padx=5)
        self.max_entry.grid(row=2, column=4, padx=5)
        
        # Ek Özellikler: Gecikme ve Tıklama Sayısı
        extra_frame = ttk.LabelFrame(self.root, text="Ek Özellikler")
        extra_frame.pack(padx=15, pady=10, fill="x")
        ttk.Label(extra_frame, text="Başlangıç Gecikmesi (s):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.delay = tk.StringVar(value="0")
        ttk.Entry(extra_frame, textvariable=self.delay, width=8).grid(row=0, column=1, padx=5)
        ttk.Label(extra_frame, text="Tıklama Sayısı (0 = sınırsız):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.click_count = tk.StringVar(value="0")
        ttk.Entry(extra_frame, textvariable=self.click_count, width=8).grid(row=1, column=1, padx=5)
        
        # Tıklama Konumu Seçenekleri
        pos_frame = ttk.LabelFrame(self.root, text="Tıklama Konumu")
        pos_frame.pack(padx=15, pady=10, fill="x")
        self.pos_mode = tk.StringVar(value="current")
        ttk.Radiobutton(pos_frame, text="Mevcut Fare Pozisyonu", variable=self.pos_mode, value="current").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(pos_frame, text="Özel Koordinat", variable=self.pos_mode, value="custom").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(pos_frame, text="X:").grid(row=1, column=0, padx=5)
        self.custom_x = tk.StringVar(value="0")
        self.x_entry = ttk.Entry(pos_frame, textvariable=self.custom_x, width=8, state="disabled")
        self.x_entry.grid(row=1, column=1, padx=5)
        ttk.Label(pos_frame, text="Y:").grid(row=1, column=2, padx=5)
        self.custom_y = tk.StringVar(value="0")
        self.y_entry = ttk.Entry(pos_frame, textvariable=self.custom_y, width=8, state="disabled")
        self.y_entry.grid(row=1, column=3, padx=5)
        self.pos_mode.trace("w", self.toggle_custom_position)
        
        # Tema Seçimi
        theme_frame = ttk.LabelFrame(self.root, text="Tema Seçimi")
        theme_frame.pack(padx=15, pady=10, fill="x")
        ttk.Label(theme_frame, text="Tema:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.theme_var = tk.StringVar(value=self.available_themes[0])
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=self.available_themes, state="readonly")
        theme_combo.grid(row=0, column=1, padx=5)
        ttk.Button(theme_frame, text="Uygula", command=self.change_theme).grid(row=0, column=2, padx=5)
        
        # Kısayol Ayarları
        hotkey_frame = ttk.LabelFrame(self.root, text="Kısayol Tuşu")
        hotkey_frame.pack(padx=15, pady=10, fill="x")
        ttk.Label(hotkey_frame, text="Başlat/Durdur Tuşu:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.hotkey_var = tk.StringVar(value=self.hotkey)
        self.hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey_var, width=8)
        self.hotkey_entry.grid(row=0, column=1, padx=5)
        ttk.Button(hotkey_frame, text="Ata", command=self.set_hotkey).grid(row=0, column=2, padx=5)
        
        # Kontrol Butonları
        control_frame = ttk.Frame(self.root)
        control_frame.pack(padx=15, pady=15, fill="x")
        self.start_button = ttk.Button(control_frame, text=f"Başlat ({self.hotkey.upper()})", command=self.start_clicking)
        self.start_button.pack(side="left", expand=True, fill="x", padx=5)
        self.stop_button = ttk.Button(control_frame, text="Durdur", command=self.stop_clicking, state="disabled")
        self.stop_button.pack(side="right", expand=True, fill="x", padx=5)
        
        # Durum Çubuğu ve Güncelleme
        self.status_var = tk.StringVar(value="Hazır")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x", padx=15, pady=5)
        update_frame = ttk.LabelFrame(self.root, text="Güncelleme")
        update_frame.pack(padx=15, pady=10, fill="x")
        ttk.Label(update_frame, text=f"Mevcut Sürüm: {self.current_version}").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Button(update_frame, text="Güncelleme Kontrol Et", command=self.check_for_updates).grid(row=0, column=1, padx=5, pady=5)
    
    def toggle_random_interval(self):
        state = "normal" if self.random_interval.get() else "disabled"
        self.min_entry.config(state=state)
        self.max_entry.config(state=state)
    
    def toggle_custom_position(self, *args):
        state = "normal" if self.pos_mode.get() == "custom" else "disabled"
        self.x_entry.config(state=state)
        self.y_entry.config(state=state)
    
    def change_theme(self):
        try:
            new_theme = self.theme_var.get()
            style = ttk.Style(self.root)
            style.theme_use(new_theme)
            self.status_var.set(f"Tema {new_theme} olarak uygulandı")
        except Exception as e:
            messagebox.showerror("Hata", f"Tema değiştirilemedi: {str(e)}")
    
    def set_hotkey(self):
        old_hotkey = self.hotkey
        new_hotkey = self.hotkey_var.get().lower()
        try:
            keyboard.remove_hotkey(old_hotkey)
            keyboard.add_hotkey(new_hotkey, self.toggle_clicking)
            self.hotkey = new_hotkey
            self.start_button.config(text=f"Başlat ({new_hotkey.upper()})")
            self.status_var.set(f"Kısayol tuşu {new_hotkey.upper()} olarak ayarlandı")
        except Exception as e:
            messagebox.showerror("Hata", f"Kısayol tuşu ayarlanamadı: {str(e)}")
            self.hotkey_var.set(old_hotkey)
    
    def toggle_clicking(self):
        if self.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()
    
    def start_clicking(self):
        if self.is_running:
            return
        try:
            # Başlangıç gecikmesi
            try:
                delay_sec = float(self.delay.get())
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir gecikme süresi giriniz")
                return
            # Tıklama sayısı kontrolü
            try:
                total_clicks = int(self.click_count.get())
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir tıklama sayısı giriniz")
                return
            
            # Sabit ya da rastgele aralık belirleme
            if self.random_interval.get():
                try:
                    min_val = float(self.min_interval.get())
                    max_val = float(self.max_interval.get())
                    if min_val > max_val:
                        raise ValueError("Min aralık, max aralıktan büyük olamaz")
                except ValueError as ve:
                    messagebox.showerror("Hata", f"Rastgele aralık değeri hatası: {ve}")
                    return
                # Rastgele aralığı kullanmak için lambda
                get_interval = lambda: random.uniform(min_val, max_val)
            else:
                try:
                    interval = float(self.interval_value.get())
                except ValueError:
                    messagebox.showerror("Hata", "Geçerli bir aralık değeri giriniz")
                    return
                get_interval = lambda: interval
            
            # Aralık tipini milisaniyeye çevirme
            unit = self.interval_type.get()
            multiplier = 1
            if unit == "saniye":
                multiplier = 1000
            elif unit == "dakika":
                multiplier = 60000
            
            # Başlangıç gecikmesi uygulama
            if delay_sec > 0:
                self.status_var.set(f"{delay_sec} saniye sonra başlıyor...")
                time.sleep(delay_sec)
            
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_var.set("Çalışıyor...")
            
            self.click_thread = threading.Thread(target=self.clicking_loop, args=(get_interval, multiplier, total_clicks))
            self.click_thread.daemon = True
            self.click_thread.start()
        except Exception as e:
            messagebox.showerror("Hata", str(e))
            self.stop_clicking()
    
    def clicking_loop(self, get_interval, multiplier, total_clicks):
        clicks_done = 0
        try:
            while self.is_running:
                # Tıklama konumunu belirleme
                if self.pos_mode.get() == "custom":
                    try:
                        x = int(self.custom_x.get())
                        y = int(self.custom_y.get())
                    except ValueError:
                        self.status_var.set("Özel koordinatlar geçersiz, mevcut pozisyon kullanılıyor")
                        x, y = pyautogui.position()
                else:
                    x, y = pyautogui.position()
                
                # Tıklama türüne göre işlem
                if self.click_type.get() == "left":
                    pyautogui.click(x=x, y=y)
                elif self.click_type.get() == "right":
                    pyautogui.rightClick(x=x, y=y)
                elif self.click_type.get() == "double":
                    pyautogui.doubleClick(x=x, y=y)
                
                clicks_done += 1
                if total_clicks and clicks_done >= total_clicks:
                    break
                
                interval = get_interval() * multiplier / 1000  # saniyeye çevir
                if interval < 0.01:
                    interval = 0.01
                time.sleep(interval)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Hata", str(e)))
        finally:
            self.root.after(0, self.stop_clicking)
    
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
                                           f"Yeni sürüm mevcut: {latest_version}\nŞu anki sürüm: {self.current_version}\n\nGüncellemek ister misiniz?"):
                        self.update_application(latest_version)
                else:
                    self.status_var.set(f"En son sürümü kullanıyorsunuz: {self.current_version}")
            else:
                self.status_var.set("Güncelleme kontrolü başarısız oldu")
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
                messagebox.showinfo("Güncelleme Tamamlandı", 
                                    f"Uygulama sürüm {new_version}'e güncellendi.\nDeğişikliklerin etkili olması için uygulamayı yeniden başlatın.")
                self.root.after(1000, self.root.destroy)
            else:
                raise Exception(f"İndirme başarısız oldu: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Güncelleme Hatası", str(e))
            self.status_var.set("Güncelleme başarısız oldu")

if __name__ == "__main__":
    pyautogui.alert(
        "Bu uygulama ekranınızda otomatik tıklamalar yapmak için izin gerektirir.\nDevam etmek için 'OK' düğmesine tıklayın.",
        "Ekran Erişim İzni"
    )
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
