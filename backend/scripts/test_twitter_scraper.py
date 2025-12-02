def test_twitter_login():
    """Test la connexion à Twitter"""
    
    logger.info("=" * 60)
    logger.info("🧪 TEST DE CONNEXION TWITTER")
    logger.info("=" * 60)
    
    # Vérifier les credentials
    if not settings.TWITTER_EMAIL or not settings.TWITTER_PASSWORD:
        logger.error("❌ Credentials Twitter manquants dans le .env")
        logger.info("\nAjoute ces lignes dans ton fichier .env :")
        logger.info("TWITTER_EMAIL=ton_email@example.com")
        logger.info("TWITTER_PASSWORD=ton_mot_de_passe")
        logger.info("TWITTER_USERNAME=ton_@username")
        return False
    
    logger.info(f"📧 Email: {settings.TWITTER_EMAIL}")
    logger.info(f"👤 Username: {settings.TWITTER_USERNAME or 'Non défini'}")
    
    # Créer le scraper
    try:
        scraper = TwitterSeleniumScraper(
            twitter_email=settings.TWITTER_EMAIL,
            twitter_password=settings.TWITTER_PASSWORD,
            twitter_username=settings.TWITTER_USERNAME,
        )
        
        # Initialiser le driver
        scraper._init_driver()
        logger.success("✅ Chrome driver initialisé")
        
        # Se connecter
        if scraper._login():
            logger.success("✅ Connexion réussie à Twitter!")
            
            # Attendre et laisser le navigateur ouvert
            input("\n✨ Connexion réussie! Le navigateur va rester ouvert. Appuie sur Entrée quand tu veux fermer...")
            
            # NE PAS fermer immédiatement
            # scraper.close()
            return scraper  # Retourner le scraper au lieu de le fermer
        else:
            logger.error("❌ Échec de connexion")
            scraper.close()
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        logger.exception("Détails:")
        return False