import tkinter as tk
from tkinter import ttk, messagebox
from pynput.mouse import Button, Controller
import threading
import keyboard
import time
import requests
import os
import sys
import sv_ttk  # Sun Valley temasını uygulamak için

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoC (Auto Clicker)")
        self.root.geometry("600x650")
        self.root.resizable(False, False)
        
        # Sun Valley temasını uygula (dark/light)
        sv_ttk.set_theme("dark")
        
        # pynput kullanarak mouse controller'ı oluştur
        self.mouse = Controller()
        
        # Değişkenler
        self.is_running = False
        self.click_thread = None
        self.current_version = "0.5"
        self.hotkey = "f8"  # Varsayılan kısayol
        
        # Arayüz öğelerini oluştur
        self.create_widgets()
        
        # Global kısayol tuşunu ayarla
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
        
        # Başlangıçta güncellemeleri kontrol et
        self.check_for_updates()
    
    def create_widgets(self):
        # Tıklama seçenekleri bölümü
        options_frame = ttk.LabelFrame(self.root, text="Tıklama Seçenekleri")
        options_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(options_frame, text="Tıklama Türü:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.click_type = tk.StringVar(value="left")
        ttk.Radiobutton(options_frame, text="Sol Tık", variable=self.click_type, value="left").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(options_frame, text="Sağ Tık", variable=self.click_type, value="right").grid(row=0, column=2, sticky="w")
        ttk.Radiobutton(options_frame, text="Çift Tık", variable=self.click_type, value="double").grid(row=0, column=3, sticky="w")
        
        # CPS veya aralık modu
        ttk.Label(options_frame, text="CPS veya Aralık:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.cps_mode = tk.BooleanVar(value=True)  # True: CPS modu, False: aralık modu
        ttk.Radiobutton(options_frame, text="CPS", variable=self.cps_mode, value=True).grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(options_frame, text="Aralık", variable=self.cps_mode, value=False).grid(row=1, column=2, sticky="w")
        
        self.rate_value = tk.StringVar(value="5")  # Varsayılan: 5 CPS veya 5 ms
        self.rate_entry = ttk.Entry(options_frame, textvariable=self.rate_value, width=8)
        self.rate_entry.grid(row=1, column=3, sticky="w")
        
        # Aralık tipi (CPS modu değilse)
        ttk.Label(options_frame, text="Aralık Tipi:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.interval_type = tk.StringVar(value="ms")
        self.interval_types_combo = ttk.Combobox(options_frame, textvariable=self.interval_type, width=8, state="readonly")
        self.interval_types_combo['values'] = ('ms', 'saniye', 'dakika')
        self.interval_types_combo.grid(row=2, column=1, sticky="w")
        
        # Mouse konumu ayarı
        pos_frame = ttk.LabelFrame(self.root, text="Mouse Pozisyonu")
        pos_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(pos_frame, text="X:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.pos_x = tk.StringVar()
        ttk.Entry(pos_frame, textvariable=self.pos_x, width=8).grid(row=0, column=1, sticky="w")
        
        ttk.Label(pos_frame, text="Y:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.pos_y = tk.StringVar()
        ttk.Entry(pos_frame, textvariable=self.pos_y, width=8).grid(row=0, column=3, sticky="w")
        
        ttk.Button(pos_frame, text="Mevcut Konumu Al", command=self.get_current_position).grid(row=0, column=4, padx=5)
        
        # Kısayol tuşu ayarı
        hotkey_frame = ttk.LabelFrame(self.root, text="Kısayol Tuşu")
        hotkey_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(hotkey_frame, text="Başlat/Durdur Tuşu:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.hotkey_var = tk.StringVar(value=self.hotkey)
        self.hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey_var, width=8)
        self.hotkey_entry.grid(row=0, column=1, sticky="w")
        
        ttk.Button(hotkey_frame, text="Ata", command=self.set_hotkey).grid(row=0, column=2, sticky="w", padx=5)
        
        # Tema değiştirme butonu
        theme_button = ttk.Button(self.root, text="Tema Değiştir", command=sv_ttk.toggle_theme)
        theme_button.pack(padx=10, pady=5, fill="x")
        
        # Kontrol butonları
        control_frame = ttk.Frame(self.root)
        control_frame.pack(padx=10, pady=10, fill="x")
        
        self.start_button = ttk.Button(control_frame, text=f"Başlat ({self.hotkey.upper()})", command=self.start_clicking)
        self.start_button.pack(side="left", fill="x", expand=True, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Durdur", command=self.stop_clicking, state="disabled")
        self.stop_button.pack(side="right", fill="x", expand=True, padx=5)
        
        # Durum çubuğu
        self.status_var = tk.StringVar(value="Hazır")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x", padx=10, pady=5)
        
        # Güncelleme bölümü
        update_frame = ttk.LabelFrame(self.root, text="Güncelleme")
        update_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(update_frame, text=f"Mevcut Sürüm: {self.current_version}").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Button(update_frame, text="Güncelleme Kontrol Et", command=self.check_for_updates).grid(row=0, column=1, padx=5, pady=5)
    
    def get_current_position(self):
        # pynput ile mevcut fare konumunu al
        pos = self.mouse.position
        self.pos_x.set(str(pos[0]))
        self.pos_y.set(str(pos[1]))
        self.status_var.set("Mevcut mouse konumu alındı")
    
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
            # CPS veya aralık hesaplaması
            rate_str = self.rate_value.get()
            try:
                rate = float(rate_str)
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir sayı giriniz")
                return
            
            if self.cps_mode.get():
                # CPS modunda: saniyede rate adet tıklama (1/CPS)
                interval = 1.0 / rate if rate > 0 else 0.1
            else:
                # Aralık modunda: girilen değeri uygun zaman birimine çevir
                interval = rate
                interval_type = self.interval_type.get()
                if interval_type == "saniye":
                    interval = rate
                elif interval_type == "dakika":
                    interval = rate * 60
                elif interval_type == "ms":
                    interval = rate / 1000
                if interval < 0.01:
                    interval = 0.01
                    self.status_var.set("Uyarı: Minimum aralık 10ms olarak ayarlandı")
            
            # Koordinat ayarı: boşsa mevcut fare konumu kullanılır
            try:
                x = int(self.pos_x.get()) if self.pos_x.get() != "" else None
                y = int(self.pos_y.get()) if self.pos_y.get() != "" else None
            except ValueError:
                messagebox.showerror("Hata", "Geçerli koordinat değerleri giriniz")
                return
            
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_var.set("Çalışıyor...")
            
            # Tıklamaları ayrı bir iş parçacığında başlat
            self.click_thread = threading.Thread(target=self.clicking_loop, args=(interval, self.click_type.get(), x, y))
            self.click_thread.daemon = True
            self.click_thread.start()
            
        except Exception as e:
            messagebox.showerror("Hata", str(e))
            self.stop_clicking()
    
    def clicking_loop(self, interval, click_type, x, y):
        next_click_time = time.perf_counter()  # İlk tıklama zamanı
        try:
            while self.is_running:
                current_time = time.perf_counter()
                if current_time >= next_click_time:
                    # Eğer koordinatlar girildiyse, fare konumunu ayarla
                    if x is not None and y is not None:
                        self.mouse.position = (x, y)
                    
                    # Tıklama işlemi: CPS mantığına göre
                    if click_type == "left":
                        self.mouse.click(Button.left)
                    elif click_type == "right":
                        self.mouse.click(Button.right)
                    elif click_type == "double":
                        self.mouse.click(Button.left)
                        time.sleep(0.05)
                        self.mouse.click(Button.left)
                    
                    next_click_time += interval
                else:
                    time.sleep(max(0, next_click_time - current_time))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Hata", str(e)))
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
            script_url = "https://raw.githubusercontent.com/ATOMGAMERAGA/autoc/main/main.py"
            response = requests.get(script_url, timeout=10)
            
            if response.status_code == 200:
                if getattr(sys, 'frozen', False):
                    application_path = os.path.dirname(sys.executable)
                    script_path = os.path.join(application_path, "main.py")
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
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
