// Client API pour communiquer avec le backend FastAPI

import axios from 'axios';
import type {
    Player,
    PlayerListResponse,
    Injury,
    InjuryListResponse,
    DashboardStats,
    SyncResponse,
} from '@/types/api';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_V1 = `${API_URL}/api/v1`;

// Instance Axios configurée
const api = axios.create({
    baseURL: API_V1,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 secondes
});

// Intercepteur pour logger les requêtes (dev only)
if (process.env.NODE_ENV === 'development') {
    api.interceptors.request.use((config) => {
        console.log(`🔵 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
    });

    api.interceptors.response.use(
        (response) => {
            console.log(`🟢 API Response: ${response.status} ${response.config.url}`);
            return response;
        },
        (error) => {
            console.error(`🔴 API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data);
            return Promise.reject(error);
        }
    );
}

// ============================================
// PLAYERS
// ============================================

export const playersApi = {
    // Récupérer tous les joueurs avec filtres
    getAll: async (params?: {
        skip?: number;
        limit?: number;
        position?: string;
        club?: string;
        is_injured?: boolean;
    }): Promise<PlayerListResponse> => {
        const { data } = await api.get<PlayerListResponse>('/players', { params });
        return data;
    },

    // Récupérer un joueur par ID
    getById: async (id: number): Promise<Player> => {
        const { data } = await api.get<Player>(`/players/${id}`);
        return data;
    },

    // Créer un joueur (manuel)
    create: async (player: Partial<Player>): Promise<Player> => {
        const { data } = await api.post<Player>('/players', player);
        return data;
    },

    // Mettre à jour un joueur
    update: async (id: number, player: Partial<Player>): Promise<Player> => {
        const { data } = await api.put<Player>(`/players/${id}`, player);
        return data;
    },

    // Supprimer un joueur
    delete: async (id: number): Promise<void> => {
        await api.delete(`/players/${id}`);
    },
};

// ============================================
// INJURIES
// ============================================

export const injuriesApi = {
    // Récupérer toutes les blessures avec filtres
    getAll: async (params?: {
        skip?: number;
        limit?: number;
        player_id?: number;
        is_active?: boolean;
    }): Promise<InjuryListResponse> => {
        const { data } = await api.get<InjuryListResponse>('/injuries', { params });
        return data;
    },

    // Récupérer une blessure par ID
    getById: async (id: number): Promise<Injury> => {
        const { data } = await api.get<Injury>(`/injuries/${id}`);
        return data;
    },

    // Créer une blessure
    create: async (injury: Partial<Injury>): Promise<Injury> => {
        const { data } = await api.post<Injury>('/injuries', injury);
        return data;
    },

    // Mettre à jour une blessure
    update: async (id: number, injury: Partial<Injury>): Promise<Injury> => {
        const { data } = await api.put<Injury>(`/injuries/${id}`, injury);
        return data;
    },

    // Supprimer une blessure
    delete: async (id: number): Promise<void> => {
        await api.delete(`/injuries/${id}`);
    },
};

// ============================================
// STATS / DASHBOARD
// ============================================

export const statsApi = {
    // Récupérer les stats du dashboard
    getDashboard: async (): Promise<DashboardStats> => {
        const { data } = await api.get<DashboardStats>('/stats/dashboard');
        return data;
    },
};

// ============================================
// SORARE SYNC
// ============================================

export const sorareApi = {
    // Tester la connexion Sorare
    testConnection: async (): Promise<{ status: string; message: string; email?: string }> => {
        const { data } = await api.get('/sorare/test-connection');
        return data;
    },

    // Synchroniser les joueurs depuis Sorare
    syncPlayers: async (): Promise<SyncResponse> => {
        const { data } = await api.post<SyncResponse>('/sorare/sync');
        return data;
    },

    // Récupérer les infos d'un joueur depuis Sorare
    getPlayerInfo: async (playerSlug: string): Promise<any> => {
        const { data } = await api.get(`/sorare/player/${playerSlug}`);
        return data;
    },
};

// ============================================
// HEALTH CHECK
// ============================================

export const healthApi = {
    check: async (): Promise<{ status: string; version: string }> => {
        const { data } = await api.get('/health', { baseURL: API_URL });
        return data;
    },
};

export default api;