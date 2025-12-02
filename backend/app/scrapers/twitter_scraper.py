"""
Scraper pour Twitter/X avec Selenium
Utilise ton compte Twitter pour scraper en temps réel
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from loguru import logger
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_scraper import BaseScraper


class TwitterSeleniumScraper(BaseScraper):
    """
    Scraper Twitter utilisant Selenium et ton compte personnel
    """
    
    def __init__(self, twitter_email: str, twitter_password: str, twitter_username: str = None):
        super().__init__(name="Twitter")
        
        self.twitter_email = twitter_email
        self.twitter_password = twitter_password
        self.twitter_username = twitter_username
        self.driver = None
        self.is_logged_in = False
        
        # Comptes Twitter fiables à surveiller
        self.verified_accounts = {
            # Clubs français
            "PSG_inside": 0.95,
            "OM_Officiel": 0.95,
            "OL": 0.95,
            "AS_Monaco": 0.95,
            "LOSC": 0.95,
            
            # Clubs anglais
            "ManCity": 0.95,
            "LFC": 0.95,
            "Arsenal": 0.95,
            "ManUtd": 0.95,
            "ChelseaFC": 0.95,
            
            # Clubs espagnols
            "realmadrid": 0.95,
            "FCBarcelona": 0.95,
            "Atleti": 0.95,
            
            # Clubs allemands
            "FCBayern": 0.95,
            "BVB": 0.95,
            
            # Clubs italiens
            "acmilan": 0.95,
            "Inter": 0.95,
            "juventusfc": 0.95,
            
            # Journalistes & Insiders
            "FabrizioRomano": 0.98,
            "lequipe": 0.95,
            "RMCsport": 0.95,
            "footmercato": 0.90,
            "Squawka": 0.90,
            "OptaJoe": 0.90,
            "WhoScored": 0.85,
        }
        
        # Mots-clés de recherche
        self.injury_keywords = [
            "injury", "injured", "blessé", "blessure",
            "forfait", "out", "absent", "indisponible",
            "sidelined", "ko", "ligament", "hamstring"
        ]
    
    def _init_driver(self):
        """Initialise le driver Chrome"""
        if self.driver:
            return
        
        logger.info("[Twitter] Initializing Chrome driver...")
        
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        try:
            self.driver = uc.Chrome(options=options)
            self.driver.set_window_size(1920, 1080)
            logger.success("[Twitter] Chrome driver initialized")
        except Exception as e:
            logger.error(f"[Twitter] Failed to initialize driver: {e}")
            raise
    
    def _login(self):
        """Se connecter à Twitter"""
        if self.is_logged_in:
            return True
        
        logger.info("[Twitter] Logging in...")
        
        try:
            self.driver.get("https://twitter.com/i/flow/login")
            time.sleep(5)
            
            # Email/Username
            logger.debug("[Twitter] Entering email/username...")
            email_selectors = [
                'input[autocomplete="username"]',
                'input[name="text"]',
                'input[type="text"]',
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.debug(f"[Twitter] Found email field with: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not email_input:
                logger.error("[Twitter] Could not find email field")
                return False
            
            email_input.clear()
            time.sleep(1)
            email_input.send_keys(self.twitter_email)
            time.sleep(1)
            email_input.send_keys(Keys.RETURN)
            time.sleep(3)
            
            # Password
            logger.debug("[Twitter] Entering password...")
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.debug(f"[Twitter] Found password field with: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not password_input:
                logger.error("[Twitter] Could not find password field")
                self.driver.save_screenshot("twitter_login_error.png")
                return False
            
            password_input.clear()
            time.sleep(1)
            password_input.send_keys(self.twitter_password)
            time.sleep(1)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Vérifier connexion
            current_url = self.driver.current_url
            if "home" in current_url or "twitter.com" in current_url:
                self.is_logged_in = True
                logger.success("[Twitter] ✅ Successfully logged in!")
                return True
            else:
                logger.error("[Twitter] Login failed")
                self.driver.save_screenshot("twitter_login_failed.png")
                return False
                
        except Exception as e:
            logger.error(f"[Twitter] Login error: {e}")
            self.driver.save_screenshot("twitter_login_exception.png")
            return False
    
    def search_player_news(self, player_name: str, player_club: str = None) -> List[Dict]:
        """Recherche des tweets sur un joueur"""
        logger.info(f"[Twitter] Searching for: {player_name}")
        
        self._init_driver()
        if not self._login():
            return []
        
        results = []
        query = f"{player_name} ({' OR '.join(self.injury_keywords)})"
        search_url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
        
        try:
            self.driver.get(search_url)
            time.sleep(3)
            
            tweets_data = self._scroll_and_extract_tweets(max_tweets=20)
            
            for tweet in tweets_data:
                results.append(self._normalize_result(
                    player_name=player_name,
                    title=f"Tweet by @{tweet['author']}",
                    content=tweet['text'],
                    url=tweet['url'],
                    date=tweet['date'],
                    source=f"Twitter (@{tweet['author']})",
                ))
            
            logger.success(f"[Twitter] Found {len(results)} tweets for {player_name}")
            
        except Exception as e:
            logger.error(f"[Twitter] Error searching: {e}")
        
        return results
    
    def get_injury_updates(self) -> List[Dict]:
        """Récupère les tweets sur blessures des comptes fiables"""
        logger.info("[Twitter] Getting injury updates")
        
        self._init_driver()
        if not self._login():
            return []
        
        all_results = []
        
        for account in list(self.verified_accounts.keys())[:10]:
            try:
                logger.info(f"[Twitter] Checking @{account}...")
                self.driver.get(f"https://twitter.com/{account}")
                time.sleep(3)
                
                tweets = self._scroll_and_extract_tweets(max_tweets=10)
                injury_tweets = [
                    t for t in tweets
                    if any(keyword in t['text'].lower() for keyword in self.injury_keywords)
                ]
                
                for tweet in injury_tweets:
                    all_results.append(self._normalize_result(
                        player_name="Unknown",
                        title=f"Tweet by @{account}",
                        content=tweet['text'],
                        url=tweet['url'],
                        date=tweet['date'],
                        source=f"Twitter (@{account})",
                    ))
                
            except Exception as e:
                logger.error(f"[Twitter] Error checking @{account}: {e}")
                continue
        
        return all_results
    
    def _scroll_and_extract_tweets(self, max_tweets: int = 20) -> List[Dict]:
        """Scrolle et extrait les tweets"""
        tweets = []
        seen_tweet_ids = set()
        scroll_attempts = 0
        max_scrolls = 5
        
        while len(tweets) < max_tweets and scroll_attempts < max_scrolls:
            tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            
            for tweet_elem in tweet_elements:
                if len(tweets) >= max_tweets:
                    break
                
                try:
                    tweet_data = self._extract_tweet_data(tweet_elem)
                    if tweet_data and tweet_data['id'] not in seen_tweet_ids:
                        tweets.append(tweet_data)
                        seen_tweet_ids.add(tweet_data['id'])
                except Exception as e:
                    continue
            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            scroll_attempts += 1
        
        return tweets
    
    def _extract_tweet_data(self, tweet_elem) -> Optional[Dict]:
        """Extrait les données d'un tweet"""
        try:
            text_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
            text = text_elem.text if text_elem else ""
            
            try:
                author_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Name"] a')
                author = author_elem.get_attribute('href').split('/')[-1]
            except:
                author = "unknown"
            
            try:
                time_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'time')
                tweet_link = time_elem.find_element(By.XPATH, './..').get_attribute('href')
            except:
                tweet_link = ""
            
            try:
                time_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'time')
                date_str = time_elem.get_attribute('datetime')
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                date = datetime.now()
            
            tweet_id = tweet_link.split('/')[-1] if tweet_link else f"{author}_{int(time.time())}"
            
            return {
                'id': tweet_id,
                'author': author,
                'text': text,
                'url': tweet_link,
                'date': date,
            }
            
        except Exception as e:
            return None
    
    def _extract_player_name(self, text: str) -> Optional[str]:
        """Extrait un nom de joueur d'un tweet"""
        return None
    
    def close(self):
        """Ferme le navigateur"""
        if self.driver:
            logger.info("[Twitter] Closing browser...")
            self.driver.quit()
            self.driver = None
            self.is_logged_in = False
    
    def __del__(self):
        """Destructeur"""
        self.close()


twitter_scraper = None