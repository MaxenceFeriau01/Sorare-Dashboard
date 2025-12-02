# 🎮 Sorare Dashboard - Ton Manager Personnel

Dashboard moderne pour gérer tes joueurs Sorare avec tracking automatique des blessures et infos.

## 🚀 Stack Technique

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Database**: PostgreSQL
- **Cache**: Redis
- **Tasks**: Celery (cron automatiques)
- **Container**: Docker & Docker Compose

## 📋 Prérequis

- Docker & Docker Compose installés
- Node.js 18+ (pour dev frontend)
- Python 3.11+ (pour dev backend)
- Git

## 🛠️ Installation Locale (Développement)

### 1. Clone et setup

```bash
cd sorare-dashboard
cp .env.example .env
# Édite .env avec tes credentials
```

### 2. Lancer l'environnement complet

```bash
# Mode développement (hot-reload activé)
docker-compose -f docker-compose.dev.yml up -d

# Ou sans Docker (développement local)
# Backend:
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (autre terminal):
cd frontend
npm install
npm run dev
```

### 3. Accès aux services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📁 Structure du Projet

```
sorare-dashboard/
├── backend/          # API FastAPI
├── frontend/         # Next.js App
├── nginx/           # Reverse proxy (prod)
├── docker-compose.yml
└── docker-compose.dev.yml
```

## 🎯 Fonctionnalités

### ✅ Phase 1 (Actuellement en dev)
- [ ] Connexion API Sorare
- [ ] Récupération de tes joueurs
- [ ] Dashboard avec stats
- [ ] Interface joueurs

### 🚧 Phase 2 (À venir)
- [ ] Bot scraping Twitter
- [ ] Bot scraping sites sport
- [ ] Système de notifications
- [ ] Cron automatiques

### 🎨 Phase 3 (Futur)
- [ ] Historique performances
- [ ] Prédictions IA
- [ ] Comparaisons joueurs

## 🐛 Debug

```bash
# Voir les logs
docker-compose -f docker-compose.dev.yml logs -f

# Logs backend uniquement
docker-compose -f docker-compose.dev.yml logs -f backend

# Restart un service
docker-compose -f docker-compose.dev.yml restart backend
```

## 🚀 Déploiement Proxmox (Plus tard)

Documentation à venir une fois le développement terminé.

## 📝 Notes

- Le mode développement active le hot-reload (modifications en temps réel)
- Les données PostgreSQL sont persistées dans un volume Docker
- Le frontend utilise Next.js 14 avec App Router

## 📄 License

Privé - Usage personnel