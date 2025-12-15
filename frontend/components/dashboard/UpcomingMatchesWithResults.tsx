"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import axios from "axios";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, Clock, Loader2, ChevronRight, Trophy } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface MatchWithResult {
    id: number;
    date: string;
    home_team: string;
    away_team: string;
    home_logo?: string;
    away_logo?: string;
    league: string;
    venue?: string;
    player_count: number;
    // Dernier résultat
    last_result?: {
        home_score: number;
        away_score: number;
        date: string;
    };
}

export default function UpcomingMatchesWithResults() {
    const router = useRouter();

    const { data: matches, isLoading } = useQuery<MatchWithResult[]>({
        queryKey: ["upcoming-matches-results"],
        queryFn: async () => {
            const response = await axios.get(`${API_URL}/api/v1/players/upcoming-matches-with-results`);
            return response.data.matches;
        },
        refetchInterval: 5 * 60 * 1000,
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

    const formatLastResult = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) return "Aujourd'hui";
        if (diffDays === 1) return "Hier";
        if (diffDays < 7) return `Il y a ${diffDays}j`;
        return date.toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
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

    const totalPlayers = matches.reduce((sum, match) => sum + match.player_count, 0);

    return (
        <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-xl font-bold">📅 Prochains matchs</h2>
                    <p className="text-sm text-gray-500 mt-1">
                        {matches.length} match{matches.length > 1 ? "s" : ""} • {totalPlayers} joueur
                        {totalPlayers > 1 ? "s" : ""} concerné{totalPlayers > 1 ? "s" : ""}
                    </p>
                </div>
            </div>

            <div className="space-y-3">
                {matches.map((match) => {
                    const { date, time } = formatMatchDate(match.date);
                    const homeWon = match.last_result && match.last_result.home_score > match.last_result.away_score;
                    const awayWon = match.last_result && match.last_result.away_score > match.last_result.home_score;
                    const draw = match.last_result && match.last_result.home_score === match.last_result.away_score;

                    return (
                        <button
                            key={match.id}
                            onClick={() => router.push(`/matches/${match.id}`)}
                            className="w-full group"
                        >
                            <Card className="p-4 hover:shadow-xl transition-all hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 border-2 hover:border-blue-300">
                                <div className="flex items-center justify-between gap-4">
                                    {/* Équipe domicile */}
                                    <div className="flex-1 flex items-center gap-3">
                                        {match.home_logo && (
                                            <div className="relative">
                                                <img
                                                    src={match.home_logo}
                                                    alt={match.home_team}
                                                    className="w-12 h-12 object-contain"
                                                />
                                                {homeWon && (
                                                    <Trophy className="absolute -top-1 -right-1 h-4 w-4 text-yellow-500 fill-yellow-500" />
                                                )}
                                            </div>
                                        )}
                                        <div className="text-left flex-1">
                                            <p className="font-bold text-gray-900 text-lg">
                                                {match.home_team}
                                            </p>
                                            {match.last_result && (
                                                <div className="flex items-center gap-2 mt-1">
                                                    <Badge
                                                        variant="outline"
                                                        className={`text-xs ${
                                                            homeWon
                                                                ? "bg-green-100 text-green-700 border-green-300"
                                                                : draw
                                                                ? "bg-gray-100 text-gray-700 border-gray-300"
                                                                : "bg-red-100 text-red-700 border-red-300"
                                                        }`}
                                                    >
                                                        Dernier: {match.last_result.home_score}-
                                                        {match.last_result.away_score}
                                                    </Badge>
                                                    <span className="text-xs text-gray-500">
                                                        {formatLastResult(match.last_result.date)}
                                                    </span>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Centre - Date et VS */}
                                    <div className="text-center px-6 py-2 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                                        <p className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                                            VS
                                        </p>
                                        <div className="flex items-center gap-1 text-xs text-gray-600 mt-1">
                                            <Calendar className="h-3 w-3" />
                                            <span className="font-medium">{date}</span>
                                        </div>
                                        <div className="flex items-center gap-1 text-xs text-gray-600">
                                            <Clock className="h-3 w-3" />
                                            <span className="font-medium">{time}</span>
                                        </div>
                                    </div>

                                    {/* Équipe extérieur */}
                                    <div className="flex-1 flex items-center gap-3 justify-end">
                                        <div className="text-right flex-1">
                                            <p className="font-bold text-gray-900 text-lg">
                                                {match.away_team}
                                            </p>
                                            {match.last_result && (
                                                <div className="flex items-center gap-2 mt-1 justify-end">
                                                    <span className="text-xs text-gray-500">
                                                        {formatLastResult(match.last_result.date)}
                                                    </span>
                                                    <Badge
                                                        variant="outline"
                                                        className={`text-xs ${
                                                            awayWon
                                                                ? "bg-green-100 text-green-700 border-green-300"
                                                                : draw
                                                                ? "bg-gray-100 text-gray-700 border-gray-300"
                                                                : "bg-red-100 text-red-700 border-red-300"
                                                        }`}
                                                    >
                                                        Dernier: {match.last_result.away_score}-
                                                        {match.last_result.home_score}
                                                    </Badge>
                                                </div>
                                            )}
                                        </div>
                                        {match.away_logo && (
                                            <div className="relative">
                                                <img
                                                    src={match.away_logo}
                                                    alt={match.away_team}
                                                    className="w-12 h-12 object-contain"
                                                />
                                                {awayWon && (
                                                    <Trophy className="absolute -top-1 -right-1 h-4 w-4 text-yellow-500 fill-yellow-500" />
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    {/* Badge joueurs + Flèche */}
                                    <div className="flex items-center gap-3 ml-2">
                                        <Badge className="bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0 px-3 py-1">
                                            {match.player_count} joueur{match.player_count > 1 ? "s" : ""}
                                        </Badge>
                                        <ChevronRight className="h-6 w-6 text-gray-400 group-hover:text-purple-600 group-hover:translate-x-2 transition-all" />
                                    </div>
                                </div>

                                {/* Ligue */}
                                <div className="mt-3 pt-3 border-t border-gray-200">
                                    <div className="flex items-center justify-between text-xs">
                                        <span className="text-gray-600">
                                            {match.league}
                                            {match.venue && ` • ${match.venue}`}
                                        </span>
                                        <span className="text-blue-600 font-medium">
                                            Voir les joueurs →
                                        </span>
                                    </div>
                                </div>
                            </Card>
                        </button>
                    );
                })}
            </div>
        </Card>
    );
}