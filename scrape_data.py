import requests
from bs4 import BeautifulSoup
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

# URL de base et les URLs spécifiques
base_url = 'https://www.data.gouv.fr'
start_urls = {
    "elections": "https://www.data.gouv.fr/fr/pages/donnees-des-elections/",
    "securite": "https://www.data.gouv.fr/fr/pages/donnees-securite/",
    "emploi": "https://www.data.gouv.fr/fr/pages/donnees-emploi/",
    "insee": "https://www.data.gouv.fr/fr/organizations/institut-national-de-la-statistique-et-des-etudeseconomiques-insee/?datasets_page=7#organization-datasets"
}

# Fonction pour obtenir les liens de datasets
def get_links(url):
    logger.info(colored(f'Scraping main page {url} for dataset links...', 'blue'))
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')  # Utiliser lxml comme parser
    links = soup.find_all('a', href=True)
    data_links = [link['href'] for link in links if 'dataset' in link['href']]
    logger.info(colored(f'Found {len(data_links)} dataset links on {url}.', 'green'))
    return data_links

# Fonction pour scraper les liens de fichiers de données sur une page dataset
def get_data_files(url):
    logger.info(colored(f'Scraping data files from {url}...', 'blue'))
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')  # Utiliser lxml comme parser
    links = soup.find_all('a', href=True)
    file_links = [link['href'] for link in links if link['href'].endswith(('.csv', '.xlsx', '.txt', '.zip'))]
    logger.info(colored(f'Found {len(file_links)} data file links on {url}.', 'green'))
    return file_links

# Fonction pour scraper les liens de données pour une URL de départ
def scrape_data(start_url, category):
    all_links = get_links(start_url)

    # Filtrer et compléter les liens
    data_links = [link if link.startswith('http') else base_url + link for link in all_links]
    data_links = list(set(data_links))  # Éliminer les doublons
    logger.info(colored(f'Filtered and deduplicated to {len(data_links)} unique dataset links for {category}.', 'green'))

    # Scraper les liens des fichiers de données sur chaque page dataset
    all_file_links = []
    for idx, link in enumerate(data_links):
        logger.info(colored(f'Processing dataset page {idx + 1}/{len(data_links)}: {link}', 'yellow'))
        file_links = get_data_files(link)
        all_file_links.extend(file_links)

    # Filtrer les doublons
    all_file_links = list(set(all_file_links))
    logger.info(colored(f'Total unique data file links found for {category}: {len(all_file_links)}', 'green'))

    # Enregistrer les liens dans un fichier texte
    file_path = f'data_links_{category}.txt'
    with open(file_path, 'w', encoding='utf-8') as file:
        for link in all_file_links:
            file.write(f"{link}\n")

    logger.info(colored(f'All data file links for {category} have been saved to {file_path}.', 'green'))

# Scraper les données pour chaque catégorie
for category, url in start_urls.items():
    scrape_data(url, category)
