# flipperkast_1078971


Een real-time systeem voor de SWDWER61X2 opdracht waarin een flipperkast wordt gesimuleerd met gebruik van MQTT.

## Projectbeschrijving

Deze applicatie simuleert een digitale flipperkast waarin spelers een metalen bal door een veld met bumpers en puntenknallers sturen om zoveel mogelijk punten te scoren. De fysica van de bal volgt het principe "hoek van inval is hoek van uitval". Het systeem maakt gebruik van MQTT voor real-time communicatie tussen de verschillende componenten.

## Architectuur

Het project volgt een object-georiënteerde architectuur met de volgende hoofdcomponenten:

### Spelobjecten
- **Ball**: Beheert de positie, snelheid en botsingen van de bal
- **Flipper**: Reageert op spelerinvoer en berekent de impact op de bal
- **Bumper**: Verhoogt de score bij botsingen en stuurt de bal weg
- **Plunger**: Lanceert de bal in het speelveld

### MQTT-Communicatie
- Verbinding met HiveMQ broker
- Realtime score-updates
- Status-updates van het spel
- Ball-position updates

### Weergave
- Grafische 2D-weergave van het speelveld
- Scorepaneel met huidige score en highscore

## Functionele Specificaties

- Flippers die reageren op toetsenbordinvoer
- Natuurkundige balbeweging met correcte reflectiehoeken
- Bumpers en puntenknallers die scores verhogen
- Scorepaneel dat updates ontvangt via MQTT
- Highscore-tracking

## Besturing

- **A/Z/Left Arrow**: Activeer linker flipper
- **L/M/Right Arrow**: Activeer rechter flipper
- **Spatiebalk**: Indrukken en loslaten om de plunger te bedienen
- **ESC**: Spel afsluiten

## Test-Driven Development

Het project is ontwikkeld volgens TDD-principes, met uitgebreide tests voor:
- Natuurkundige accuraatheid (hoek van inval = hoek van uitval)
- Bumper interacties en score-updates
- MQTT-communicatie
- Game-management

## Installatie

1. Clone de repository
2. Installeer de benodigde packages:
   ```
   pip install -r requirements.txt
   ```
3. Start het spel:
   ```
   python main.py
   ```

## Tests Uitvoeren

```
python run_tests.py
```

## Projectstructuur

```
flipperkast/
├── game/
│   ├── __init__.py
│   ├── ball.py
│   ├── bumper.py
│   ├── flipper.py
│   ├── plunger.py
│   ├── score_panel.py
│   └── game_manager.py
├── mqtt/
│   ├── __init__.py
│   ├── mqtt_client.py
│   └── topics.py
├── tests/
│   ├── __init__.py
│   ├── test_ball.py
│   ├── test_bumper.py
│   ├── test_mqtt_client.py
│   ├── test_game_manager.py
│   └── test_physics.py
├── display.py
├── main.py
├── run_tests.py
├── requirements.txt
└── README.md
```

## Technische Implementatie

Dit project gebruikt:
- **PyMunk** voor natuurkundige simulatie
- **PyGame** voor grafische weergave
- **Paho-MQTT** voor de MQTT-communicatie
- **Unittest** voor TDD-testen

## Uitbreiding

De code is goed opgezet, wat het gemakkelijk maakt om nieuwe functionaliteiten toe te voegen zoals:
- Meerdere niveaus
- Extra speltypen bumpers en obstakels