# Auto C (Auto Clicker)

## Linux:

Kurmak için relases bölümünden en son versiyonun bütün kodunu yükleyin ve dosyaya çıkarın zip dosyasını , ardından sağ tıklayıp burda terminal aça tıklayın sonra sanal ortam oluşturun ve ondanda "bash" yazıp sonra aktif edin sonra gerekli modülleri ve gerekli yan moülleri yükleyin ve en son herşey bitince sanal ortamdayken "sudo python main.py" yazın.

!UYARI!: Linuxte gerekli modülleri yüklerken başına sudo koyun çünkü ekranınıza tıklaması için root yetkisi gerekiyor koda güvenmiyorsanız inceliyebilirsiniz.

## Windows:

Kurmak için relases bölümünden en son versiyonun bütün kodunu yükleyin ve dosyaya çıkarın zip dosyasını , ardından bilgisayarınıza en son pythonu [buraya tıklayarak](https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe) yükleyin sonra yukardaki dosya konum yerine gidip yukardaki dosya konum yerindeki herşeyi kopyalayıp komut istemcisini yetkili olarak açın ve oraya "cd kopyaladığnız-konum" sonra entera basıp açılan yere gerekli modülleri yükleyin ancak yan mödül olan tkinterı siz "pip install tk" komutuyla indirin ve herşey bitince "python main.py" yazın.

## Komutlar: 

### Sanal Ortamı Oluşturma:
   `python3 -m venv myenv`

### Sanal Ortamı Aktif Etme:
   `source myenv/bin/activate`

### Gerekli Modül:
   `pip install pyautogui keyboard requests sv-ttk`



### Gerekli Yan Modül (Sadece Linux):
 Debian or Ubuntu:
  `sudo apt-get update`
  `sudo apt-get install python3-tk`

 Fedora:
  `sudo dnf install python3-tkinter`

 Arch:
  `sudo pacman -S tk`
