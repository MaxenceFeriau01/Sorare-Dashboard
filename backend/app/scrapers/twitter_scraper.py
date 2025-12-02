"""
Scraper pour Twitter/X avec Selenium et undetected-chromedriver.
Version optimisée pour la recherche multi-joueurs (session persistante) et délais réduits (5s).
"""
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

class TwitterSeleniumScraper:
    """
    Scraper Twitter utilisant Selenium pour l'extraction de nouvelles sur les blessures.
    """
    
    def __init__(self, twitter_email: str, twitter_password: str, twitter_username: str = None):
        self.name = "Twitter"
        self.twitter_email = twitter_email
        self.twitter_password = twitter_password
        self.twitter_username = twitter_username
        
        self.driver = None
        self.is_logged_in = False
        
        # Mots-clés de base pour les requêtes (doivent être synchronisés avec keywords.py)
        self.injury_keywords = [
            "injury", "injured", "blessé", "blessure",
            "forfait", "out", "absent", "indisponible",
            "sidelined", "ko", "ligament", "hamstring"
        ]
        
    def _init_driver(self):
        """Initialise le driver undetected-chromedriver."""
        if self.driver is None:
            try:
                options = uc.ChromeOptions()
                # options.headless = False # Décommenter pour voir la fenêtre
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36")

                self.driver = uc.Chrome(options=options)
                logger.info("[Twitter] Chrome driver initialisé.")
            except Exception as e:
                logger.error(f"[Twitter] Erreur lors de l'initialisation du driver : {e}")
                raise

    def _find_element_by_selectors(self, selectors: List[str], timeout: int = 5): # DÉLAI PAR DÉFAUT : 5S
        """Essaie de trouver un élément avec une liste de sélecteurs."""
        for selector in selectors:
            try:
                by = By.XPATH if selector.startswith('/') else By.CSS_SELECTOR
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, selector))
                )
            except TimeoutException:
                continue
        raise TimeoutException(f"Impossible de trouver l'élément avec les sélecteurs fournis après {timeout}s.")

    def _handle_cookie_banner(self):
        """Tente de cliquer sur le bouton d'acceptation des cookies ou la bannière de connexion initiale."""
        initial_action_selectors = [
            '//span[contains(text(), "Accepter tout")]/ancestor::button',
            '//span[contains(text(), "Next")]/ancestor::button',
            '//span[contains(text(), "Se connecter")]/ancestor::button', 
            '//button[@role="button"]',
        ]
        
        try:
            action_button = self._find_element_by_selectors(initial_action_selectors, timeout=3) 
            logger.info("[Twitter] Écran initial/Bannière détectée, tentative de clic.")
            action_button.click()
            time.sleep(0.5) 
        except TimeoutException:
            logger.info("[Twitter] Aucun écran initial ou bannière bloquante détectée. Continuez.")
        except Exception as e:
            logger.warning(f"[Twitter] Erreur lors de la gestion de l'écran initial : {e}")
            
    def _login(self) -> bool:
        """Tente de se connecter à Twitter/X."""
        if self.is_logged_in and self.driver:
            return True
            
        try:
            self._init_driver()
            self.driver.get("https://twitter.com/i/flow/login")
            
            # 1. Gestion de la bannière
            self._handle_cookie_banner()
            
            # 2. Saisie Email/Nom d'utilisateur (TIMEOUT: 5s)
            email_field = self._find_element_by_selectors([
                '//input[@data-testid="User-Name-Field"]',
                '//input[@autocomplete="username"]', 
                'input[name="text"]',                
            ], timeout=5)
            
            logger.info("[Twitter] Saisie de l'email/username...")
            email_field.send_keys(self.twitter_email)
            email_field.send_keys(Keys.RETURN)
            
            time.sleep(1) 

            # 3. Étape Nom d'utilisateur (si elle apparaît) (TIMEOUT: 5s)
            try:
                username_field = self._find_element_by_selectors([
                    '//input[@data-testid="ocfEnterText"]', 
                    'input[name="text"]',
                ], timeout=5)
                
                if self.twitter_username:
                     logger.info("[Twitter] Étape de vérification du nom d'utilisateur détectée.")
                     username_field.send_keys(self.twitter_username)
                     username_field.send_keys(Keys.RETURN)
                     time.sleep(1) 
                else:
                     logger.error("[Twitter] Nom d'utilisateur requis par Twitter pour la connexion, mais non fourni.")
                     return False
            except TimeoutException:
                pass 
            
            # 4. Saisie Mot de passe (TIMEOUT: 5s)
            password_field = self._find_element_by_selectors([
                '//input[@name="password"]',          
                'input[type="password"]',            
            ], timeout=5) 
            
            logger.info("[Twitter] Saisie du mot de passe...")
            password_field.send_keys(self.twitter_password)
            password_field.send_keys(Keys.RETURN)
            
            # 5. Vérification finale (Confirmation de la page d'accueil) (TIMEOUT: 20s)
            logger.info("[Twitter] Attente de la confirmation de la page d'accueil (Barre de recherche)...")
            WebDriverWait(self.driver, 20).until( 
                EC.presence_of_element_located((By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]')) 
            )
            
            self.is_logged_in = True
            logger.success("✅ [Twitter] Connexion réussie et page d'accueil chargée. Prêt pour la recherche.")
            return True
            
        except TimeoutException:
            logger.error("[Twitter] Timeout lors de la connexion. Échec de la détection de l'élément à l'étape finale.")
        except Exception as e:
            logger.error(f"[Twitter] Échec de la connexion : {e}")
        
        return False

    # ---------------------------------------------------------------------
    # Fonctions de Recherche et d'Extraction
    # ---------------------------------------------------------------------

    def _extract_tweet_data(self, tweet_element) -> Optional[Dict]:
        """Extrait l'auteur, le contenu, la date et l'URL d'un élément de tweet."""
        data = {}
        
        try:
            content_element = tweet_element.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
            data['text'] = content_element.text
        except NoSuchElementException:
            return None 

        data['date'] = datetime.now()
        data['url'] = "N/A"
        try:
            time_element = tweet_element.find_element(By.TAG_NAME, 'time')
            datetime_str = time_element.get_attribute('datetime')
            data['date'] = datetime.fromisoformat(datetime_str.replace('Z', '+00:00')) if datetime_str else datetime.now()
            
            url_element = time_element.find_element(By.XPATH, '..')
            data['url'] = url_element.get_attribute('href')
        except (NoSuchElementException, Exception):
            pass

        data['author'] = "N/A"
        try:
            author_element = tweet_element.find_element(By.XPATH, './/div[@data-testid="User-Names"]//a')
            author_url = author_element.get_attribute('href')
            data['author'] = author_url.split('/')[-1] if author_url else "N/A"
        except (NoSuchElementException, Exception):
            pass
            
        return data
        

    def _scroll_and_extract_tweets(self, max_tweets: int = 30) -> List[Dict]:
        """Scrolle la page et extrait les tweets jusqu'à atteindre max_tweets."""
        results = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        try:
             WebDriverWait(self.driver, 5).until( # Délai réduit à 5s
                EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')) 
            )
             logger.info("[Twitter] Premiers résultats de recherche chargés.")
        except TimeoutException:
            logger.warning("[Twitter] Aucun tweet trouvé immédiatement après la recherche.")
        
        max_scrolls = 5 
        scroll_count = 0
        
        while len(results) < max_tweets and scroll_count < max_scrolls:
            tweet_elements = self.driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            
            current_urls = {r['url'] for r in results}
            for tweet_element in tweet_elements:
                tweet_data = self._extract_tweet_data(tweet_element)
                
                if tweet_data and tweet_data.get('url') not in current_urls and tweet_data.get('url') != "N/A": 
                    results.append(tweet_data)
                    current_urls.add(tweet_data['url'])
                    
                    if len(results) >= max_tweets:
                        break
            
            if len(results) >= max_tweets:
                break
                
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1) # Délai de scroll réduit
            scroll_count += 1
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height and len(results) < max_tweets:
                logger.info("[Twitter] Bas de la page atteint ou chargement bloqué, arrêt du scrolling.")
                break
            last_height = new_height
            
        return results

    def _normalize_result(self, player_name: str, title: str, content: str, url: str, date: datetime, source: str, author: str = None) -> Dict:
        """Normalise la structure des données récupérées par le scraper."""
        return {
            'player_name': player_name,
            'title': title,
            'content': content,
            'url': url,
            'date': date,
            'source': source,
            'author': author
        }
    
    
    def search_player_news(self, player_name: str, max_tweets_per_query: int = 30) -> List[Dict]:
        """
        Recherche des tweets en utilisant des requêtes multiples pour une analyse complète.
        Se connecte uniquement si self.is_logged_in est False (session persistante).
        """
        logger.info(f"[Twitter] Starting multi-query search for: {player_name}")
        
        # 🚨 Gestion de la session persistante : Connexion si la session n'est pas active
        if not self.is_logged_in:
            logger.info("[Twitter] Tentative de connexion (Première recherche)...")
            if not self._login():
                return []
        else:
            logger.info("[Twitter] Session déjà active. Réutilisation de la connexion.")
        
        all_results = []
        
        # Recherche limitée aux tweets du jour (aujourd'hui)
        today = datetime.now().strftime('%Y-%m-%d')
        injury_terms = ' OR '.join(self.injury_keywords)
        composition_terms = ' OR '.join(["lineup", "titulaire", "composition", "start", "bench", "remplaçant"])
        
        queries = {
            "Blessure/Forfait": f'"{player_name}" ({injury_terms}) since:{today}',
            "Composition/Présence": f'"{player_name}" ({composition_terms}) since:{today}',
        }
        
        for query_type, query in queries.items():
            logger.info(f"[Twitter] Exécuter la requête : {query_type}")
            safe_query = query.replace(' ', '+').replace('"', '%22')
            search_url = f"https://twitter.com/search?q={safe_query}&src=typed_query&f=live"
            
            try:
                self.driver.get(search_url)
                time.sleep(2) 
                
                tweets_data = self._scroll_and_extract_tweets(max_tweets=max_tweets_per_query)
                
                for tweet in tweets_data:
                    if tweet['url'] not in [r['url'] for r in all_results]:
                        author_handle = tweet['author'].replace('@', '').lower()
                        
                        all_results.append(self._normalize_result(
                            player_name=player_name,
                            title=f"Tweet {query_type} by @{author_handle}",
                            content=tweet['text'],
                            url=tweet['url'],
                            date=tweet.get('date', datetime.now()),
                            source=author_handle, 
                            author=author_handle
                        ))
                
                logger.success(f"[Twitter] Found {len(tweets_data)} tweets for {query_type}")
                
            except Exception as e:
                logger.error(f"[Twitter] Error searching for {query_type}: {e}")
        
        logger.info(f"[Twitter] Total de {len(all_results)} résultats consolidés pour {player_name}")
        return all_results

    def close(self):
        """
        Ferme le navigateur. À appeler une seule fois après la dernière recherche pour éviter 
        l'erreur "Descripteur non valide".
        """
        if self.driver:
            logger.info("[Twitter] Closing browser...")
            try:
                self.driver.quit()
            except WebDriverException as e:
                logger.warning(f"WebDriverException lors de la fermeture : {e}. Ignoré.")
            
            self.driver = None
            self.is_logged_in = False