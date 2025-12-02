"""
Module de scraping pour détecter les blessures
"""
from .base_scraper import BaseScraper
from .twitter_scraper import TwitterSeleniumScraper
from .lequipe_scraper import lequipe_scraper
from .scraping_manager import scraping_manager

__all__ = [
    "BaseScraper",
    "TwitterSeleniumScraper",
    "lequipe_scraper",
    "scraping_manager",
]