# Genetik algoritma ile gezgin satıcı problemi (berlin52)

# %% Aşama 0: ortam testi
# Kurulum doğru mu? Bu hücre çalışıyorsa Python ve kütüphaneler hazır.
import sys

import matplotlib
import pandas

print("Hazır! Python", sys.version.split()[0], "| matplotlib", matplotlib.__version__, "| pandas", pandas.__version__)
# Beklenen (sürümler farklı olabilir): Hazır! Python 3.12.x | matplotlib 3.11.2 | pandas 3.1.1

# %% Aşama 1: veriyi oku
# Dosya düz metin. Başlık satırlarını atla, NODE_COORD_SECTION'dan sonra
# her satırdan x ve y'yi al, EOF'ta dur.
from pathlib import Path


def read_tsp(path):
    file_path = Path(path)            # 1. dosyanın adresi
    text = file_path.read_text()      # 2. dosyanın tamamı, tek bir uzun metin
    lines = text.splitlines()         # 3. metin, satırlardan oluşan bir listeye bölünür

    coords = []                       # okunan koordinatlar buraya eklenecek
    in_coords = False                 # bayrak: koordinat bölümüne geldik mi?
    for line in lines:                # 4. her satır için bir tur
        line = line.strip()           # baştaki ve sondaki boşlukları at
        if line == "NODE_COORD_SECTION":
            in_coords = True          # bundan sonraki satırlar koordinat
        elif line == "EOF":
            break                     # dosya sonu: döngüden çık
        elif in_coords:
            parts = line.split()      # "1 565.0 575.0" -> ['1', '565.0', '575.0']
            x = float(parts[1])       # parts[0] şehir numarası, kullanmıyoruz
            y = float(parts[2])
            coords.append((x, y))
    return coords


cities = read_tsp("data/berlin52.tsp")
print(len(cities), cities[:3])
# Beklenen: 52 [(565.0, 575.0), (25.0, 185.0), (345.0, 750.0)]

# %% Aşama 2: mesafe matrisi
# TSPLIB'de mesafe tam sayıdır: Öklid mesafesi en yakın tam sayıya yuvarlanır.
import math


def distance(a, b):
    dx = a[0] - b[0]                  # x farkı
    dy = a[1] - b[1]                  # y farkı
    exact = math.sqrt(dx ** 2 + dy ** 2)
    return int(exact + 0.5)           # en yakın tam sayıya yuvarla (TSPLIB kuralı)


n = len(cities)
D = []                                # D[i][j]: i ile j arasındaki mesafe
for i in range(n):
    row = []
    for j in range(n):
        row.append(distance(cities[i], cities[j]))
    D.append(row)

print(D[0][1], D[0][:6])
# Beklenen: 666 [0, 666, 281, 396, 291, 326]

# %% Aşama 3: tur uzunluğu ve doğrulama
# Kodumuz doğru mu? TSPLIB'in optimal turunu ölçelim: tam 7542 çıkmalı.


def tour_length(tour, D):
    total = 0
    for i in range(len(tour) - 1):    # ardışık şehirler arasındaki mesafeler
        city = tour[i]
        next_city = tour[i + 1]
        total = total + D[city][next_city]
    last_city = tour[-1]              # -1: listenin son elemanı
    first_city = tour[0]
    total = total + D[last_city][first_city]   # son şehirden başa dönüş
    return total


def read_tour(path):
    file_path = Path(path)
    text = file_path.read_text()
    lines = text.splitlines()

    tour = []
    in_tour = False                   # bayrak: tur bölümüne geldik mi?
    for line in lines:
        line = line.strip()
        if line == "TOUR_SECTION":
            in_tour = True
        elif in_tour:
            if line == "-1":          # tur -1 ile biter
                break
            city_number = int(line)   # dosyada şehirler 1'den başlar
            tour.append(city_number - 1)   # Python'da 0'dan başlar
    return tour


opt = read_tour("data/berlin52.opt.tour")
print(len(opt), tour_length(opt, D))
# Beklenen: 52 7542

# %% Aşama 4: taban çizgisi ve çizim
# GA'yı neyle kıyaslayacağız? Rastgele tur ve en yakın komşu.
import random

import matplotlib.pyplot as plt


def random_tour(n, rng):
    tour = list(range(n))             # [0, 1, 2, ..., n-1]
    rng.shuffle(tour)                 # listeyi yerinde karıştır
    return tour


def nearest_neighbor(D, start=0):
    n = len(D)
    tour = [start]
    unvisited = []                    # henüz gidilmemiş şehirler
    for city in range(n):
        if city != start:
            unvisited.append(city)

    while len(unvisited) > 0:
        last = tour[-1]               # şu an bulunduğumuz şehir
        nearest = unvisited[0]        # şimdilik ilk adayı en yakın say
        for city in unvisited:
            if D[last][city] < D[last][nearest]:
                nearest = city        # daha yakını bulundu
        tour.append(nearest)
        unvisited.remove(nearest)
    return tour


def plot_tour(tour, coords, title=""):
    xs = []
    ys = []
    for city in tour:
        xs.append(coords[city][0])
        ys.append(coords[city][1])
    xs.append(coords[tour[0]][0])     # başa dönüş çizilsin diye
    ys.append(coords[tour[0]][1])     # ilk şehri sona bir kez daha ekle
    plt.figure(figsize=(6, 4))
    plt.plot(xs, ys, "-o", markersize=3)
    plt.title(title)
    plt.show()


nn = nearest_neighbor(D)
rand = random_tour(n, random.Random(1))
print("rastgele:", tour_length(rand, D))
print("en yakın komşu:", tour_length(nn, D))
plot_tour(nn, cities, f"En yakın komşu: {tour_length(nn, D)}")
# Beklenen: rastgele: 30745 / en yakın komşu: 8980

# %% Aşama 5a: popülasyon
# Birey = bir tur. Popülasyon = rastgele turlar. Uygunluk = uzunluk, küçük olan iyi.
rng = random.Random(1)
population = []
for _ in range(6):                  
    population.append(random_tour(n, rng))

lengths = []
for tour in population:
    lengths.append(tour_length(tour, D))

for i in range(len(population)):
    print(population[i][:8], lengths[i])
# Beklenen ilk satır: [49, 9, 37, 22, 2, 38, 19, 11] 30745

# %% Aşama 5b: turnuva seçimi
# k aday rastgele seçilir, en kısa turlu olan kazanır.


def tournament(population, lengths, k, rng):
    candidates = rng.sample(range(len(population)), k)   # k farklı sıra numarası
    winner = candidates[0]            # şimdilik ilk adayı kazanan say
    for i in candidates:
        if lengths[i] < lengths[winner]:
            winner = i                # daha kısa turlu bir aday bulundu
    return population[winner]


selected = tournament(population, lengths, 3, random.Random(3))
print("seçilenin uzunluğu:", tour_length(selected, D))
# Beklenen: seçilenin uzunluğu: 29213

# %% Aşama 5c: sıralı çaprazlama (OX)
# Önce tahtada elle yapalım (kesim 3-6), sonra kodla aynı sonucu bulalım.


def order_crossover(p1, p2, rng, cuts=None):
    n = len(p1)

    # 1. Kesim noktaları: verilmemişse rastgele iki konum seç
    if cuts is None:
        positions = rng.sample(range(n), 2)
        a = min(positions)
        b = max(positions)
    else:
        a = cuts[0]
        b = cuts[1]

    # 2. Birinci ebeveynin a..b parçasını çocuğa aynı konumlara kopyala
    child = [None] * n                # n tane boş yer
    for i in range(a, b + 1):
        child[i] = p1[i]

    # 3. Okuma sırası: b'den sonrası, ardından baştan b'ye kadar (dairesel)
    reading_order = []
    for i in range(b + 1, n):
        reading_order.append(i)
    for i in range(0, b + 1):
        reading_order.append(i)

    # 4. İkinci ebeveyni bu sırayla oku; çocukta olmayan şehirleri sırayla topla
    remaining = []
    for i in reading_order:
        city = p2[i]
        if city not in child:
            remaining.append(city)

    # 5. Çocuğun boş yerlerini aynı sırayla doldur
    k = 0
    for i in reading_order:
        if child[i] is None:
            child[i] = remaining[k]
            k = k + 1
    return child


child = order_crossover(list(range(10)), [4, 8, 2, 9, 0, 6, 1, 7, 3, 5], None, cuts=(3, 6))
print(child, "geçerli mi:", sorted(child) == list(range(10)))
# Beklenen: [9, 0, 1, 3, 4, 5, 6, 7, 8, 2] geçerli mi: True

# %% Aşama 5d: mutasyon
# Ters çevirme (inversion) bir parçayı tersine çevirir: turda yalnızca iki kenar değişir.


def inversion(tour, rng):
    positions = rng.sample(range(len(tour)), 2)   # rastgele iki farklı konum
    i = min(positions)
    j = max(positions)
    segment = tour[i : j + 1]         # i'den j'ye kadar olan parça (j dahil)
    segment.reverse()                 # parçayı ters çevir
    tour[i : j + 1] = segment         # ters çevrilmiş parçayı aynı yere koy


t = list(range(10))
inversion(t, random.Random(0))
print(t)
# Beklenen: [0, 1, 2, 3, 4, 5, 9, 8, 7, 6]

# %% Aşama 6: ana döngü
# Parçaları birleştiriyoruz: değerlendir, sırala, elitleri koru, seç, çaprazla,
# mutasyona uğrat. Not: İlk yazışta mutation parametresi yoktur, döngüde doğrudan
# inversion(child, rng) çağrılır. Parametre Aşama 8'de eklenir.


def ga(D, pop_size=100, generations=1000, pc=0.9, pm=0.5, k=5, elite=2, seed=1, mutation=inversion):
    rng = random.Random(seed)
    n = len(D)

    # Başlangıç popülasyonu: pop_size tane rastgele tur
    population = []
    for _ in range(pop_size):
        population.append(random_tour(n, rng))

    history = []                      # her neslin en iyi uzunluğu
    for gen in range(generations + 1):
        # 1. Değerlendir: her turun uzunluğu
        lengths = []
        for tour in population:
            lengths.append(tour_length(tour, D))

        # 2. Sırala: (uzunluk, sıra numarası) çiftlerini küçükten büyüğe diz
        pairs = []
        for i in range(pop_size):
            pairs.append((lengths[i], i))
        pairs.sort()
        best_index = pairs[0][1]      # en kısa turun sıra numarası

        # 3. Kaydet
        history.append(lengths[best_index])

        # Son nesilde yalnızca değerlendirip çık
        if gen == generations:
            break

        # 4. Elitizm: en iyi turların kopyaları yeni nesle geçer
        new_population = []
        for e in range(elite):
            elite_index = pairs[e][1]
            new_population.append(population[elite_index][:])

        # 5. Doldur: yeni popülasyon dolana kadar çocuk üret
        while len(new_population) < pop_size:
            p1 = tournament(population, lengths, k, rng)
            p2 = tournament(population, lengths, k, rng)
            if rng.random() < pc:     # pc olasılıkla çaprazla
                child = order_crossover(p1, p2, rng)
            else:                     # değilse birinci ebeveynin kopyası
                child = p1[:]
            if rng.random() < pm:     # pm olasılıkla mutasyon
                mutation(child, rng)
            new_population.append(child)

        # 6. Değiştir: yeni nesil eskisinin yerini alır
        population = new_population

    return population[best_index], lengths[best_index], history


best_tour, best_length, history = ga(D)
gap = 100 * (best_length - 7542) / 7542
print("en iyi:", best_length, f"| sapma: %{gap:.2f}")
# Beklenen: en iyi: 7896 | sapma: %4.69

# %% Aşama 7: grafikler
# İlk yüzlerce nesilde hızlı iyileşme, sonra durma: erken yakınsama.
plt.figure(figsize=(6, 4))
plt.plot(history, label="en iyi")
plt.axhline(7542, linestyle="--", color="gray", label="optimum")
plt.xlabel("nesil")
plt.ylabel("tur uzunluğu")
plt.legend()
plt.show()
plot_tour(best_tour, cities, f"GA: {best_length}")

# %% Aşama 8: mini deney
# Tek koşu bir şey kanıtlamaz. Takas (swap) mutasyonunu yazalım; ga'ya mutasyonu
# parametre olarak verelim (Python'da fonksiyon da bir değerdir) ve 5 tohumla karşılaştıralım.
import pandas as pd


def swap(tour, rng):
    positions = rng.sample(range(len(tour)), 2)
    i = positions[0]
    j = positions[1]
    temp = tour[i]                    # iki şehrin yerini değiştir
    tour[i] = tour[j]
    tour[j] = temp


rows = []
for mutation_name in ["inversion", "swap"]:
    if mutation_name == "inversion":
        mutation_function = inversion
    else:
        mutation_function = swap
    for seed in range(1, 6):
        run_tour, run_length, run_history = ga(D, seed=seed, mutation=mutation_function)
        rows.append({"mutation": mutation_name, "seed": seed, "length": run_length})

df = pd.DataFrame(rows)
df["gap"] = 100 * (df["length"] - 7542) / 7542
summary = df.groupby("mutation")["gap"].agg(["min", "mean", "std"])
print(summary.round(2))
# Beklenen (yaklaşık 20 saniye sürer):
#              min   mean   std
# inversion   4.63   6.41  3.00
# swap       12.93  21.02  6.38


# %% Kapanış: yerel optimumdan kaçmak
# GA yüzde 4,7'de takıldı. Farklı bir hamleyle bu vadiden çıkabilir miyiz? İki fikir:
# 2-opt kesişen kenarları açar; çift köprü turu üç yerden kesip yeniden birleştirir.
def two_opt(tour, D):
    tour = tour[:]                    # kopya: verilen tur bozulmasın
    n = len(tour)
    improved = True
    while improved:                   # bir tam taramada iyileşme olmayana kadar
        improved = False
        for i in range(n - 1):
            if i == 0:
                last_j = n - 2        # i = 0 iken son kenar ilk kenarla bitişik, atla
            else:
                last_j = n - 1
            for j in range(i + 2, last_j + 1):
                a = tour[i]
                b = tour[i + 1]
                c = tour[j]
                if j + 1 == n:
                    d = tour[0]       # son şehirden sonra başa dönülür
                else:
                    d = tour[j + 1]
                old_edges = D[a][b] + D[c][d]
                new_edges = D[a][c] + D[b][d]
                if new_edges < old_edges:
                    segment = tour[i + 1 : j + 1]
                    segment.reverse()
                    tour[i + 1 : j + 1] = segment
                    improved = True
    return tour


def double_bridge(tour, rng):
    cuts = rng.sample(range(1, len(tour)), 3)   # üç kesim noktası
    cuts.sort()
    a = cuts[0]
    b = cuts[1]
    c = cuts[2]
    part_a = tour[:a]
    part_b = tour[a:b]
    part_c = tour[b:c]
    part_d = tour[c:]
    return part_a + part_d + part_c + part_b   # A B C D -> A D C B


rng = random.Random(1)
tour = best_tour[:]
length = best_length
for it in range(1, 301):
    shaken = double_bridge(tour, rng)           # turu sars
    candidate = two_opt(shaken, D)              # sonra iyileştir
    candidate_length = tour_length(candidate, D)
    if candidate_length < length:               # daha kısaysa kabul et
        tour = candidate
        length = candidate_length
        print(f"iterasyon {it}: {length}")
# Beklenen:
# iterasyon 2: 7888
# iterasyon 5: 7857
# iterasyon 17: 7810
# iterasyon 34: 7618
# iterasyon 87: 7542
plot_tour(tour, cities, f"GA + çift köprü + 2-opt: {length}")
