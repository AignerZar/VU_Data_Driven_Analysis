Meine Überlegungen:

Einen Code Get_DATA mit dem wir auf die Daten zugreifen. Der Code muss dabei mehrere Aufgaben übernehmen:

Zum einen alle Landslides rausfiltern und Zeitpunkt und Koordinaten erfassen, dann Hangneigung, 3-Tagessumme Niederschlag und vielleicht auch 1-Tagessumme Niederschlag dem Event zuordnen. Zusätzlich zu den positiven Events auch die 5 Niederschlagsstärksten (3-Tagessumme) negativen Events ohne Landslide an denselben Koordinaten vor dem Landslide erfassen. Alle Daten sollten in eine Tabelle eingefügt werden mit Zeitstempel (Zeitpunkt des Landslides, bzw. Zeitpunkt des negativen Events, also dem Ende der 3-tägigen Niederschlagsperiode) und den 5 zusätzlichen Spalten (Koordinate, Hangneigung, 3-Tagessumme, 1-Tagessumme, Ereignisklassifizierung (1:Landslide, 0:kein Landslide)).

Diese Tabelle wird dann zum Modelltraining im main_code verwendet.

Um das zu bewerkstelligen braucht es folgende Funktionen:
1. Einlesen des Landslide Katalogs für Ereignisse in den Alpen
2. Ausgabe der Hangneigung einer Koordinate
3. Ausgabe der 3-Tages- und 1-Tagessumme Niederschlag einer Koordinate
4. Ausgabe der 5-stärksten 3-Tagessumme Niederschlagsevents für eine Koordinate und vor einem Zeitpunkt. (return: 3-Tagessumme, Zeitpunkt, 1-Tagessumme)
5. Erstellen einer Tabelle mit den ganzen Daten
(6. Split der Tabelle in Trainings und Testdaten mit vorgegebenen Split)


Wenn das alles klappt, dann folgt die Implementierung des Modells im main_code. Da hab ich mir aber bisher noch keine Gedanken gemacht.

Nasa Landslide Katalog:
https://data.nasa.gov/dataset/global-landslide-catalog-export/resource/7dc0d8c1-05f6-4c5c-8fee-20834e4d5d31

Topographiemodell:
https://portal.opentopography.org/raster?opentopoID=OTSDEM.032021.4326.3

ERA-5 Land Daten:
https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=overview


Mein Papa hat gemeint ein zusätzlicher interessanter Parameter wäre noch die Bodenfeuchte, die könnte auch in den ERA-5 Daten drinnen sein, können wir uns ja überlegen ob wir die auch noch integrieren wollen.

Bin offen für andere Ansätze oder Verbesserungen:)