### Cel Projektu
Celem badania jest weryfikacja, w jakim stopniu wyniki uzyskane z wytrenowanego modelu **CLAP** odzwierciedlają subiektywne, ludzkie poczucie podobieństwa utworów muzycznych — sprawdzana jest korelacja pomiędzy matematyczną bliskością wektorów z ocenami słuchaczy.

---

### Model i Zbiór Danych
W badaniu zastosowany zostanie model `laion/clap-htsat-unfused` udostępniony w bibliotece `transformers` (Hugging Face). Model generuje wektor cech dla podanego fragmentu audio.

Do przeprowadzenia doświadczenia wykorzystany zostanie zbiór referencyjny **GTZAN** - 1000 utworów audio (po 30 sekund każdy), podzielonych na 10 równych gatunków (po 100 utworów): *blues, classical, country, disco, hiphop, jazz, metal, pop, reggae, rock*.

---

### Metryki
Do porównywania wyników wykorzystane zostaną metryki:

1. **Podobieństwo Cosinusowe (*Cosine Similarity*):** Mierzy kąt pomiędzy dwoma znormalizowanymi wektorami CLAP w przestrzeni wielowymiarowej.
2. **Ocena Podobieństwa:** Uśredniona wartość subiektywnych ocen ankietowanych słuchaczy wyliczana dla każdej z ocenianych par.

---

### Przebieg Doświadczenia i Statystyczna Obróbka

#### Próba Badawcza (Słuchacze)
* **Liczebność próby:** Jak najwięcej (co najmniej 20 słuchaczy).
* **Kryteria doboru:** Osoby wykonujące badanie wyłącznie na słuchawkach, zróżnicowanie pod kątem wykształcenia muzycznego.

#### Dobór Utworów
* X zestawów testowych: w każdym zestawie znajduje się utwór referencyjny oraz kilka utworów porównywanych (ten sam gatunek, bliski gatunkowo, kontrastowy, kotwica, ukryta referencja).
* Próbki przycięte do kilkunastosekundowych fragmentów ze środka utworu.
* Badanie powinno trwać nie więcej niż kilkanaście minut, by zapobiec zmęczeniu i utracie skupienia słuchacza.

#### Scenariusz Badania
1. Zapoznanie z instrukcją i próba treningowa niezaliczana do wyników.
2. Odsłuch właściwy obejmujący zestawy prezentowane w losowej kolejności oraz ich ocena w skali 0–100 pod względem np. melodii, rytmu, nastroju oraz ogólnego odbioru.

#### Obróbka Statystyczna
* Zebranie wyników z ankiet oraz wyznaczenie korelacji pomiędzy wartościami przeskalowanego podobieństwa cosinusowego CLAP a wartościami wyliczonymi z testów odsłuchowych.
* Uwzględnienie odrzucenia odpowiedzi, które sugerują brak uwagi słuchacza (niska ocena podobieństwa dla tego samego utworu oraz wysoka ocena dla kotwicy).