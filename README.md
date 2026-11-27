# Peakbound

Peakbound er et fysikkbasert 2D-kjørespill laget i Python og Pygame som et prosjekt i Informasjonsteknologi 2. Bruk farten over toppene og prøv å slå dine egne rekorder. Fjellene har spilltilpasset terreng inspirert av de virkelige fjellene.

## Start i VS Code

Åpne Peakbound-mappen i VS Code. Velg Python-tolken du har installert Pygame CE i, åpne `main.py` og trykk på kjøreknappen. Fra terminalen kan du starte med `python main.py`.

Hvis Pygame mangler, installer avhengighetene med `python -I -m pip install -r requirements.txt` fra Peakbound-mappen.

| Tast | Handling |
|---|---|
| **D** eller **→** | Gass |
| **A** eller **←** | Brems og rygg |
| **Q / E** eller **↑ / ↓** | Vipp bilen i lufta |
| **Esc** | Pause eller fortsett |
| **R** | Start turen på nytt |
| **Tab og Enter** eller **mus** | Bruk menyene |

## Spillmåter og rekorder

- **Fri kjøring.** Kjør så langt du kan før bilen velter eller tanken går tom. Drivstoffkanner fyller tanken. Mynter gir poeng og kan brukes i garasjen. Poengsummen er lengste avstand fra start i hele meter, pluss fem poeng per opptjent mynt.
- **Fjellpost.** Lever pakker ved hyttene. Harde landinger skader pakken. En hel eller skadet pakke gir ti bonusmynter når den kommer fram. Ved neste hytte får du en ny pakke. Rekorden er flest leveringer, med distanse som avgjør hvis to turer har like mange.
- **Fjell og kjøretøy.** Velg Mount Everest, K2, Kilimanjaro eller den opprinnelige Fjellveien. Bakker fortsetter å genereres etter hvert som du kjører. Ridge er lett og rask. Tinde har mer kraft oppover og høyere drivstofforbruk.

Turen lagres ved game over eller når du avslutter den. Etterpå kan du velge **Slå denne turen**, eller velge et opptak under **Tidligere turer** for samme fjell og modus. Spøkelsesbilen gjentar den lagrede bevegelsen på banen. Oppgraderinger og myntsaldo er felles for de to spillmodusene, og rekorder er delt opp etter fjell og modus.

Menyen viser valgt fjell og kjøretøy før du starter. Under kjøring samler speedometeret fart, turdata, tank og pakkestatus i ett instrument. Når du fyller tanken, vises mengden som ble fylt på ved tankmåleren.

Spillernavn, mynter, motor, tank, dekk og turhistorikk lagres lokalt i `saves/saves.json`. Spillet beholder de fem siste turene og den beste turen per fjell og modus. Lagringen registrerer ferdige turer. En ny runde starter ved fjellets startpunkt.

## Slik henger koden sammen

| Fil | Ansvar |
|---|---|
| `main.py` | Åpner vinduet og kjører spilløkka. |
| `game/game.py`, `game/ui.py`, `game/menu.py` og `game/instruments.py` | Styrer skjermer, innstillinger, meny, instrument og tegnerekkefølge. |
| `game/run.py` | Regler for en tur, med tank, mynter, pakkestatus og game over. |
| `game/vehicle.py` | Tyngdekraft, hjulkontakt, motor og rotasjon med Pygame-vektorer. |
| `game/terrain.py`, `game/scenery.py` og `game/camera.py` | Gjentakbar fjellform, bakgrunn og kamerafølging. |
| `game/replay.py` og `game/progress.py` | Opptak, avspilling og JSON-lagring. |

Spøkelsesløpet lagrer målepunkter med tid, posisjon og vinkel. Når spillet viser spøkelsesbilen, regner det ut en posisjon mellom to målepunkter. Banen genereres likt for hvert forsøk på samme fjell, slik at gamle opptak fortsatt ligger på riktig underlag. Ved lange turer reduseres antall målepunkter for å holde lagringsfilen mindre.

## Grafikk og kilder

- **Original grafikk til Peakbound.** Bilene, hjulene, mynten, drivstoffkannen, pakken og posthytta er tegnet på samme pikselrutenett. Everest, K2 og Kilimanjaro bruker tegnede landskapslag, terrengteksturer og dekor fra spillets Python-kode.
- **Grafikk fra prosjektarkivene.** Fjellveiens teksturer, deler av bakgrunnen samt instrument- og menyikoner er fra de vedlagte Hill Climb Racing-ressurspakkene fra Fingersoft. Kildene står i [grafikkoversikten](docs/asset-manifest.json).

Den visuelle retningen er dokumentert i [grafikkguiden](docs/art-direction.md). Åpne [utviklingsdiagrammene](docs/Peakbound-UML.drawio) i draw.io for klassene, spilltilstandene og flyten for spøkelsesløp.
