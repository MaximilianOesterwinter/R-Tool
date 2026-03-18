# Danke, dass du mein kleines R-Tool nutzt!!

# So funktioniert es:
#
# 1.) Installiere R
#
# 2.)  Öffne ein neues R-Script und führe folgende Befehle aus:
#     - install.packages("readr")
#     - install.packages("dplyr")
#     - install.packages("rmarkdown")
#     - install.packages("knitr")
#     - install.packages("psych")
#     - install.packages("tinytex")
#     - tinytex::install_tinytex()
#
# 3.) Öffne die Konsole (PowerShell oder CMD) und gib folgenden Code ein:
#     - Rscript --version
#     Wenn alles funktioniert, gibt dir die Konsole die installierte Version von Rscript an.
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
# Gib "python" oder "py" ein. Das sagt dem Computer,
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
# python main.py DEINE_ANALYSEMETHODE VARIABLE_1 VARIABLE_2
#
# Ein Beispiel aus dem mitgelieferten Beispieldatensatz wäre:
#
# python main.py chi_square gender vote_intent
#
#
##########################
# Unterstützte Analysen: #
##########################
#
# Überblick über den Dataframe verschaffen: df
#                                           Benötigt keine Variablen
#
# Deskriptive Analyse: describe
#                      Benötigt 1 Variable
#
# Chi-Quadrat: chi_square
#              Benötigt 2 Variablen!
# 
# Logistische Regressionsanalyse: logit
#                                 Benötigt 1 UV, mind. 1 AV!
#
# Lineare Regressionsanalye: lin_reg
#                            Benötigt 1 UV, mind. 1 AV!
#
