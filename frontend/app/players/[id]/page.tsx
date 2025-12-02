'use client';

import { useQuery } from '@tanstack/react-query';
import { playersApi, injuriesApi } from '@/lib/api';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton, Alert, AlertDescription } from '@/components/ui/extras';
import {
    ArrowLeft,
    MapPin,
    Calendar,
    TrendingUp,
    Activity,
    HeartPulse,
    Edit,
    Trash2,
    ExternalLink,
} from 'lucide-react';
import {
    formatScore,
    formatDate,
    formatRelativeTime,
    translatePosition,
    getPositionBadge,
    getFlagEmoji,
    getPlayerAvatar,
    formatNumber,
    translateSeverity,
    getSeverityColor,
} from '@/lib/utils';

export default function PlayerDetailPage() {
    const params = useParams();
    const router = useRouter();
    const playerId = parseInt(params.id as string);

    // Récupérer les infos du joueur
    const {
        data: player,
        isLoading: playerLoading,
        error: playerError,
    } = useQuery({
        queryKey: ['player', playerId],
        queryFn: () => playersApi.getById(playerId),
        enabled: !!playerId,
    });

    // Récupérer les blessures du joueur
    const {
        data: injuriesData,
        isLoading: injuriesLoading,
    } = useQuery({
        queryKey: ['player-injuries', playerId],
        queryFn: () => injuriesApi.getAll({ player_id: playerId }),
        enabled: !!playerId,
    });

    if (playerError) {
        return (
            <div className="space-y-6">
                <Button variant="ghost" onClick={() => router.back()}>
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Retour
                </Button>

                <Alert variant="destructive">
                    <AlertDescription>
                        Impossible de charger ce joueur. Il n'existe peut-être pas.
                    </AlertDescription>
                </Alert>
            </div>
        );
    }

    if (playerLoading) {
        return (
            <div className="space-y-6">
                <Skeleton className="h-10 w-32" />
                <div className="grid gap-6 lg:grid-cols-3">
                    <div className="lg:col-span-2 space-y-6">
                        <Skeleton className="h-64" />
                        <Skeleton className="h-96" />
                    </div>
                    <div className="space-y-6">
                        <Skeleton className="h-48" />
                        <Skeleton className="h-64" />
                    </div>
                </div>
            </div>
        );
    }

    if (!player) {
        return null;
    }

    const injuries = injuriesData?.injuries || [];
    const activeInjuries = injuries.filter((i) => i.is_active);
    const pastInjuries = injuries.filter((i) => !i.is_active);

    return (
        <div className="space-y-6">
            {/* Header avec retour */}
            <div className="flex items-center justify-between">
                <Button variant="ghost" onClick={() => router.back()}>
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Retour aux joueurs
                </Button>

                <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                        <Edit className="h-4 w-4 mr-2" />
                        Modifier
                    </Button>
                    <Button variant="outline" size="sm">
                        <Trash2 className="h-4 w-4 mr-2" />
                        Supprimer
                    </Button>
                </div>
            </div>

            {/* Contenu principal */}
            <div className="grid gap-6 lg:grid-cols-3">
                {/* Colonne principale */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Carte profil */}
                    <Card className="p-6">
                        <div className="flex items-start gap-6">
                            {/* Avatar */}
                            <img
                                src={getPlayerAvatar(player.image_url, player.display_name)}
                                alt={player.display_name || 'Player'}
                                className="w-32 h-32 rounded-full object-cover"
                            />

                            {/* Infos principales */}
                            <div className="flex-1">
                                <div className="flex items-start justify-between mb-2">
                                    <div>
                                        <h1 className="text-3xl font-bold">{player.display_name}</h1>
                                        <p className="text-lg text-gray-500">
                                            {player.first_name} {player.last_name}
                                        </p>
                                    </div>

                                    {player.is_injured && (
                                        <Badge className="bg-red-100 text-red-800 border-red-200">
                                            <HeartPulse className="h-4 w-4 mr-1" />
                                            Blessé
                                        </Badge>
                                    )}
                                </div>

                                <div className="flex flex-wrap gap-2 mb-4">
                                    <Badge className={getPositionBadge(player.position)}>
                                        {translatePosition(player.position)}
                                    </Badge>

                                    {player.is_active ? (
                                        <Badge className="bg-green-100 text-green-800 border-green-200">
                                            Actif
                                        </Badge>
                                    ) : (
                                        <Badge className="bg-gray-100 text-gray-800 border-gray-200">
                                            Inactif
                                        </Badge>
                                    )}
                                </div>

                                {/* Détails */}
                                <div className="grid grid-cols-2 gap-3 text-sm">
                                    <div className="flex items-center gap-2">
                                        <MapPin className="h-4 w-4 text-gray-400" />
                                        <span>
                                            {player.country_code && getFlagEmoji(player.country_code)}{' '}
                                            {player.country}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Calendar className="h-4 w-4 text-gray-400" />
                                        <span>
                                            {player.age} ans {player.birth_date && `(${formatDate(player.birth_date)})`}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Activity className="h-4 w-4 text-gray-400" />
                                        <span className="font-medium">{player.club_name}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <ExternalLink className="h-4 w-4 text-gray-400" />
                                        {player.sorare_id && (
                                            <Link
                                                href={`https://sorare.com/football/players/${player.sorare_id}`}
                                                target="_blank"
                                                className="text-blue-600 hover:underline"
                                            >
                                                Voir sur Sorare
                                            </Link>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Statut de blessure actuel */}
                        {player.is_injured && player.injury_status && (
                            <div className="mt-6 pt-6 border-t border-gray-100">
                                <div className="flex items-start gap-3 p-4 bg-red-50 rounded-lg">
                                    <HeartPulse className="h-5 w-5 text-red-600 mt-0.5" />
                                    <div>
                                        <p className="font-semibold text-red-900">Blessure actuelle</p>
                                        <p className="text-sm text-red-700">{player.injury_status}</p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </Card>

                    {/* Statistiques détaillées */}
                    <Card className="p-6">
                        <h2 className="text-xl font-bold mb-4">Statistiques</h2>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                            <div className="text-center p-4 bg-blue-50 rounded-lg">
                                <TrendingUp className="h-6 w-6 mx-auto mb-2 text-blue-600" />
                                <p className="text-sm text-gray-600">Score moyen</p>
                                <p className="text-2xl font-bold text-blue-600">
                                    {formatScore(player.average_score)}
                                </p>
                            </div>

                            <div className="text-center p-4 bg-green-50 rounded-lg">
                                <Activity className="h-6 w-6 mx-auto mb-2 text-green-600" />
                                <p className="text-sm text-gray-600">Total matchs</p>
                                <p className="text-2xl font-bold text-green-600">
                                    {formatNumber(player.total_games)}
                                </p>
                            </div>

                            <div className="text-center p-4 bg-purple-50 rounded-lg">
                                <Calendar className="h-6 w-6 mx-auto mb-2 text-purple-600" />
                                <p className="text-sm text-gray-600">Saison</p>
                                <p className="text-2xl font-bold text-purple-600">
                                    {formatNumber(player.season_games)}
                                </p>
                            </div>

                            <div className="text-center p-4 bg-orange-50 rounded-lg">
                                <TrendingUp className="h-6 w-6 mx-auto mb-2 text-orange-600" />
                                <p className="text-sm text-gray-600">Dernier match</p>
                                <p className="text-2xl font-bold text-orange-600">
                                    {player.last_game_score !== null
                                        ? formatScore(player.last_game_score)
                                        : '-'}
                                </p>
                            </div>
                        </div>
                    </Card>

                    {/* Historique des blessures */}
                    {injuries.length > 0 && (
                        <Card className="p-6">
                            <h2 className="text-xl font-bold mb-4">Historique des blessures</h2>

                            {/* Blessures actives */}
                            {activeInjuries.length > 0 && (
                                <div className="mb-6">
                                    <h3 className="text-sm font-semibold text-red-600 mb-3">
                                        Blessures actives ({activeInjuries.length})
                                    </h3>
                                    <div className="space-y-3">
                                        {activeInjuries.map((injury) => (
                                            <div
                                                key={injury.id}
                                                className="p-4 bg-red-50 border border-red-200 rounded-lg"
                                            >
                                                <div className="flex items-start justify-between mb-2">
                                                    <div>
                                                        <p className="font-semibold text-red-900">
                                                            {injury.injury_type || 'Blessure'}
                                                        </p>
                                                        <p className="text-sm text-red-700">
                                                            {injury.injury_description}
                                                        </p>
                                                    </div>
                                                    {injury.severity && (
                                                        <Badge className={getSeverityColor(injury.severity)}>
                                                            {translateSeverity(injury.severity)}
                                                        </Badge>
                                                    )}
                                                </div>

                                                <div className="grid grid-cols-2 gap-2 text-xs text-red-700 mt-3">
                                                    <div>
                                                        <span className="font-medium">Date: </span>
                                                        {formatDate(injury.injury_date)}
                                                    </div>
                                                    <div>
                                                        <span className="font-medium">Retour prévu: </span>
                                                        {injury.expected_return_date
                                                            ? formatDate(injury.expected_return_date)
                                                            : 'Indéterminé'}
                                                    </div>
                                                </div>

                                                {injury.source && (
                                                    <p className="text-xs text-red-600 mt-2">
                                                        Source: {injury.source}
                                                    </p>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Blessures passées */}
                            {pastInjuries.length > 0 && (
                                <div>
                                    <h3 className="text-sm font-semibold text-gray-600 mb-3">
                                        Historique ({pastInjuries.length})
                                    </h3>
                                    <div className="space-y-2">
                                        {pastInjuries.map((injury) => (
                                            <div
                                                key={injury.id}
                                                className="p-3 bg-gray-50 border border-gray-200 rounded-lg"
                                            >
                                                <div className="flex items-start justify-between">
                                                    <div className="flex-1">
                                                        <p className="font-medium text-sm">
                                                            {injury.injury_type || 'Blessure'}
                                                        </p>
                                                        <p className="text-xs text-gray-600">
                                                            {injury.injury_description}
                                                        </p>
                                                    </div>
                                                    {injury.severity && (
                                                        <Badge variant="outline" className="text-xs">
                                                            {translateSeverity(injury.severity)}
                                                        </Badge>
                                                    )}
                                                </div>
                                                <p className="text-xs text-gray-500 mt-2">
                                                    {formatDate(injury.injury_date)} →{' '}
                                                    {injury.actual_return_date
                                                        ? formatDate(injury.actual_return_date)
                                                        : 'Retour non enregistré'}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </Card>
                    )}
                </div>

                {/* Sidebar droite */}
                <div className="space-y-6">
                    {/* Infos rapides */}
                    <Card className="p-6">
                        <h3 className="font-semibold mb-4">Informations</h3>

                        <div className="space-y-3 text-sm">
                            <div>
                                <p className="text-gray-500">ID Sorare</p>
                                <p className="font-medium">{player.sorare_id || '-'}</p>
                            </div>

                            <div>
                                <p className="text-gray-500">Club</p>
                                <p className="font-medium">{player.club_name || '-'}</p>
                            </div>

                            <div>
                                <p className="text-gray-500">Position</p>
                                <p className="font-medium">{translatePosition(player.position)}</p>
                            </div>

                            <div>
                                <p className="text-gray-500">Nationalité</p>
                                <p className="font-medium">
                                    {player.country_code && getFlagEmoji(player.country_code)}{' '}
                                    {player.country || '-'}
                                </p>
                            </div>

                            <div>
                                <p className="text-gray-500">Âge</p>
                                <p className="font-medium">{player.age || '-'} ans</p>
                            </div>
                        </div>
                    </Card>

                    {/* Dernière mise à jour */}
                    <Card className="p-6">
                        <h3 className="font-semibold mb-4">Synchronisation</h3>

                        <div className="space-y-3 text-sm">
                            <div>
                                <p className="text-gray-500">Dernière sync Sorare</p>
                                <p className="font-medium">
                                    {player.last_sorare_sync
                                        ? formatRelativeTime(player.last_sorare_sync)
                                        : 'Jamais'}
                                </p>
                            </div>

                            <div>
                                <p className="text-gray-500">Mis à jour</p>
                                <p className="font-medium">
                                    {formatRelativeTime(player.updated_at)}
                                </p>
                            </div>

                            <div>
                                <p className="text-gray-500">Créé</p>
                                <p className="font-medium">
                                    {formatDate(player.created_at)}
                                </p>
                            </div>
                        </div>

                        <Button className="w-full mt-4" size="sm">
                            Synchroniser maintenant
                        </Button>
                    </Card>
                </div>
            </div>
        </div>
    );
}