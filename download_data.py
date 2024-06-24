import os
import requests
from tqdm import tqdm
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

try:
    from termcolor import colored
except ImportError:
    import pip
    pip.main(['install', 'termcolor'])
    from termcolor import colored

# Créer les sous-dossiers
categories = ['elections', 'securite', 'emploi', 'insee']
base_dir = 'data'

if not os.path.exists(base_dir):
    os.makedirs(base_dir)

for category in categories:
    os.makedirs(os.path.join(base_dir, category), exist_ok=True)

# Fonction pour télécharger les fichiers
def download_file(url, save_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    with open(save_path, 'wb') as file:
        for data in tqdm(response.iter_content(block_size), total=total_size//block_size, unit='KB', unit_scale=True):
            file.write(data)

# Télécharger les fichiers pour chaque catégorie
for category in categories:
    file_path = f'data_links_{category}.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        links = file.readlines()
    
    for idx, link in enumerate(links):
        link = link.strip()
        if link:
            logger.info(colored(f'Downloading file {idx + 1}/{len(links)} from {category}: {link}', 'yellow'))
            file_name = link.split('/')[-1]
            save_path = os.path.join(base_dir, category, file_name)
            try:
                download_file(link, save_path)
                logger.info(colored(f'Successfully downloaded {file_name}', 'green'))
            except Exception as e:
                logger.error(colored(f'Failed to download {file_name}. Error: {e}', 'red'))

logger.info(colored('All files have been downloaded and organized.', 'green'))
