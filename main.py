import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import keyboard
import time
import requests
import os
import sys

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("320x350")
        self.root.resizable(False, False)
        
        # Variables
        self.is_running = False
        self.click_thread = None
        self.current_version = "1.0"
        self.hotkey = "f6"  # Default hotkey
        
        # Create UI elements
        self.create_widgets()
        
        # Bind hotkey for global access
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
        
        # Check for updates on startup
        self.check_for_updates()
    
    def create_widgets(self):
        # Frame for click options
        options_frame = ttk.LabelFrame(self.root, text="Tıklama Seçenekleri")
        options_frame.pack(padx=10, pady=10, fill="x")
        
        # Click type
        ttk.Label(options_frame, text="Tıklama Türü:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.click_type = tk.StringVar(value="left")
        ttk.Radiobutton(options_frame, text="Sol Tık", variable=self.click_type, value="left").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(options_frame, text="Sağ Tık", variable=self.click_type, value="right").grid(row=0, column=2, sticky="w")
        
        # Click interval
        ttk.Label(options_frame, text="Tıklama Aralığı:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.interval_value = tk.StringVar(value="100")
        interval_entry = ttk.Entry(options_frame, textvariable=self.interval_value, width=8)
        interval_entry.grid(row=1, column=1, sticky="w")
        
        # Interval type
        self.interval_type = tk.StringVar(value="ms")
        interval_types = ttk.Combobox(options_frame, textvariable=self.interval_type, width=8)
        interval_types['values'] = ('ms', 'saniye', 'dakika')
        interval_types['state'] = 'readonly'
        interval_types.grid(row=1, column=2, sticky="w")
        
        # Hotkey configuration
        hotkey_frame = ttk.LabelFrame(self.root, text="Kısayol Tuşu")
        hotkey_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(hotkey_frame, text="Başlat/Durdur Tuşu:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.hotkey_var = tk.StringVar(value=self.hotkey)
        self.hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey_var, width=8)
        self.hotkey_entry.grid(row=0, column=1, sticky="w")
        
        ttk.Button(hotkey_frame, text="Ata", command=self.set_hotkey).grid(row=0, column=2, sticky="w", padx=5)
        
        # Control buttons
        control_frame = ttk.Frame(self.root)
        control_frame.pack(padx=10, pady=20, fill="x")
        
        self.start_button = ttk.Button(control_frame, text="Başlat (F6)", command=self.start_clicking)
        self.start_button.pack(side="left", fill="x", expand=True, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Durdur", command=self.stop_clicking, state="disabled")
        self.stop_button.pack(side="right", fill="x", expand=True, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Hazır")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x", padx=10, pady=5)
        
        # Update section
        update_frame = ttk.LabelFrame(self.root, text="Güncelleme")
        update_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(update_frame, text=f"Mevcut Sürüm: {self.current_version}").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Button(update_frame, text="Güncelleme Kontrol Et", command=self.check_for_updates).grid(row=0, column=1, padx=5, pady=5)
    
    def set_hotkey(self):
        old_hotkey = self.hotkey
        new_hotkey = self.hotkey_var.get().lower()
        
        try:
            # Remove old hotkey
            keyboard.remove_hotkey(old_hotkey)
            
            # Add new hotkey
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
            # Convert interval to milliseconds
            interval_str = self.interval_value.get()
            interval_type = self.interval_type.get()
            
            try:
                interval = float(interval_str)
                
                if interval_type == "saniye":
                    interval *= 1000
                elif interval_type == "dakika":
                    interval *= 60000
                
                # Minimum interval to prevent system freeze
                if interval < 10:
                    interval = 10
                    self.status_var.set("Uyarı: Minimum aralık 10ms olarak ayarlandı")
                
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir sayı giriniz")
                return
            
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_var.set("Çalışıyor...")
            
            # Start clicking in a separate thread
            self.click_thread = threading.Thread(target=self.clicking_loop, args=(interval / 1000, self.click_type.get()))
            self.click_thread.daemon = True
            self.click_thread.start()
            
        except Exception as e:
            messagebox.showerror("Hata", str(e))
            self.stop_clicking()
    
    def clicking_loop(self, interval, click_type):
        try:
            while self.is_running:
                if click_type == "left":
                    pyautogui.click()
                else:
                    pyautogui.rightClick()
                time.sleep(interval)
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
            
            # Get the latest version from GitHub
            version_url = "https://raw.githubusercontent.com/username/auto-clicker/main/VERSION.txt"
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
            
            # Get the latest script from GitHub
            script_url = "https://raw.githubusercontent.com/ATOMGAMERAGA/autoc/main/main.py"
            response = requests.get(script_url, timeout=10)
            
            if response.status_code == 200:
                # Save the current script path
                if getattr(sys, 'frozen', False):
                    # If running as executable
                    application_path = os.path.dirname(sys.executable)
                    script_path = os.path.join(application_path, "main.py")
                else:
                    # If running as script
                    script_path = os.path.abspath(__file__)
                
                # Create backup
                backup_path = script_path + ".bak"
                try:
                    os.rename(script_path, backup_path)
                except:
                    pass
                
                # Write the new script
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                
                # Update version file
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
    # Request screen access permission
    pyautogui.alert(
        "Bu uygulama ekranınızda otomatik tıklamalar yapmak için izin gerektirir.\n"
        "Devam etmek için 'OK' düğmesine tıklayın.",
        "Ekran Erişim İzni"
    )
    
    # Create and start the application
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
