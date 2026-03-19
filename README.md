# 📊 R-Tool für Datenanalyse

Danke, dass du mein kleines R-Tool nutzt!  
Dieses Tool unterstützt dich bei grundlegenden statistischen Analysen über eine einfache Kommandozeilen-Schnittstelle.

---

## 🚀 Installation

### 1. R installieren
Stelle sicher, dass R auf deinem System installiert ist.

---

### 2. Benötigte Pakete installieren

Öffne ein neues R-Script und führe folgende Befehle aus:

```r
install.packages("readr")
install.packages("dplyr")
install.packages("rmarkdown")
install.packages("knitr")
install.packages("psych")
install.packages("car")
install.packages("tinytex")

tinytex::install_tinytex()
```
### 3. Installation prüfen

Öffne die Konsole (PowerShell oder CMD) und führe aus:

```Bash
Rscript --version
```

Wenn alles korrekt installiert ist, wird dir die Version von `Rscript` angezeigt.

### 4. Daten vorbereiten

Öffne die Datei `prepare_data.R` und füge im gekennzeichneten Bereich deine gewünschte Datenaufbereitung ein.

👉 Wichtig:
Verkette Befehle mit der Pipe:
```R
%>%
```

### 5. Fertig!

Das Tool ist jetzt einsatzbereit 🎉

## 💻 Verwendung

Das Programm befindet sich noch in der Alpha und wird daher aktuell noch über die Konsole gesteuert.

### Grundstruktur des Befehls:

```Bash
python main.py ANALYSE VARIABLE_1 VARIABLE_2
```

### 🧠 Erklärung

| Bestandteil | Bedeutung |
|-------------|-----------|
| `python`/`py`| Startet das Programm |
| `main.py` | Hauptscript |
| `ANALYSE` | Gewünschte Analyse |
| `VARIABLE` | Variablen aus deinem Datensatz |

### 📌 Beispiel

```Bash
python main.py chi_square gender vote_intent
```

## 📈 Unterstützte Analysen

### 🔍 Überblick

| Analyse | Beschreibung | Benötigte Variablen |
|---------|--------------|---------------------|
| `df` | Überblick über den Dataframe | keine |
| `describe` | Deskriptive Statistik | 1 Variable |
| `chi_square` | Chi-Quadrat-Test | 2 Variablen |
| `logit` | Logistische Regression | 1 UV, >= 1 AV |
| `lin_reg` | Lineare Regression | 1 UV, >= 1 AV |
| `anova` | ANOVA (ein- oder zweifaktoriell) | 1 AV, 1-2 UV |

### 📊 Details

`df`
Zeigt eine Übersicht über den gesamten Dataframe.

`describe`
Berechnet grundlegende deskriptive Statistiken.

`chi_square`
Führt einen Chi-Quadrat-Test zwischen zwei Variablen durch.

`logit`
Berechnet eine logistische Regressionsanalyse.

`lin_reg`
Berechnet eine lineare Regressionsanalyse.

`anova`
Führt eine ANOVA mit den benötigten Post-Hoc-Tests durch:
- 1 UV -> einfaktorielle ANOVA
- 2 UV -> zweifaktorielle ANOVA

## ⚠️ Hinweise

- Achte unbedingt auf eine **exakte Schreibweise** der Variablen (inkl. Groß-/Kleinschreibung).
- Das Tool ist aktuell **CLI-basiert** (keine grafische Oberfläche).
- Fehler entstehen häufig durch falsch benannte oder in der Aufbereitung falsch formatierte Variablen.

## 🛠️ Geplante Features

- GUI (grafische Benutzeroberfläche)
- Erweiterte statistische Tests
## 📄 Lizenz

MIT License
