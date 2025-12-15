"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { Player, LeagueStats } from "@/app/types/api";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface PlayersTabsProps {
    onPlayerSelect?: (player: Player) => void;
}

export default function PlayersTabs({ onPlayerSelect }: PlayersTabsProps) {
    const [selectedLeague, setSelectedLeague] = useState<string | "all">("all");
    
    // Récupérer les statistiques par ligue
    const { data: leaguesData, isLoading: leaguesLoading } = useQuery<LeagueStats[]>({
        queryKey: ["leagues-stats"],
        queryFn: async () => {
            const response = await axios.get(`${API_URL}/api/v1/players/leagues`);
            return response.data;
        },
    });

    // Récupérer les joueurs filtrés par ligue
    const { data: playersData, isLoading: playersLoading, refetch } = useQuery<{
        total: number;
        players: Player[];
    }>({
        queryKey: ["players", selectedLeague],
        queryFn: async () => {
            const params: any = { limit: 500 };
            if (selectedLeague !== "all") {
                params.league = selectedLeague;
            }
            
            const response = await axios.get(`${API_URL}/api/v1/players`, { params });
            return response.data;
        },
    });

    // Sélectionner automatiquement la première ligue au chargement
    useEffect(() => {
        if (leaguesData && leaguesData.length > 0 && selectedLeague === "all") {
            setSelectedLeague(leaguesData[0].league_name);
        }
    }, [leaguesData]);

    if (leaguesLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="w-full">
            {/* Onglets des ligues */}
            <div className="border-b border-gray-200 bg-white rounded-t-lg">
                <div className="flex overflow-x-auto">
                    {/* Onglet "Tous" */}
                    <button
                        onClick={() => setSelectedLeague("all")}
                        className={`px-6 py-3 text-sm font-medium whitespace-nowrap transition-colors border-b-2 ${
                            selectedLeague === "all"
                                ? "border-blue-600 text-blue-600"
                                : "border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300"
                        }`}
                    >
                        <div className="flex flex-col items-center">
                            <span>Tous les joueurs</span>
                            <span className="text-xs text-gray-500 mt-1">
                                {leaguesData?.reduce((acc, l) => acc + l.player_count, 0) || 0}
                            </span>
                        </div>
                    </button>

                    {/* Onglets des ligues */}
                    {leaguesData?.map((league) => (
                        <button
                            key={league.league_name}
                            onClick={() => setSelectedLeague(league.league_name)}
                            className={`px-6 py-3 text-sm font-medium whitespace-nowrap transition-colors border-b-2 ${
                                selectedLeague === league.league_name
                                    ? "border-blue-600 text-blue-600"
                                    : "border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300"
                            }`}
                        >
                            <div className="flex flex-col items-center">
                                <span>{league.league_name}</span>
                                <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                                    <span>{league.player_count} joueurs</span>
                                    {league.injured_count > 0 && (
                                        <span className="text-red-500">
                                            • {league.injured_count} blessés
                                        </span>
                                    )}
                                </div>
                            </div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Contenu des joueurs */}
            <Card className="rounded-t-none p-6">
                {playersLoading ? (
                    <div className="flex items-center justify-center h-32">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                ) : (
                    <>
                        {/* En-tête */}
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-gray-900">
                                {selectedLeague === "all" 
                                    ? "Tous les joueurs" 
                                    : `${selectedLeague} - ${playersData?.players.length || 0} joueurs`}
                            </h2>
                            
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => refetch()}
                            >
                                <RefreshCw className="h-4 w-4 mr-2" />
                                Actualiser
                            </Button>
                        </div>

                        {/* Grille de joueurs */}
                        {playersData?.players && playersData.players.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                                {playersData.players.map((player) => (
                                    <Card
                                        key={player.id}
                                        onClick={() => onPlayerSelect?.(player)}
                                        className="p-4 hover:shadow-lg transition-shadow cursor-pointer"
                                    >
                                        {/* Image du joueur */}
                                        <div className="flex justify-center mb-3">
                                            {player.image_url ? (
                                                <img
                                                    src={player.image_url}
                                                    alt={player.display_name || "Joueur"}
                                                    className="w-20 h-20 rounded-full object-cover"
                                                />
                                            ) : (
                                                <div className="w-20 h-20 rounded-full bg-gray-200 flex items-center justify-center">
                                                    <span className="text-2xl text-gray-400">👤</span>
                                                </div>
                                            )}
                                        </div>

                                        {/* Nom */}
                                        <h3 className="font-semibold text-center text-gray-900 mb-1 truncate">
                                            {player.display_name || `${player.first_name} ${player.last_name}`}
                                        </h3>

                                        {/* Club */}
                                        <p className="text-sm text-center text-gray-600 mb-2 truncate">
                                            {player.club_name || "Club inconnu"}
                                        </p>

                                        {/* Stats */}
                                        <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                                            <Badge variant="outline">
                                                {player.position || "N/A"}
                                            </Badge>
                                            <span>⚽ {player.total_games} matchs</span>
                                        </div>

                                        {/* Score moyen */}
                                        <div className="flex items-center justify-between text-xs">
                                            <span className="text-gray-600">Score moyen:</span>
                                            <span className="font-semibold text-green-600">
                                                {player.average_score.toFixed(1)}
                                            </span>
                                        </div>

                                        {/* Badge blessure */}
                                        {player.is_injured && (
                                            <Badge variant="destructive" className="mt-2 w-full justify-center">
                                                🚑 Blessé
                                            </Badge>
                                        )}
                                    </Card>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-12 text-gray-500">
                                <p className="text-lg">Aucun joueur trouvé</p>
                                <p className="text-sm mt-2">
                                    Importez des joueurs depuis l'API-Football pour commencer
                                </p>
                            </div>
                        )}
                    </>
                )}
            </Card>
        </div>
    );
}