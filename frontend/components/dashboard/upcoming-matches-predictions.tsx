'use client';

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { footballApi } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
    TrendingUp,
    Trophy,
    Calendar,
    RefreshCw,
    AlertCircle,
} from 'lucide-react';
import { formatDate } from '@/lib/utils';
import Link from 'next/link';
import { useState } from 'react';

export function UpcomingMatchesPredictions() {
    const queryClient = useQueryClient();
    const [isRefreshing, setIsRefreshing] = useState(false);

    const { data, isLoading, error } = useQuery({
        queryKey: ['dashboard-predictions'],
        queryFn: () => footballApi.getDashboardPredictions(),
        refetchInterval: 3600000, // Rafraîchir toutes les heures
    });

    // Handler pour le bouton Rafraîchir
    const handleRefresh = async () => {
        setIsRefreshing(true);
        try {
            await queryClient.invalidateQueries({ queryKey: ['dashboard-predictions'] });
            await queryClient.refetchQueries({ queryKey: ['dashboard-predictions'] });
        } catch (error) {
            console.error('Erreur lors du rafraîchissement:', error);
        } finally {
            setIsRefreshing(false);
        }
    };

    if (isLoading) {
        return (
            <Card className="p-6">
                <div className="space-y-4">
                    <Skeleton className="h-8 w-64" />
                    <div className="grid gap-4">
                        {[...Array(3)].map((_, i) => (
                            <Skeleton key={i} className="h-32" />
                        ))}
                    </div>
                </div>
            </Card>
        );
    }

    if (error || !data?.success) {
        return null; // Ne rien afficher si erreur
    }

    const predictions = data.predictions || [];

    if (predictions.length === 0) {
        return null; // Rien à afficher
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <Trophy className="h-6 w-6 text-yellow-500" />
                        Prochains Matchs & Prédictions
                    </h2>
                    <p className="text-gray-500 mt-1">
                        Optimise ta lineup avec les matchs recommandés
                    </p>
                </div>
                
                {/* Bouton Rafraîchir */}
                <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRefresh}
                    disabled={isRefreshing}
                    className="gap-2"
                >
                    <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                    Rafraîchir
                </Button>
            </div>

            {/* Grille de prédictions */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {predictions.slice(0, 6).map((item: any) => {
                    const player = item.player;
                    const match = item.match;
                    const prediction = item.prediction;
                    const playability = item.playability_score;
                    const hasPredict = item.has_prediction;

                    const fixture = match?.fixture || {};
                    const teams = match?.teams || {};
                    const league = match?.league || {};

                    const homeTeam = teams.home || {};
                    const awayTeam = teams.away || {};
                    const isHome = homeTeam.id === player.club;

                    return (
                        <Card
                            key={player.id}
                            className={`overflow-hidden transition-all hover:shadow-xl ${
                                playability?.color === 'green'
                                    ? 'border-l-4 border-l-green-500'
                                    : playability?.color === 'blue'
                                    ? 'border-l-4 border-l-blue-500'
                                    : playability?.color === 'orange'
                                    ? 'border-l-4 border-l-orange-500'
                                    : 'border-l-4 border-l-red-500'
                            }`}
                        >
                            {/* Header avec joueur */}
                            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4">
                                <Link
                                    href={`/players/${player.id}`}
                                    className="flex items-center gap-3 group"
                                >
                                    <img
                                        src={
                                            player.image ||
                                            `https://ui-avatars.com/api/?name=${encodeURIComponent(
                                                player.name
                                            )}&background=random`
                                        }
                                        alt={player.name}
                                        className="w-12 h-12 rounded-full object-cover border-2 border-white shadow-md group-hover:scale-110 transition-transform"
                                        onError={(e) => {
                                            e.currentTarget.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(
                                                player.name
                                            )}&background=random`;
                                        }}
                                    />
                                    <div className="flex-1 min-w-0">
                                        <h3 className="font-bold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                                            {player.name}
                                        </h3>
                                        <p className="text-sm text-gray-600">
                                            {player.position} • {player.club}
                                        </p>
                                    </div>
                                </Link>
                            </div>

                            {/* Match Info */}
                            <div className="p-4 space-y-3">
                                {/* Date & Compétition */}
                                <div className="flex items-center justify-between text-sm">
                                    <div className="flex items-center gap-1 text-gray-600">
                                        <Calendar className="h-3 w-3" />
                                        <span>{formatDate(fixture.date)}</span>
                                    </div>
                                    <Badge variant="outline" className="text-xs">
                                        {league.name}
                                    </Badge>
                                </div>

                                {/* Match */}
                                <div className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center gap-2 flex-1">
                                        <img
                                            src={homeTeam.logo}
                                            alt={homeTeam.name}
                                            className="w-6 h-6"
                                        />
                                        <span className="font-medium text-sm truncate">
                                            {homeTeam.name}
                                        </span>
                                    </div>
                                    <span className="text-gray-400 font-bold mx-2">vs</span>
                                    <div className="flex items-center gap-2 flex-1 justify-end">
                                        <span className="font-medium text-sm truncate">
                                            {awayTeam.name}
                                        </span>
                                        <img
                                            src={awayTeam.logo}
                                            alt={awayTeam.name}
                                            className="w-6 h-6"
                                        />
                                    </div>
                                </div>

                                {/* Playability Score */}
                                {hasPredict && playability && (
                                    <div className="space-y-2">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm font-medium text-gray-600">
                                                Score de jouabilité
                                            </span>
                                            <div
                                                className={`text-2xl font-bold ${
                                                    playability.color === 'green'
                                                        ? 'text-green-600'
                                                        : playability.color === 'blue'
                                                        ? 'text-blue-600'
                                                        : playability.color === 'orange'
                                                        ? 'text-orange-600'
                                                        : 'text-red-600'
                                                }`}
                                            >
                                                {playability.score}/10
                                            </div>
                                        </div>

                                        {/* Barre de progression */}
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className={`h-2 rounded-full transition-all ${
                                                    playability.color === 'green'
                                                        ? 'bg-green-500'
                                                        : playability.color === 'blue'
                                                        ? 'bg-blue-500'
                                                        : playability.color === 'orange'
                                                        ? 'bg-orange-500'
                                                        : 'bg-red-500'
                                                }`}
                                                style={{ width: `${playability.score * 10}%` }}
                                            />
                                        </div>

                                        {/* Conseil */}
                                        <div
                                            className={`text-xs font-medium text-center py-2 rounded-lg ${
                                                playability.color === 'green'
                                                    ? 'bg-green-50 text-green-700'
                                                    : playability.color === 'blue'
                                                    ? 'bg-blue-50 text-blue-700'
                                                    : playability.color === 'orange'
                                                    ? 'bg-orange-50 text-orange-700'
                                                    : 'bg-red-50 text-red-700'
                                            }`}
                                        >
                                            {playability.advice}
                                        </div>

                                        {/* Raisons */}
                                        {playability.reasons &&
                                            playability.reasons.length > 0 && (
                                                <div className="space-y-1 pt-2 border-t border-gray-100">
                                                    {playability.reasons
                                                        .slice(0, 2)
                                                        .map((reason: string, idx: number) => (
                                                            <p
                                                                key={idx}
                                                                className="text-xs text-gray-600"
                                                            >
                                                                • {reason}
                                                            </p>
                                                        ))}
                                                </div>
                                            )}
                                    </div>
                                )}

                                {/* Pas de prédiction disponible */}
                                {!hasPredict && (
                                    <div className="text-center py-4 text-sm text-gray-500">
                                        <AlertCircle className="h-4 w-4 mx-auto mb-1" />
                                        Prédictions non disponibles
                                    </div>
                                )}
                            </div>
                        </Card>
                    );
                })}
            </div>
        </div>
    );
}