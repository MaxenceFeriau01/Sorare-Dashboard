// Types pour l'API Backend - Complet avec tous les types nécessaires

// ============================================
// PLAYERS
// ============================================

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
    // 🆕 Ligue
    league_name: string | null;
    league_id: number | null;
    league_country: string | null;
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

// 🆕 Nouveau type pour les statistiques par ligue
export interface LeagueStats {
    league_name: string;
    league_country: string | null;
    player_count: number;
    avg_score: number;
    injured_count: number;
}

export interface LeagueListResponse {
    success: boolean;
    leagues: string[];
}

// ============================================
// INJURIES
// ============================================

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

// ============================================
// DASHBOARD STATS
// ============================================

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

// ============================================
// SYNC
// ============================================

export interface SyncResponse {
    message: string;
    total_cards?: number;
    unique_players?: number;
    new_players?: number;
    updated_players?: number;
}

// ============================================
// API-FOOTBALL - TYPES
// ============================================

export interface FootballAPIPlayer {
    id: number;
    name: string;
    firstname: string;
    lastname: string;
    age: number;
    birth: {
        date: string;
        place: string;
        country: string;
    };
    nationality: string;
    height: string;
    weight: string;
    injured: boolean;
    photo: string;
}

export interface FootballAPITeam {
    id: number;
    name: string;
    code: string;
    country: string;
    founded: number;
    national: boolean;
    logo: string;
}

export interface FootballAPIMatch {
    fixture: {
        id: number;
        referee: string;
        timezone: string;
        date: string;
        timestamp: number;
        venue: {
            id: number;
            name: string;
            city: string;
        };
        status: {
            long: string;
            short: string;
            elapsed: number;
        };
    };
    league: {
        id: number;
        name: string;
        country: string;
        logo: string;
        flag: string;
        season: number;
        round: string;
    };
    teams: {
        home: {
            id: number;
            name: string;
            logo: string;
            winner: boolean | null;
        };
        away: {
            id: number;
            name: string;
            logo: string;
            winner: boolean | null;
        };
    };
    goals: {
        home: number | null;
        away: number | null;
    };
    score: {
        halftime: {
            home: number | null;
            away: number | null;
        };
        fulltime: {
            home: number | null;
            away: number | null;
        };
    };
}

export interface FootballSearchResult {
    player: FootballAPIPlayer;
    statistics: Array<{
        team: FootballAPITeam;
        league: {
            id: number;
            name: string;
            country: string;
            logo: string;
            flag: string;
            season: number;
        };
        games: {
            appearences: number;
            lineups: number;
            minutes: number;
            number: number | null;
            position: string;
            rating: string;
            captain: boolean;
        };
        goals: {
            total: number;
            conceded: number;
            assists: number;
            saves: number | null;
        };
        cards: {
            yellow: number;
            yellowred: number;
            red: number;
        };
    }>;
}

export interface FootballSearchResponse {
    success: boolean;
    results: number;
    players: FootballSearchResult[];
}

// ============================================
// IMPORT PLAYER
// ============================================

export interface ImportPlayerRequest {
    football_api_id: number;
    sorare_id: string;
    display_name: string;
    position?: string;
}

export interface ImportPlayerResponse {
    id: number;
    sorare_id: string;
    display_name: string;
    first_name: string | null;
    last_name: string | null;
    club_name: string | null;
    position: string | null;
    country: string | null;
    age: number | null;
    average_score: number;
    total_games: number;
    is_injured: boolean;
    football_data: {
        id: number;
        player_id: number;
        football_api_id: number;
        name: string;
        age: number | null;
        nationality: string | null;
        height: string | null;
        weight: string | null;
        photo: string | null;
        current_team: {
            id: number;
            name: string;
            logo: string | null;
        } | null;
        season_stats: {
            season: number;
            appearances: number;
            goals: number;
            assists: number;
            minutes: number;
            yellow_cards: number;
            red_cards: number;
            rating: number | null;
        };
        injury_status: {
            is_injured: boolean;
            type: string | null;
            reason: string | null;
            date: string | null;
        };
        upcoming_matches: Array<{
            date: string;
            opponent: string;
            competition: string;
            is_home: boolean;
            venue: string | null;
        }>;
        last_api_sync: string | null;
        created_at: string | null;
        updated_at: string | null;
    } | null;
}

// ============================================
// TEAM SQUAD
// ============================================

export interface SquadPlayer {
    id: number;
    name: string;
    age: number;
    number: number | null;
    position: string;
    photo: string;
}

export interface TeamSquadResponse {
    success: boolean;
    team: {
        id: number;
        name: string;
        logo: string;
    };
    players: SquadPlayer[];
}