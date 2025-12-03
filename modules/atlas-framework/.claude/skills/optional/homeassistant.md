# Home Assistant Control Skill

Ce skill permet de contrôler rapidement Home Assistant via les outils MCP.

## 🔧 Outils MCP Disponibles

Les outils MCP sont préfixés par `mcp__homeassistant__`. Utilise toujours ces outils au lieu de curl !

### Outils Principaux
- `mcp__homeassistant__get_entity_state` : Lire l'état d'une entité
- `mcp__homeassistant__call_service` : Exécuter un service (turn_on, turn_off, etc.)
- `mcp__homeassistant__search_entities` : Chercher des entités par domaine/nom/état

### Outils Avancés
- `mcp__homeassistant__get_areas` : Liste toutes les zones/pièces
- `mcp__homeassistant__get_automations` : Liste les automations
- `mcp__homeassistant__create_automation` : Créer une automation
- `mcp__homeassistant__get_history` : Historique des entités

## 📍 Entités Importantes

### Températures
- **Salon/Living Room** : `sensor.ecobee_main_current_temperature` (20.4°C)
- **Cuisine** : `sensor.multisensor_kitchen_air_temperature` (22.4°C)
- **2e Étage** : `sensor.multisensor_2nd_floor_air_temperature` (21.8°C)
- **Salle de bain 2e** : `sensor.bathroom_2nd_temperature` (20.35°C)
- **Extérieur** : `sensor.outside_current_temperature` (actuel)

### Thermostat
- **Ecobee Principal** : `climate.ecobee`
- **Température actuelle** : `sensor.ecobee_curently_temperature`
- **Consigne** : `sensor.ecobee_set_temp`
- **Température extérieure** : `sensor.ecobee_outside_temp`

### Lumières Cuisine
- **Îlot** : `light.kitchen_island_led_dimmer`
- **Lavabo** : `light.kitchen_sink_led_dimmer`
- **Hall cuisine** : `light.hall_kitchen_led_dimmer`

### Lumières Salon/Living Room
- **LED Salon** : `light.livingroom_led_dimmer`

### Lumières Chambre (Bedroom)
- **Lampe chambre** : `light.bedroom_lamp_dimmer`
- **LED chambre** : `light.bedroom_led_dimmer`
- **Fenêtre chambre** : `light.bedroom_window_dimer`

### Lumières Escaliers
- **2e étage** : `light.stairs_2e_led_dimmer_3way`

### Lumières Extérieur
- **Avant** : `light.outdoor_front_light_trip_dimmer`
- **Porte avant** : `switch.front_door_light`
- **Arrière** : `light.outdoor_rear_light_dimmer`
- **Soffit** : `light.outside_sofit_led_dimmer`

### Lumières Entrée
- **Entrée** : `light.entrance_led_dimmer`

### Lumières Salle de bain
- **1er étage** : `light.bathroom_1st_led_dimmer`
- **2e étage** : `light.bathroom_2e_led_dimmer`

### Capteurs Environnement
- **Humidité sous-sol** : `sensor.basement_temp_hum_sensors_display_humidity` (35.1%)
- **Température sous-sol** : `sensor.basement_temp_hum_sensors_display_temperature` (22.3°C)

### Énergie/Consommation
- **UPS Power** : `sensor.0x282c02bfffe6cc5e_power` (221.5 W)
- **Machine espresso** : `sensor.0x282c02bfffe6b88c_power`
- **Grinder espresso** : `sensor.0x282c02bfffe6bd98_power`

### Scènes Disponibles
- `scene.cooking` : Configuration cuisine
- `scene.movie` : Mode cinéma
- `scene.outdoor_lights` : Ambiance extérieure
- `scene.ambiance` : Ambiance maison
- `scene.morning_2` : Matin (maison)
- `scene.diner` : Souper
- `scene.outdoor_fireplace` : Foyer extérieur

### Modes Maison
- `input_select.house_mode` : Mode actuel (Away, Night, Morning, Work, Movies, Party, Fire, Diner, Normal, Vacation, Sleeping)

## 🎯 Exemples d'Utilisation Rapide

### Lire une température
```
Utilise mcp__homeassistant__get_entity_state avec entity_id="sensor.ecobee_main_current_temperature"
```

### Éteindre toutes les lumières de la cuisine
```
Utilise mcp__homeassistant__call_service avec:
- domain: "light"
- service: "turn_off"
- entity_id: ["light.kitchen_island_led_dimmer", "light.kitchen_sink_led_dimmer", "light.hall_kitchen_led_dimmer"]
```

### Chercher tous les capteurs de température
```
Utilise mcp__homeassistant__search_entities avec:
- domain: "sensor"
- query: "temperature"
```

### Activer une scène
```
Utilise mcp__homeassistant__call_service avec:
- domain: "scene"
- service: "turn_on"
- entity_id: "scene.movie"
```

### Ajuster le thermostat
```
Utilise mcp__homeassistant__call_service avec:
- domain: "climate"
- service: "set_temperature"
- entity_id: "climate.ecobee"
- service_data: {"temperature": 21}
```

## ⚡ Performance

**IMPORTANT** : Utilise TOUJOURS les outils MCP (`mcp__homeassistant__*`) au lieu de curl/API directe !
- Les outils MCP sont 10x plus rapides
- Connexion persistante
- Pas besoin de parser JSON manuellement

## 🏠 Organisation par Pièce

### Cuisine
- Lumières : kitchen_island, kitchen_sink, hall_kitchen
- Température : multisensor_kitchen_air_temperature

### Salon/Living Room
- Lumière : livingroom_led_dimmer
- Température : ecobee_main_current_temperature

### Chambre
- Lumières : bedroom_lamp, bedroom_led, bedroom_window
- Température : Via ecobee (upstairs)

### Sous-sol
- Température : basement_temp_hum_sensors_display_temperature
- Humidité : basement_temp_hum_sensors_display_humidity

### Extérieur
- Lumières : outdoor_front, front_door, outdoor_rear, outside_sofit
- Température : outside_current_temperature
