Pour exécuter le programme `audio.py`, vous devez installer les dépendances suivantes :

## Dépendances Python
- `os`
- `subprocess`
- `tkinter`
- `datetime`
- `threading`

## Dépendances externes
- `ffmpeg`

### Installation des dépendances

#### Windows
1. Installez Python à partir de [python.org](https://www.python.org/downloads/).
2. Installez `ffmpeg` :
    - Téléchargez `ffmpeg` depuis [ffmpeg.org](https://ffmpeg.org/download.html).
    - Extrayez le contenu et ajoutez le chemin du dossier `bin` de `ffmpeg` à la variable d'environnement `PATH`.
3. Installez les bibliothèques Python nécessaires :
    ```sh
    pip install tk
    ```

#### Linux
1. Installez Python (si ce n'est pas déjà fait) :
    ```sh
    sudo apt-get update
    sudo apt-get install python3 python3-pip
    ```
2. Installez `ffmpeg` :
    ```sh
    sudo apt-get install ffmpeg
    ```
3. Installez les bibliothèques Python nécessaires :
    ```sh
    sudo apt-get install python3-tk
    ```

Une fois toutes les dépendances installées, vous pouvez exécuter le programme `audio.py` en utilisant la commande suivante :
```sh
python3 audio.py
```