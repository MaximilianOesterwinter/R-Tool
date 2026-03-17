# Danke, dass du mein kleines R-Tool nutzt!!

# So funktioniert es:
#
# 1.) Öffne ein neues R-Script und führe folgende Befehle aus:
#     - install.packages("readr")
#     - install.packages("dplyr")
#     - install.packages("rmarkdown")
#     - install.packages("knitr")
#     - install.packages("tinytex")
#     - tinytex::install_tinytex()
#
# 2.) Installiere den PDF-Viewer "Zathura"
#
# 3.) Öffne die Datei main.py und füge in der gekennzeichneten Zeile den Dateipfad zu 
#     deinem Datensatz ein.
#
# 4.) Öffne prepare_data.R in R und füge im gekennzeicheten Bereich die gewünschten 
#     Aufbereitungen ein. Beachte, dass jeder neue Befehl mit einer sogenannten "Pipe",
#     also diesem Symbol: %>% an den vorangegangenen Befehl angebunden wird.
#
# 5.) Jetzt ist das Programm startklar!
#     Nach einer Erklärung zur richtigen Bedienung folgt die Liste mit den bisherigen Funktionen.
#
##################################
# So bedienst du R-Tool richtig: #
##################################
#
# Das Programm wird aktuell leider noch über die Konsole gesteuert.
# 
# Öffne die Konsole und navigiere mit dem Befehl "cd RTool" in den richtigen Ordner.
# (Je nachdem, wo du das Programm gespeichert hast, musst du unter Umständen statt
# "RTool" den gesamten Pfad bis in den Projektordner angeben.)
#
# Gib "python3" ein. Das sagt dem Computer,
# welche Sprache das Programm verwendet.
# 
# Schreibe anschließend mit einem Leerzeichen dazwischen "main.py".
#
# Danach, wieder mit einem Leerzeichen dazwischen folgt die Analysemethode, die du anwenden willst.
# Eine Liste mit den derzeit verfügbaren Analysen findest du weiter unten.
#
# Im Anschluss folgen die zu untersuchenden Variablen. Achte auf die genaue Schreibweise und
# Groß-/Kleinschreibung, sonst findet das Programm die Variablen in deinem Datensatz nicht!
#
# Der Befehl sollte jetzt so aussehen:
# 
# python3 main.py DEINE_ANALYSEMETHODE VARIABLE_1 VARIABLE_2
#
# Ein Beispiel aus dem mitgelieferten Beispieldatensatz wäre:
#
# python3 main.py chi_square gender vote_intent
#
#
##########################
# Unterstützte Analysen: #
##########################
#
# Chi-Quadrat: chi_square
#              Benötigt: 2 Variablen!
# 
# Logistische Regressionsanalyse: logit
#                                 Benötigt: 1 UV, mind. 1 AV!
#
# Lineare Regressionsanalye: lin_reg
#                            Benötigt: 1 UV, mind. 1 AV!
#
