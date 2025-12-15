// Client API pour communiquer avec le backend FastAPI

import axios from 'axios';
import type {
    Player,
    PlayerListResponse,
    Injury,
    InjuryListResponse,
    DashboardStats,
    SyncResponse,
    FootballSearchResponse,
    FootballAPIPlayer,
    FootballAPITeam,
    FootballAPIMatch,
    ImportPlayerRequest,
    ImportPlayerResponse,
} from '../app/types/api';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_V1 = `${API_URL}/api/v1`;

// Instance Axios configurée
const api = axios.create({
    baseURL: API_V1,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 120000,
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
    getAll: async (params?: {
        skip?: number;
        limit?: number;
        position?: string;
        club?: string;
        league?: string;
        is_injured?: boolean;
    }): Promise<PlayerListResponse> => {
        const { data } = await api.get<PlayerListResponse>('/players', { params });
        return data;
    },

    getById: async (id: number): Promise<Player> => {
        const { data } = await api.get<Player>(`/players/${id}`);
        return data;
    },

    create: async (player: Partial<Player>): Promise<Player> => {
        const { data } = await api.post<Player>('/players', player);
        return data;
    },

    update: async (id: number, player: Partial<Player>): Promise<Player> => {
        const { data} = await api.put<Player>(`/players/${id}`, player);
        return data;
    },

    delete: async (id: number): Promise<void> => {
        await api.delete(`/players/${id}`);
    },
};

// ============================================
// INJURIES
// ============================================

export const injuriesApi = {
    getAll: async (params?: {
        skip?: number;
        limit?: number;
        player_id?: number;
        is_active?: boolean;
    }): Promise<InjuryListResponse> => {
        const { data } = await api.get<InjuryListResponse>('/injuries', { params });
        return data;
    },

    getById: async (id: number): Promise<Injury> => {
        const { data } = await api.get<Injury>(`/injuries/${id}`);
        return data;
    },

    create: async (injury: Partial<Injury>): Promise<Injury> => {
        const { data } = await api.post<Injury>('/injuries', injury);
        return data;
    },

    update: async (id: number, injury: Partial<Injury>): Promise<Injury> => {
        const { data } = await api.put<Injury>(`/injuries/${id}`, injury);
        return data;
    },

    delete: async (id: number): Promise<void> => {
        await api.delete(`/injuries/${id}`);
    },
};

// ============================================
// STATS / DASHBOARD
// ============================================

export const statsApi = {
    getDashboard: async (): Promise<DashboardStats> => {
        const { data } = await api.get<DashboardStats>('/stats/dashboard');
        return data;
    },
};

// ============================================
// SORARE SYNC
// ============================================

export const sorareApi = {
    testConnection: async (): Promise<{ status: string; message: string; email?: string }> => {
        const { data } = await api.get('/sorare/test-connection');
        return data;
    },

    syncPlayers: async (): Promise<SyncResponse> => {
        const { data } = await api.post<SyncResponse>('/sorare/sync');
        return data;
    },

    getPlayerInfo: async (playerSlug: string): Promise<any> => {
        const { data } = await api.get(`/sorare/player/${playerSlug}`);
        return data;
    },
};

// ============================================
// API-FOOTBALL
// ============================================

export const footballApi = {
    checkStatus: async (): Promise<any> => {
        const { data } = await api.get('/football/status');
        return data;
    },

    searchPlayers: async (query: string, page: number = 1): Promise<FootballSearchResponse> => {
        const { data } = await api.get<FootballSearchResponse>('/football/search-players', {
            params: { query, page }
        });
        return data;
    },

    getPlayerDetails: async (playerId: number, season: number = 2025): Promise<any> => {
        const { data } = await api.get(`/football/player/${playerId}`, {
            params: { season }
        });
        return data;
    },

    searchTeams: async (query: string, country?: string): Promise<any> => {
        const { data } = await api.get('/football/search-teams', {
            params: { query, country }
        });
        return data;
    },

    getTeamInfo: async (teamId: number): Promise<any> => {
        const { data } = await api.get(`/football/team/${teamId}`);
        return data;
    },

    getTeamSquad: async (teamId: number): Promise<any> => {
        const { data } = await api.get(`/football/team/${teamId}/squad`);
        return data;
    },

    getUpcomingMatches: async (teamId: number, next: number = 5): Promise<{ success: boolean; count: number; matches: FootballAPIMatch[] }> => {
        const { data } = await api.get(`/football/matches/upcoming/${teamId}`, {
            params: { next }
        });
        return data;
    },

    getLeagues: async (country?: string, season: number = 2025): Promise<any> => {
        const { data } = await api.get('/football/leagues', {
            params: { country, season }
        });
        return data;
    },

    getInjuries: async (playerId?: number, teamId?: number, season: number = 2025): Promise<any> => {
        const { data } = await api.get('/football/injuries', {
            params: { player_id: playerId, team_id: teamId, season }
        });
        return data;
    },

    syncInjuries: async (): Promise<any> => {
        const { data } = await api.post('/football/sync-injuries');
        return data;
    },

    importPlayer: async (request: ImportPlayerRequest): Promise<ImportPlayerResponse> => {
        const { data } = await api.post<ImportPlayerResponse>('/players/import', request);
        return data;
    },

    syncPlayer: async (playerId: number): Promise<any> => {
        const { data } = await api.post(`/players/${playerId}/sync`);
        return data;
    },

    getCompletePlayerData: async (playerId: number): Promise<any> => {
        const { data } = await api.get(`/players/${playerId}/complete`);
        return data;
    },

    getDashboardPredictions: async (): Promise<any> => {
        const { data } = await api.get('/football/dashboard-predictions');
        return data;
    },

    getPlayerNextMatchPrediction: async (playerId: number): Promise<any> => {
        const { data } = await api.get(`/football/player/${playerId}/next-match-prediction`);
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