# AmbiantLedStrip

Système d'éclairage d'ambiance dynamique (type *Ambilight*) pour écran de PC, synchronisé en temps réel avec un ruban LED connecté au réseau local (ESP8266, ESP32, Arduino WiFi, Raspberry Pi, etc.).

---

## Sommaire

- [À quoi sert ce projet ?](#-à-quoi-sert-ce-projet-)
- [Fonctionnement technique](#-fonctionnement-technique)
  - [Protocole réseau (Trame TCP)](#protocole-réseau-trame-tcp)
- [Prérequis et Installation](#-prérequis-et-installation)
  - [1. Prérequis système](#1-prérequis-système)
  - [2. Installation des dépendances](#2-installation-des-dépendances)
- [Comment lancer le programme](#-comment-lancer-le-programme)
- [Problèmes potentiels et bogues identifiés](#-problèmes-potentiels-et-bogues-identifiés)
  - [1. Crash au lancement sans arguments (`IndexError`)](#1-crash-au-lancement-sans-arguments-indexerror)
  - [2. Erreur de condition dans la validation des arguments (`verif_args`)](#2-erreur-de-condition-dans-la-validation-des-arguments-verif_args)
  - [3. Type du port non converti (`TypeError`)](#3-type-du-port-non-converti-typeerror)
  - [4. Dépassement de la résolution d'écran (`IndexError: out of bounds`)](#4-dépassement-de-la-résolution-décran-indexerror-out-of-bounds)
  - [5. Connexion TCP ouverte et fermée à chaque image (Goulot d'étranglement)](#5-connexion-tcp-ouverte-et-fermée-à-chaque-image-goulot-détranglement)
  - [6. Incompatibilité sous Linux avec Wayland](#6-incompatibilité-sous-linux-avec-wayland)
  - [7. Calcul de la couleur dominante trop restrictif](#7-calcul-de-la-couleur-dominante-trop-restrictif)
  - [8. Absence de gestion des déconnexions réseau](#8-absence-de-gestion-des-déconnexions-réseau)
- [Pistes d'amélioration & Code corrigé](#-pistes-damélioration--code-corrigé)
- [Exemple de récepteur (Côté microcontrôleur)](#-exemple-de-récepteur-côté-microcontrôleur)

---

## À quoi sert ce projet ?

Ce projet permet de créer un rétroéclairage immersif derrière un moniteur ou un téléviseur :
- **Capture en continu** de l'image affichée à l'écran du PC.
- **Extraction de la couleur dominante** de la scène affichée.
- **Transmission sans fil / réseau** de cette couleur vers un contrôleur matériel (par exemple un microcontrôleur ESP32 / ESP8266 pilotant un bandeau de LED adressables WS2812B / Neopixel).
- **Immersion visuelle accrue** lors du visionnage de films, séries ou de sessions de jeu vidéo en synchronisant la lumière ambiante avec l'affichage.

---

## Fonctionnement technique

Le script [`led.py`](led.py) fonctionne selon une boucle continue :
1. **Capture d'écran** : Prise d'une capture d'écran via `pyautogui.screenshot()`.
2. **Conversion de format** : Conversion de l'image RGB de Pillow en format BGR pour OpenCV (`cv2.cvtColor`).
3. **Échantillonnage de pixels** : Parcours d'une grille de coordonnées $(x, y)$ pour dénombrer la fréquence de chaque couleur.
4. **Sélection de la couleur dominante** : Recherche de la valeur $(R, G, B)$ la plus fréquente dans le dictionnaire `couleur_dom`.
5. **Envoi réseau** : Envoi de la trame binaire sur un socket TCP vers l'adresse IP et le port du récepteur.

### Protocole réseau (Trame TCP)

Le script envoie un paquet de **8 octets** à chaque mise à jour :

| Octet | Nom | Valeur / Description |
|:---:|:---:|:---|
| `0` | En-tête (Header) | `0x41` (caractère ASCII `'A'`, servant d'identifiant de trame) |
| `1` | Rouge (Red) | Valeur comprise entre `0` et `255` (`0x00` à `0xFF`) |
| `2` | Vert (Green) | Valeur comprise entre `0` et `255` (`0x00` à `0xFF`) |
| `3` | Bleu (Blue) | Valeur comprise entre `0` et `255` (`0x00` à `0xFF`) |
| `4` | Réservé / Padding | `0x00` |
| `5` | Réservé / Padding | `0x00` |
| `6` | Réservé / Padding | `0x00` |
| `7` | Réservé / Padding | `0x00` |

---

## Prérequis et Installation

### 1. Prérequis système

- **Python** 3.8 ou supérieur.
- **Linux (X11)** : `pyautogui` nécessite un serveur d'affichage X11 et l'utilitaire `scrot` ou `xlib`.
  ```bash
  sudo apt update
  sudo apt install scrot python3-tk python3-dev
  ```
  *(Voir la section [Incompatibilité Wayland](#6-incompatibilité-sous-linux-avec-wayland) si vous utilisez Wayland).*
- **Windows / macOS** : Les bibliothèques fonctionnent sans paquet système supplémentaire.

### 2. Installation des dépendances

Il est recommandé d'utiliser un environnement virtuel :

```bash
# 1. Création de l'environnement virtuel
python3 -m venv venv

# 2. Activation de l'environnement virtuel
# Sur Linux / macOS :
source venv/bin/activate
# Sur Windows :
venv\Scripts\activate

# 3. Installation des dépendances
pip install -r requirements.txt
```

Ou installation manuelle des paquets :
```bash
pip install pyautogui opencv-python numpy
```

---

## Comment lancer le programme

Le programme attend deux arguments en ligne de commande : l'adresse IP locale du microcontrôleur et son port d'écoute TCP.

```bash
python3 led.py <IP_DU_CONTROLEUR> <PORT>
```

### Exemple :
```bash
python3 led.py 192.168.1.42 8888
```

> [!NOTE]
> Le contrôleur (ESP8266, ESP32, etc.) doit être allumé, connecté au même réseau local (WiFi/Ethernet) et avoir un serveur TCP actif en écoute sur le port spécifié avant le lancement du script.

---

## Problèmes potentiels et bogues identifiés

Plusieurs anomalies sont présentes dans l'implémentation initiale de [`led.py`](led.py) et peuvent causer des plantages ou des dégradations de performance :

### 1. Crash au lancement sans arguments (`IndexError`)
- **Problème** : Dans le bloc `if __name__ == "__main__":`, la ligne suivante est exécutée **avant** la vérification des arguments :
  ```python
  DEST_IP, DEST_PORT = sys.argv[1], sys.argv[2]
  if verif_args(): ...
  ```
  Si aucun argument n'est fourni, Python lève immédiatement `IndexError: list index out of range` sans jamais afficher le message d'aide.
- **Solution** : Vérifier `len(sys.argv)` avant d'accéder aux indices 1 et 2.

### 2. Erreur de condition dans la validation des arguments (`verif_args`)
- **Problème** : La fonction `verif_args()` contient :
  ```python
  if len(sys.argv) != 2:
      print("Wrong usage: python3 led.py [Local_IP] [Port]")
  ```
  `sys.argv[0]` étant le nom du script, fournir deux paramètres (IP et Port) donne `len(sys.argv) == 3`. Avec le test actuel `!= 2`, le script considère qu'il y a une erreur même lorsque la syntaxe est correcte.
- **Solution** : Corriger le test en `if len(sys.argv) != 3:`.

