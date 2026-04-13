# Konfigurator sensorow do silownika

Aplikacja desktopowa w Pythonie i Tkinterze do szybkiego doboru sensorow oraz mocowan na podstawie typu rowka lub typu silownika.

## Co potrafi aplikacja

- wybor typu rowka lub typu silownika z listy po lewej stronie,
- wyswietlanie zdjecia wybranego rowka lub typu silownika,
- wyswietlanie listy pasujacych sensorow i mocowan,
- otwieranie linku produktu w przegladarce,
- pokazywanie notatki technicznej dla wybranego elementu,
- pokazywanie zdjecia konkretnego sensora lub mocowania,
- przewijanie listy sensorow kolkiem myszy,
- przewijanie panelu notatki kolkiem myszy oraz paskiem przewijania,
- reczna zmiana wysokosci sekcji `Dostepne sensory` i `Notatka do wybranego sensora`,
- automatyczne skalowanie zdjec, zeby nie zajmowaly calego okna.

## Wymagania

Do uruchomienia projektu potrzebne sa:

- Windows
- Python 3.11 lub nowszy
- `tkinter`
- opcjonalnie `Pillow`

## Biblioteki

### Wymagane

`tkinter`

To biblioteka GUI dostepna standardowo w typowej instalacji Pythona na Windows.

### Opcjonalne, ale zalecane

`Pillow`

Biblioteka jest przydatna do:

- lepszego skalowania obrazow,
- wygodnej obslugi plikow `.jpg` i `.jpeg`.

Bez `Pillow` aplikacja nadal moze dzialac, ale dla czesci obrazow JPG korzysta z tymczasowej konwersji przez mechanizmy Windows.

## Instalacja

### 1. Sprawdzenie instalacji Pythona

W PowerShell:

```powershell
python --version
```

albo:

```powershell
py --version
```

Jesli komenda nie dziala, zainstaluj Pythona z:

[python.org/downloads](https://www.python.org/downloads/)

Podczas instalacji najlepiej zaznaczyc dodanie Pythona do `PATH`.

### 2. Instalacja Pillow

W PowerShell:

```powershell
pip install pillow
```

albo:

```powershell
python -m pip install pillow
```

albo:

```powershell
py -m pip install pillow
```

## Uruchomienie

W katalogu projektu:

```powershell
python .\konfigurator_sensorow_silownika.py
```

albo:

```powershell
py .\konfigurator_sensorow_silownika.py
```

## Jak dziala interfejs

1. Po lewej stronie wybierasz typ rowka lub typ silownika.
2. U gory po prawej wyswietla sie obraz przypisanego rowka lub grupy produktowej.
3. W sekcji `Dostepne sensory` pojawiaja sie dopasowane sensory i mocowania.
4. Po kliknieciu `Szczegoly` lub zaznaczeniu checkboxa aktualizuje sie panel notatki.
5. W notatce widac opis, link i zdjecie konkretnego elementu.
6. Przyciskiem `Otworz link` mozna przejsc do strony produktu.

## Sekcje przewijane i zmiana wielkosci

- `Dostepne sensory` ma wlasny obszar przewijany.
- `Notatka do wybranego sensora` ma osobny scrollbar i obsluge scrolla myszy.
- Wysokosc sekcji `Dostepne sensory` i `Notatka do wybranego sensora` mozna zmieniac przeciagnieciem separatora miedzy nimi.

## Skalowanie obrazow

Aplikacja nie wyswietla obrazow w ich pelnym, oryginalnym rozmiarze.

Aktualnie obrazy sa ograniczane do maksymalnych rozmiarow:

- podglad rowka: `520x260`
- zdjecie elementu w notatce: `260x180`

To ustawienie znajduje sie w pliku:

[konfigurator_sensorow_silownika.py](C:\Users\Fakro\Desktop\Dobór sensorów\ConfigSensor\konfigurator_sensorow_silownika.py)

w stalych:

- `GROOVE_IMAGE_MAX_SIZE`
- `NOTE_IMAGE_MAX_SIZE`

## Jak dodawac zdjecia

Wszystkie obrazy nalezy umieszczac w folderze:

[images](C:\Users\Fakro\Desktop\Dobór sensorów\ConfigSensor\images)

### Zdjecia rowkow i typow silownikow

Sa przypisywane recznie w slowniku `GROOVE_IMAGES`.

### Zdjecia sensorow i mocowan

Aplikacja najpierw probuje znalezc plik automatycznie po nazwie modelu.

Przyklady:

- `BMF00AR` -> `images/BMF00AR.png`
- `BAM01K9 - mocowanie` -> najpierw pelna nazwa, a potem sam kod `BAM01K9.png`

Obslugiwane rozszerzenia:

- `.png`
- `.jpg`
- `.jpeg`
- `.gif`

Jesli automatyczne wyszukiwanie nie znajdzie pliku, aplikacja korzysta z recznego mapowania w slowniku `SENSOR_NOTE_IMAGES`.

## Struktura danych

Kazdy element w bazie `SENSOR_DB` moze zawierac miedzy innymi:

- `name`
- `link`
- `note`

To pozwala przypisac do kazdego sensora lub mocowania:

- nazwe widoczna w liscie,
- link do strony produktu,
- notatke ze szczegolami technicznymi.

## Uwagi

- Aplikacja jest przygotowana glownie pod Windows.
- Linki sa otwierane w domyslnej przegladarce systemowej.
- Dla najlepszej obslugi obrazow warto miec zainstalowane `Pillow`.
