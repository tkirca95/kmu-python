# Python Programlama · Ders Materyalleri

KMÜ Veri Bilimi ve Analitiği · 2. sınıf · 2026-2027 Güz

Bu sayfadaki komutları elle yazmayın: her kod kutusunun sağ üst köşesindeki **kopyala** düğmesine basıp terminale yapıştırın.

## 1. VS Code'u hazırlayın

VS Code'da sol çubuktaki **Extensions** simgesine tıklayın ve **Python** ile **Jupyter** eklentilerini kurun (ikisinin de yayıncısı Microsoft).

## 2. Proje klasörünü açın

1. Yolunda boşluk ve Türkçe karakter olmayan yeni bir klasör oluşturun, örneğin `C:\ders\ga-live`.
2. VS Code'da **File → Open Folder** ile bu klasörü açın; "Do you trust the authors?" sorusuna **Yes** deyin.
3. Üst menüden **Terminal → New Terminal** açın. Bundan sonraki bütün komutlar bu terminale yazılacak.

## 3. uv'yi kurun

uv, Python'ı ve kütüphaneleri kuran, her projeye ayrı bir ortam hazırlayan araçtır. Bilgisayarda kuruluysa (`uv --version` bir sürüm yazıyorsa) bu adımı atlayın.

**Windows:**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Kurulumdan sonra aynı terminalde şunu çalıştırın (ya da VS Code'u kapatıp yeniden açın):

```powershell
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
```

**macOS / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Kurulumdan sonra terminali kapatıp yeniden açın. Kontrol:

```
uv --version
```

## 4. Projeyi oluşturun

```
uv init --python 3.12
uv add matplotlib pandas
uv add --dev ipykernel
```

- `uv init` projeyi başlatır: `pyproject.toml` ve birkaç başlangıç dosyası oluşturur.
- `uv add` kütüphaneleri projenin kendi ortamına (`.venv` klasörü) kurar ve sürümleri `uv.lock` dosyasına yazar.
- `ipykernel`, VS Code'un kodu hücre hücre çalıştırabilmesi için gerekir.

Bilgisayarda Python yoksa uv onu da indirir; ilk sefer birkaç dakika sürebilir.

## 5. Veriyi indirin

**Windows:**

```powershell
mkdir data
Invoke-WebRequest https://raw.githubusercontent.com/tkirca95/kmu-python/main/data/berlin52.tsp -OutFile data/berlin52.tsp
Invoke-WebRequest https://raw.githubusercontent.com/tkirca95/kmu-python/main/data/berlin52.opt.tour -OutFile data/berlin52.opt.tour
```

**macOS / Linux:**

```bash
mkdir data
curl -L -o data/berlin52.tsp https://raw.githubusercontent.com/tkirca95/kmu-python/main/data/berlin52.tsp
curl -L -o data/berlin52.opt.tour https://raw.githubusercontent.com/tkirca95/kmu-python/main/data/berlin52.opt.tour
```

Soldaki dosya gezgininde `data` klasörünün içinde iki dosya görünmeli.

## 6. İlk hücreyi çalıştırın

`live.py` adında yeni bir dosya oluşturup şunu yazın:

```python
# %%
import sys, matplotlib, pandas
print("Hazır! Python", sys.version.split()[0], "| matplotlib", matplotlib.__version__, "| pandas", pandas.__version__)
```

`# %%` satırının üstünde beliren **Run Cell**'e tıklayın; çekirdek (kernel) sorulursa içinde `.venv` geçeni seçin. Sağda açılan pencerede "Hazır!" yazısını görüyorsanız derse hazırsınız.

Derste kuralımız: **kod ve değişken adları İngilizce, açıklamalar (yorumlar) Türkçe.**

## 7. Dönem projesi verisi: kroA100

Proje klasörünüzün terminalinde:

**Windows:**

```powershell
Invoke-WebRequest https://raw.githubusercontent.com/tkirca95/kmu-python/main/data/kroA100.tsp -OutFile data/kroA100.tsp
Invoke-WebRequest https://raw.githubusercontent.com/tkirca95/kmu-python/main/data/kroA100.opt.tour -OutFile data/kroA100.opt.tour
```

**macOS / Linux:**

```bash
curl -L -o data/kroA100.tsp https://raw.githubusercontent.com/tkirca95/kmu-python/main/data/kroA100.tsp
curl -L -o data/kroA100.opt.tour https://raw.githubusercontent.com/tkirca95/kmu-python/main/data/kroA100.opt.tour
```

kroA100: 100 şehir, kanıtlanmış optimum 21282. Resmî kaynak: [TSPLIB](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/)

## 8. Sunum

[Metasezgisel optimizasyona giriş](sunum/metasezgisel_sunum.html): dosyayı indirip tarayıcıda açın.

## Sık karşılaşılan sorunlar

| Belirti | Çözüm |
|---|---|
| `uv` tanınmıyor | 3. adımdaki PATH satırını çalıştırın ya da VS Code'u kapatıp yeniden açın |
| Kurulum betiği engellendi | `winget install --id=astral-sh.uv -e` |
| Terminalde kırmızı "running scripts is disabled" yazısı | Zararsızdır, görmezden gelin |
| `uv init`: "already initialized" | Klasörde zaten bir proje var; bu adımı atlayın |
| **Run Cell** görünmüyor | Jupyter eklentisini kurun; dosya adı `.py` ile bitmeli, ilk satır `# %%` olmalı |
| Çekirdek listesinde `.venv` yok | `uv add --dev ipykernel` çalıştırıldı mı? Sonra Ctrl+Shift+P → "Developer: Reload Window" |
| "ipykernel kurulmalı" uyarısı | **Install**'a basmayın; `uv add --dev ipykernel` çalıştırın |
| `FileNotFoundError: data/berlin52.tsp` | VS Code'da proje klasörünün kendisini açtığınızdan emin olun; 5. adımı tekrarlayın |
| Klavyede `[ ] { }` yok | Türkçe Q klavyede AltGr+8, AltGr+9, AltGr+7, AltGr+0 |

uv hakkında daha fazlası: [docs.astral.sh/uv](https://docs.astral.sh/uv/)
