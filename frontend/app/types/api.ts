// Types pour l'API Backend

export interface Player {
    id: number;
    sorare_id: string;
    first_name: string | null;
    last_name: string | null;
    display_name: string | null;
    slug: string | null;
    club_name: string | null;
    club_slug: string | null;
    position: string | null;
    country: string | null;
    country_code: string | null;
    age: number | null;
    birth_date: string | null;
    average_score: number;
    total_games: number;
    season_games: number;
    last_game_score: number | null;
    is_active: boolean;
    is_injured: boolean;
    injury_status: string | null;
    image_url: string | null;
    card_sample_url: string | null;
    created_at: string | null;
    updated_at: string | null;
    last_sorare_sync: string | null;
}

export interface PlayerListResponse {
    total: number;
    players: Player[];
}

export interface Injury {
    id: number;
    player_id: number;
    injury_type: string | null;
    injury_description: string | null;
    severity: string | null;
    injury_date: string | null;
    expected_return_date: string | null;
    actual_return_date: string | null;
    is_active: boolean;
    source: string | null;
    source_url: string | null;
    created_at: string | null;
    updated_at: string | null;
}

export interface InjuryListResponse {
    total: number;
    injuries: Injury[];
}

export interface DashboardStats {
    overview: {
        total_players: number;
        active_players: number;
        injured_players: number;
        avg_team_score: number;
        active_injuries_count: number;
    };
    position_distribution: Record<string, number>;
    top_players: Array<{
        id: number;
        name: string;
        club: string;
        position: string;
        score: number;
        games: number;
    }>;
    last_update: {
        type: string;
        status: string;
        date: string;
        items_processed: number;
    } | null;
}

export interface SyncResponse {
    message: string;
    total_cards?: number;
    unique_players?: number;
    players_added: number;
    players_updated: number;
}

export interface ApiError {
    error: string;
    detail: string;
}

// ============================================
// 🆕 TYPES API-FOOTBALL
// ============================================

export interface FootballAPIPlayer {
    id: number;
    name: string;
    firstname: string | null;
    lastname: string | null;
    age: number | null;
    nationality: string | null;
    photo: string | null;
    height: string | null;
    weight: string | null;
    birth: {
        date: string | null;
        place: string | null;
        country: string | null;
    } | null;
    injured: boolean;
}

export interface FootballAPITeam {
    id: number;
    name: string;
    code: string | null;
    country: string | null;
    founded: number | null;
    logo: string | null;
    venue: {
        name: string | null;
        city: string | null;
        capacity: number | null;
    } | null;
}

export interface FootballAPIMatch {
    id: number;
    date: string;
    timestamp: number;
    venue: string | null;
    status: string | null;
    league: {
        id: number;
        name: string;
        country: string;
        logo: string | null;
    };
    home_team: {
        id: number;
        name: string;
        logo: string | null;
    };
    away_team: {
        id: number;
        name: string;
        logo: string | null;
    };
}

export interface FootballSearchResponse {
    success: boolean;
    count: number;
    players: FootballAPIPlayer[];
}

export interface ImportPlayerRequest {
    football_api_id: number;
    sorare_id: string;
    display_name: string;
    position?: string;
}

// ✅ CORRECTION: Le backend retourne directement un Player (PlayerCompleteResponse)
export interface ImportPlayerResponse extends Player {
    // La réponse est directement un Player avec tous ses champs
    football_data?: any; // Optionnel car peut être null
}