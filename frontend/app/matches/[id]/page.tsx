"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import axios from "axios";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
    ArrowLeft,
    Calendar,
    Clock,
    MapPin,
    TrendingUp,
    Trophy,
    AlertCircle,
    Activity,
} from "lucide-react";
import type { Player } from "@/app/types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface MatchDetail {
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
    last_result?: {
        home_score: number;
        away_score: number;
        date: string;
    };
}

export default function MatchDetailPage() {
    const params = useParams();
    const router = useRouter();
    const matchId = parseInt(params.id as string);

    const { data: match, isLoading } = useQuery<MatchDetail>({
        queryKey: ["match-detail", matchId],
        queryFn: async () => {
            const response = await axios.get(
                `${API_URL}/api/v1/players/match/${matchId}/details`
            );
            return response.data;
        },
    });

    const formatMatchDate = (dateString: string) => {
        const date = new Date(dateString);
        return {
            fullDate: date.toLocaleDateString("fr-FR", {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric",
            }),
            time: date.toLocaleTimeString("fr-FR", {
                hour: "2-digit",
                minute: "2-digit",
            }),
        };
    };

    if (isLoading) {
        return (
            <div className="space-y-6">
                <Skeleton className="h-12 w-48" />
                <Skeleton className="h-64" />
                <div className="grid md:grid-cols-2 gap-6">
                    <Skeleton className="h-96" />
                    <Skeleton className="h-96" />
                </div>
            </div>
        );
    }

    if (!match) {
        return (
            <div className="space-y-6">
                <Button variant="ghost" onClick={() => router.back()}>
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Retour
                </Button>
                <Card className="p-12 text-center">
                    <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Match non trouvé</p>
                </Card>
            </div>
        );
    }

    const { fullDate, time } = formatMatchDate(match.date);
    const totalPlayers = match.home_players.length + match.away_players.length;
    const homeWon =
        match.last_result && match.last_result.home_score > match.last_result.away_score;
    const awayWon =
        match.last_result && match.last_result.away_score > match.last_result.home_score;
    const draw =
        match.last_result && match.last_result.home_score === match.last_result.away_score;

    return (
        <div className="space-y-6">
            {/* Header avec retour */}
            <Button variant="ghost" onClick={() => router.back()}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Retour au dashboard
            </Button>

            {/* Carte principale du match */}
            <Card className="overflow-hidden">
                {/* Bandeau supérieur coloré */}
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
                    <div className="flex items-center justify-between mb-4">
                        <Badge className="bg-white/20 text-white border-white/30">
                            {match.league}
                        </Badge>
                        <div className="flex items-center gap-2 text-sm">
                            <MapPin className="h-4 w-4" />
                            <span>{match.venue || "Stade à confirmer"}</span>
                        </div>
                    </div>

                    {/* Affrontement */}
                    <div className="flex items-center justify-between gap-8">
                        {/* Équipe domicile */}
                        <div className="flex-1 flex flex-col items-center">
                            {match.home_logo && (
                                <div className="relative mb-4">
                                    <img
                                        src={match.home_logo}
                                        alt={match.home_team}
                                        className="w-24 h-24 object-contain drop-shadow-2xl"
                                    />
                                    {homeWon && (
                                        <Trophy className="absolute -top-2 -right-2 h-8 w-8 text-yellow-300 fill-yellow-300" />
                                    )}
                                </div>
                            )}
                            <h2 className="text-2xl font-bold text-center mb-2">
                                {match.home_team}
                            </h2>
                            <Badge className="bg-blue-500/30 text-white border-white/30">
                                {match.home_players.length} joueur
                                {match.home_players.length > 1 ? "s" : ""}
                            </Badge>
                        </div>

                        {/* Centre - VS + Date */}
                        <div className="text-center px-8">
                            <p className="text-5xl font-black mb-4 drop-shadow-lg">VS</p>
                            <div className="space-y-2">
                                <div className="flex items-center gap-2 justify-center">
                                    <Calendar className="h-4 w-4" />
                                    <span className="text-sm font-medium">{fullDate}</span>
                                </div>
                                <div className="flex items-center gap-2 justify-center">
                                    <Clock className="h-4 w-4" />
                                    <span className="text-xl font-bold">{time}</span>
                                </div>
                            </div>
                        </div>

                        {/* Équipe extérieur */}
                        <div className="flex-1 flex flex-col items-center">
                            {match.away_logo && (
                                <div className="relative mb-4">
                                    <img
                                        src={match.away_logo}
                                        alt={match.away_team}
                                        className="w-24 h-24 object-contain drop-shadow-2xl"
                                    />
                                    {awayWon && (
                                        <Trophy className="absolute -top-2 -right-2 h-8 w-8 text-yellow-300 fill-yellow-300" />
                                    )}
                                </div>
                            )}
                            <h2 className="text-2xl font-bold text-center mb-2">
                                {match.away_team}
                            </h2>
                            <Badge className="bg-purple-500/30 text-white border-white/30">
                                {match.away_players.length} joueur
                                {match.away_players.length > 1 ? "s" : ""}
                            </Badge>
                        </div>
                    </div>

                    {/* Dernier résultat */}
                    {match.last_result && (
                        <div className="mt-6 pt-6 border-t border-white/20">
                            <p className="text-sm text-white/80 text-center mb-2">
                                Dernier affrontement
                            </p>
                            <div className="flex items-center justify-center gap-4">
                                <div
                                    className={`px-6 py-3 rounded-lg font-bold text-2xl ${
                                        homeWon
                                            ? "bg-green-500/30 border-2 border-green-400"
                                            : "bg-white/10"
                                    }`}
                                >
                                    {match.last_result.home_score}
                                </div>
                                <span className="text-xl">-</span>
                                <div
                                    className={`px-6 py-3 rounded-lg font-bold text-2xl ${
                                        awayWon
                                            ? "bg-green-500/30 border-2 border-green-400"
                                            : "bg-white/10"
                                    }`}
                                >
                                    {match.last_result.away_score}
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Statistiques */}
                <div className="p-6 bg-gray-50 border-t border-gray-200">
                    <div className="flex items-center justify-around text-center">
                        <div>
                            <p className="text-3xl font-bold text-blue-600">{totalPlayers}</p>
                            <p className="text-sm text-gray-600">Joueurs concernés</p>
                        </div>
                        <div className="h-12 w-px bg-gray-300"></div>
                        <div>
                            <p className="text-3xl font-bold text-green-600">
                                {(
                                    [...match.home_players, ...match.away_players].reduce(
                                        (sum, p) => sum + p.average_score,
                                        0
                                    ) / totalPlayers
                                ).toFixed(1)}
                            </p>
                            <p className="text-sm text-gray-600">Score moyen</p>
                        </div>
                        <div className="h-12 w-px bg-gray-300"></div>
                        <div>
                            <p className="text-3xl font-bold text-red-600">
                                {
                                    [...match.home_players, ...match.away_players].filter(
                                        (p) => p.is_injured
                                    ).length
                                }
                            </p>
                            <p className="text-sm text-gray-600">Blessés</p>
                        </div>
                    </div>
                </div>
            </Card>

            {/* Grille des joueurs */}
            <div className="grid md:grid-cols-2 gap-6">
                {/* Joueurs domicile */}
                <div>
                    <div className="flex items-center gap-3 mb-4">
                        {match.home_logo && (
                            <img src={match.home_logo} alt={match.home_team} className="w-8 h-8" />
                        )}
                        <h3 className="text-xl font-bold">{match.home_team}</h3>
                        <Badge variant="outline">{match.home_players.length}</Badge>
                    </div>
                    <div className="space-y-3">
                        {match.home_players.map((player) => (
                            <PlayerCard key={player.id} player={player} />
                        ))}
                    </div>
                </div>

                {/* Joueurs extérieur */}
                <div>
                    <div className="flex items-center gap-3 mb-4">
                        {match.away_logo && (
                            <img src={match.away_logo} alt={match.away_team} className="w-8 h-8" />
                        )}
                        <h3 className="text-xl font-bold">{match.away_team}</h3>
                        <Badge variant="outline">{match.away_players.length}</Badge>
                    </div>
                    <div className="space-y-3">
                        {match.away_players.map((player) => (
                            <PlayerCard key={player.id} player={player} />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

// Composant carte joueur
function PlayerCard({ player }: { player: Player }) {
    return (
        <Card className="p-4 hover:shadow-lg transition-all hover:border-blue-300 border-2">
            <div className="flex items-start gap-4">
                <img
                    src={
                        player.image_url ||
                        `https://ui-avatars.com/api/?name=${encodeURIComponent(
                            player.display_name || "Player"
                        )}&background=random`
                    }
                    alt={player.display_name || "Player"}
                    className="w-16 h-16 rounded-full object-cover border-2 border-gray-200"
                />
                <div className="flex-1">
                    <h4 className="font-bold text-lg">{player.display_name}</h4>
                    <p className="text-sm text-gray-600">{player.position}</p>

                    <div className="mt-3 flex items-center gap-4">
                        <div className="flex items-center gap-1">
                            <TrendingUp className="h-4 w-4 text-green-600" />
                            <span className="text-lg font-bold text-green-600">
                                {player.average_score.toFixed(1)}
                            </span>
                        </div>
                        <div className="flex items-center gap-1 text-gray-600">
                            <Activity className="h-4 w-4" />
                            <span className="text-sm">{player.total_games} matchs</span>
                        </div>
                    </div>

                    {player.is_injured && (
                        <Badge variant="destructive" className="mt-2">
                            🚑 Blessé
                        </Badge>
                    )}
                </div>
            </div>
        </Card>
    );
}