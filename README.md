# AmbiantLedStrip

Système d'éclairage d'ambiance dynamique (type Ambilight) pour écran d'ordinateur, synchronisé en temps réel avec un ruban LED connecté au réseau local.

---

## Sommaire

- [À quoi sert ce projet ?](#à-quoi-sert-ce-projet-)
- [Fonctionnement technique](#fonctionnement-technique)
  - [Protocole réseau (Trame TCP)](#protocole-réseau-trame-tcp)
- [Prérequis et Installation](#prérequis-et-installation)
  - [1. Prérequis système](#1-prérequis-système)
  - [2. Installation des dépendances](#2-installation-des-dépendances)
- [Comment lancer le programme](#comment-lancer-le-programme)

---

## À quoi sert ce projet ?

Ce projet permet de concevoir un système de rétroéclairage adaptatif placé derrière un moniteur :
- **Capture continue de l'écran** : Prise de vue en direct de l'affichage vidéo du PC.
- **Analyse colorimétrique** : Détermination de la couleur principale de l'image.
- **Transmission réseau** : Envoi des composantes de couleur (Rouge, Vert, Bleu) via une liaison TCP vers un récepteur local.
- **Rendu lumineux** : Le contrôleur distant pilote un ruban de LED adressables pour projeter une lumière d'ambiance accordée au contenu affiché (films, séries, jeux vidéo).

---

## Fonctionnement technique

Le script [`led.py`](led.py) s'exécute de la manière suivante :
1. **Établissement du socket** : Ouverture d'une socket TCP vers l'adresse IP et le port spécifiés.
2. **Boucle de capture (`main`)** :
   - Prise d'une capture d'écran complète avec `pyautogui.screenshot()`.
   - Conversion de l'image RGB de Pillow vers l'espace BGR avec OpenCV (`cv2.cvtColor`).
3. **Échantillonnage** :
   - Parcours d'une grille de pixels (50 lignes x 10 colonnes).
   - Comptage des occurrences de chaque couleur dans un dictionnaire `couleur_dom`.
4. **Extraction de la couleur dominante** :
   - Sélection du tuple BGR ayant le nombre maximal d'occurrences.
   - Conversion en valeurs hexadécimales puis entières pour Rouge, Vert et Bleu.
5. **Transmission binaire** :
   - Construction d'une trame de 8 octets.
   - Envoi au récepteur via `co.sendall()`.

### Protocole réseau (Trame TCP)

Chaque trame envoyée mesure **8 octets** :

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
- **Windows / macOS** : Aucune dépendance système externe spécifique.

### 2. Installation des dépendances

Il est recommandé d'utiliser un environnement virtuel dédié :

```bash
# Création de l'environnement virtuel
python3 -m venv venv

# Activation de l'environnement virtuel
# Sur Linux / macOS :
source venv/bin/activate
# Sur Windows :
venv\Scripts\activate

# Installation des paquets requis
pip install -r requirements.txt
```

Ou directement avec pip :
```bash
pip install pyautogui opencv-python numpy
```

---

## Comment lancer le programme

Le programme requiert deux arguments en ligne de commande : l'adresse IP locale du microcontrôleur et son port d'écoute TCP.

```bash
python3 led.py <Local_IP> <Port>
```

### Exemple :
```bash
python3 led.py 192.168.1.42 8888
```

> [!NOTE]
> Le bandeau led doit être connecté au même réseau local et disposer d'un serveur TCP à l'écoute sur le port renseigné avant d'exécuter la commande.
