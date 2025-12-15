"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Calendar, Clock, Loader2, ChevronRight, TrendingUp } from "lucide-react";
import type { Player } from "@/app/types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Match {
    id: number;
    date: string;
    home_team: string;
    away_team: string;
    home_logo?: string;
    away_logo?: string;
    league: string;
    venue?: string;
    home_players: Player[];
    away_players: Player[];
}

export default function UpcomingMatches() {
    const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);

    // Récupérer les prochains matchs des joueurs
    const { data: matches, isLoading } = useQuery<Match[]>({
        queryKey: ["upcoming-matches"],
        queryFn: async () => {
            const response = await axios.get(`${API_URL}/api/v1/players/upcoming-matches`);
            return response.data.matches;
        },
        refetchInterval: 5 * 60 * 1000, // Rafraîchir toutes les 5 minutes
    });

    const formatMatchDate = (dateString: string) => {
        const date = new Date(dateString);
        return {
            date: date.toLocaleDateString("fr-FR", {
                weekday: "short",
                day: "numeric",
                month: "short",
            }),
            time: date.toLocaleTimeString("fr-FR", {
                hour: "2-digit",
                minute: "2-digit",
            }),
        };
    };

    if (isLoading) {
        return (
            <Card className="p-6">
                <div className="flex items-center justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                </div>
            </Card>
        );
    }

    if (!matches || matches.length === 0) {
        return (
            <Card className="p-6">
                <h2 className="text-xl font-bold mb-4">📅 Prochains matchs</h2>
                <p className="text-gray-500 text-center py-8">
                    Aucun match à venir pour vos joueurs
                </p>
            </Card>
        );
    }

    // Compter le total de joueurs concernés
    const totalPlayers = matches.reduce(
        (sum, match) => sum + match.home_players.length + match.away_players.length,
        0
    );

    return (
        <>
            <Card className="p-6">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-xl font-bold">📅 Prochains matchs</h2>
                        <p className="text-sm text-gray-500 mt-1">
                            {matches.length} match{matches.length > 1 ? "s" : ""} • {totalPlayers}{" "}
                            joueur{totalPlayers > 1 ? "s" : ""} concerné{totalPlayers > 1 ? "s" : ""}
                        </p>
                    </div>
                </div>

                <div className="space-y-3">
                    {matches.map((match) => {
                        const { date, time } = formatMatchDate(match.date);
                        const playerCount = match.home_players.length + match.away_players.length;

                        return (
                            <button
                                key={match.id}
                                onClick={() => setSelectedMatch(match)}
                                className="w-full group"
                            >
                                <Card className="p-4 hover:shadow-lg transition-all hover:bg-gray-50 border-2 hover:border-blue-200">
                                    <div className="flex items-center justify-between">
                                        {/* Équipes */}
                                        <div className="flex-1 flex items-center justify-between gap-4">
                                            {/* Équipe domicile */}
                                            <div className="flex items-center gap-3 flex-1">
                                                {match.home_logo && (
                                                    <img
                                                        src={match.home_logo}
                                                        alt={match.home_team}
                                                        className="w-10 h-10 object-contain"
                                                    />
                                                )}
                                                <div className="text-left">
                                                    <p className="font-semibold text-gray-900">
                                                        {match.home_team}
                                                    </p>
                                                    {match.home_players.length > 0 && (
                                                        <p className="text-xs text-blue-600 font-medium">
                                                            {match.home_players.length} joueur
                                                            {match.home_players.length > 1 ? "s" : ""}
                                                        </p>
                                                    )}
                                                </div>
                                            </div>

                                            {/* Score séparateur */}
                                            <div className="text-center px-4">
                                                <p className="text-2xl font-bold text-gray-400">VS</p>
                                                <div className="flex items-center gap-1 text-xs text-gray-500 mt-1">
                                                    <Calendar className="h-3 w-3" />
                                                    <span>{date}</span>
                                                </div>
                                                <div className="flex items-center gap-1 text-xs text-gray-500">
                                                    <Clock className="h-3 w-3" />
                                                    <span>{time}</span>
                                                </div>
                                            </div>

                                            {/* Équipe extérieur */}
                                            <div className="flex items-center gap-3 flex-1 justify-end">
                                                <div className="text-right">
                                                    <p className="font-semibold text-gray-900">
                                                        {match.away_team}
                                                    </p>
                                                    {match.away_players.length > 0 && (
                                                        <p className="text-xs text-blue-600 font-medium">
                                                            {match.away_players.length} joueur
                                                            {match.away_players.length > 1 ? "s" : ""}
                                                        </p>
                                                    )}
                                                </div>
                                                {match.away_logo && (
                                                    <img
                                                        src={match.away_logo}
                                                        alt={match.away_team}
                                                        className="w-10 h-10 object-contain"
                                                    />
                                                )}
                                            </div>
                                        </div>

                                        {/* Badge + Flèche */}
                                        <div className="ml-4 flex items-center gap-3">
                                            <Badge
                                                variant="secondary"
                                                className="bg-blue-100 text-blue-700"
                                            >
                                                {playerCount} joueur{playerCount > 1 ? "s" : ""}
                                            </Badge>
                                            <ChevronRight className="h-5 w-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                                        </div>
                                    </div>

                                    {/* Ligue */}
                                    <div className="mt-2 pt-2 border-t border-gray-100">
                                        <p className="text-xs text-gray-500">
                                            {match.league}
                                            {match.venue && ` • ${match.venue}`}
                                        </p>
                                    </div>
                                </Card>
                            </button>
                        );
                    })}
                </div>
            </Card>

            {/* Modal avec les joueurs du match */}
            <Dialog open={!!selectedMatch} onOpenChange={() => setSelectedMatch(null)}>
                <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
                    {selectedMatch && (
                        <>
                            <DialogHeader>
                                <DialogTitle className="text-2xl">
                                    <div className="flex items-center justify-between gap-4">
                                        <span>{selectedMatch.home_team}</span>
                                        <span className="text-gray-400">VS</span>
                                        <span>{selectedMatch.away_team}</span>
                                    </div>
                                    <p className="text-sm font-normal text-gray-500 mt-2">
                                        {formatMatchDate(selectedMatch.date).date} à{" "}
                                        {formatMatchDate(selectedMatch.date).time}
                                    </p>
                                </DialogTitle>
                            </DialogHeader>

                            <div className="mt-6 space-y-6">
                                {/* Joueurs de l'équipe domicile */}
                                {selectedMatch.home_players.length > 0 && (
                                    <div>
                                        <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                                            {selectedMatch.home_logo && (
                                                <img
                                                    src={selectedMatch.home_logo}
                                                    alt={selectedMatch.home_team}
                                                    className="w-6 h-6"
                                                />
                                            )}
                                            {selectedMatch.home_team} ({selectedMatch.home_players.length})
                                        </h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                            {selectedMatch.home_players.map((player) => (
                                                <PlayerCard key={player.id} player={player} />
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Joueurs de l'équipe extérieur */}
                                {selectedMatch.away_players.length > 0 && (
                                    <div>
                                        <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                                            {selectedMatch.away_logo && (
                                                <img
                                                    src={selectedMatch.away_logo}
                                                    alt={selectedMatch.away_team}
                                                    className="w-6 h-6"
                                                />
                                            )}
                                            {selectedMatch.away_team} ({selectedMatch.away_players.length})
                                        </h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                            {selectedMatch.away_players.map((player) => (
                                                <PlayerCard key={player.id} player={player} />
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="mt-6 flex justify-end">
                                <Button
                                    variant="outline"
                                    onClick={() => setSelectedMatch(null)}
                                >
                                    Fermer
                                </Button>
                            </div>
                        </>
                    )}
                </DialogContent>
            </Dialog>
        </>
    );
}

// Composant carte joueur (même style que dashboard)
function PlayerCard({ player }: { player: Player }) {
    return (
        <Card className="p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start gap-3">
                <img
                    src={
                        player.image_url ||
                        `https://ui-avatars.com/api/?name=${encodeURIComponent(
                            player.display_name || "Player"
                        )}&background=random`
                    }
                    alt={player.display_name || "Player"}
                    className="w-12 h-12 rounded-full object-cover"
                />
                <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-sm truncate">
                        {player.display_name}
                    </h4>
                    <p className="text-xs text-gray-500">{player.position}</p>

                    <div className="mt-2 flex items-center gap-2">
                        <div className="flex items-center gap-1">
                            <TrendingUp className="h-3 w-3 text-green-600" />
                            <span className="text-sm font-semibold text-green-600">
                                {player.average_score.toFixed(1)}
                            </span>
                        </div>
                        <span className="text-xs text-gray-400">
                            {player.total_games} matchs
                        </span>
                    </div>

                    {player.is_injured && (
                        <Badge variant="destructive" className="mt-2 text-xs">
                            🚑 Blessé
                        </Badge>
                    )}
                </div>
            </div>
        </Card>
    );
}