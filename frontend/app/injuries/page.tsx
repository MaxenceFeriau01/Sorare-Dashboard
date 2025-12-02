'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { injuriesApi, playersApi } from '@/lib/api';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton, Alert, AlertDescription } from '@/components/ui/extras';
import {
    AlertCircle,
    Search,
    Filter,
    HeartPulse,
    Plus,
    Calendar,
    Clock,
    TrendingUp,
    User,
    ExternalLink,
} from 'lucide-react';
import {
    formatDate,
    formatRelativeTime,
    translateSeverity,
    getSeverityColor,
    getPlayerAvatar,
    formatNumber,
} from '@/lib/utils';
import type { Injury, Player } from '@/types/api';

export default function InjuriesPage() {
    // États pour les filtres
    const [statusFilter, setStatusFilter] = useState<string>('active');
    const [severityFilter, setSeverityFilter] = useState<string>('all');
    const [searchTerm, setSearchTerm] = useState('');

    // Récupérer toutes les blessures
    const {
        data: injuriesData,
        isLoading: injuriesLoading,
        error: injuriesError,
    } = useQuery({
        queryKey: ['injuries-list'],
        queryFn: () => injuriesApi.getAll({ limit: 500 }),
    });

    // Récupérer tous les joueurs pour avoir les noms
    const { data: playersData } = useQuery({
        queryKey: ['players-for-injuries'],
        queryFn: () => playersApi.getAll({ limit: 500 }),
    });

    // Créer un map des joueurs par ID
    const playersMap = new Map<number, Player>();
    playersData?.players.forEach((player) => {
        playersMap.set(player.id, player);
    });

    // Filtrer les blessures
    const filteredInjuries = injuriesData?.injuries.filter((injury) => {
        const player = playersMap.get(injury.player_id);

        // Filtre de statut
        const matchesStatus =
            statusFilter === 'all' ||
            (statusFilter === 'active' && injury.is_active) ||
            (statusFilter === 'past' && !injury.is_active);

        // Filtre de gravité
        const matchesSeverity =
            severityFilter === 'all' || injury.severity === severityFilter;

        // Filtre de recherche
        const matchesSearch =
            !searchTerm ||
            player?.display_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            injury.injury_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            injury.injury_description?.toLowerCase().includes(searchTerm.toLowerCase());

        return matchesStatus && matchesSeverity && matchesSearch;
    }) || [];

    // Stats
    const activeInjuries = injuriesData?.injuries.filter((i) => i.is_active) || [];
    const pastInjuries = injuriesData?.injuries.filter((i) => !i.is_active) || [];
    const severeInjuries = injuriesData?.injuries.filter(
        (i) => i.severity === 'Severe' && i.is_active
    ) || [];

    if (injuriesError) {
        return (
            <div className="space-y-6">
                <div>
                    <h1 className="text-3xl font-bold">Blessures</h1>
                    <p className="text-gray-500 mt-1">Suivi des blessures de tes joueurs</p>
                </div>

                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                        Impossible de charger les blessures. Vérifie que le backend est lancé.
                    </AlertDescription>
                </Alert>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Blessures</h1>
                    <p className="text-gray-500 mt-1">
                        {filteredInjuries.length} blessure{filteredInjuries.length > 1 ? 's' : ''}{' '}
                        trouvée{filteredInjuries.length > 1 ? 's' : ''}
                    </p>
                </div>

                <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Ajouter une blessure
                </Button>
            </div>

            {/* Stats rapides */}
            <div className="grid gap-6 md:grid-cols-3">
                <Card className="p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-500">Blessures actives</p>
                            <p className="text-3xl font-bold text-red-600 mt-2">
                                {formatNumber(activeInjuries.length)}
                            </p>
                        </div>
                        <div className="rounded-full p-3 bg-red-50">
                            <HeartPulse className="h-8 w-8 text-red-600" />
                        </div>
                    </div>
                </Card>

                <Card className="p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-500">Blessures graves</p>
                            <p className="text-3xl font-bold text-orange-600 mt-2">
                                {formatNumber(severeInjuries.length)}
                            </p>
                        </div>
                        <div className="rounded-full p-3 bg-orange-50">
                            <AlertCircle className="h-8 w-8 text-orange-600" />
                        </div>
                    </div>
                </Card>

                <Card className="p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-500">Historique total</p>
                            <p className="text-3xl font-bold text-gray-600 mt-2">
                                {formatNumber(injuriesData?.total || 0)}
                            </p>
                        </div>
                        <div className="rounded-full p-3 bg-gray-50">
                            <Calendar className="h-8 w-8 text-gray-600" />
                        </div>
                    </div>
                </Card>
            </div>

            {/* Filtres */}
            <Card className="p-6">
                <div className="grid gap-4 md:grid-cols-3">
                    {/* Recherche */}
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Rechercher une blessure..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    {/* Filtre par statut */}
                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">Tous les statuts</option>
                        <option value="active">Actives uniquement</option>
                        <option value="past">Historique uniquement</option>
                    </select>

                    {/* Filtre par gravité */}
                    <select
                        value={severityFilter}
                        onChange={(e) => setSeverityFilter(e.target.value)}
                        className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">Toutes les gravités</option>
                        <option value="Minor">Légère</option>
                        <option value="Moderate">Modérée</option>
                        <option value="Severe">Grave</option>
                    </select>
                </div>
            </Card>

            {/* Liste des blessures */}
            {injuriesLoading ? (
                <div className="space-y-4">
                    {[...Array(5)].map((_, i) => (
                        <Skeleton key={i} className="h-32" />
                    ))}
                </div>
            ) : filteredInjuries.length === 0 ? (
                <Card className="p-12 text-center">
                    <HeartPulse className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <h3 className="text-lg font-semibold mb-2">Aucune blessure trouvée</h3>
                    <p className="text-gray-500 mb-4">
                        {statusFilter === 'active'
                            ? 'Aucune blessure active pour le moment. Tant mieux ! 🎉'
                            : 'Essaie de modifier tes filtres ou ta recherche'}
                    </p>
                </Card>
            ) : (
                <div className="space-y-4">
                    {filteredInjuries.map((injury) => {
                        const player = playersMap.get(injury.player_id);
                        if (!player) return null;

                        return (
                            <Card
                                key={injury.id}
                                className={`p-6 ${injury.is_active
                                    ? 'border-l-4 border-l-red-500'
                                    : 'border-l-4 border-l-gray-300'
                                    }`}
                            >
                                <div className="flex items-start justify-between">
                                    {/* Gauche - Info joueur et blessure */}
                                    <div className="flex items-start gap-4 flex-1">
                                        {/* Avatar joueur */}
                                        <Link href={`/players/${player.id}`}>
                                            <img
                                                src={getPlayerAvatar(player.image_url, player.display_name)}
                                                alt={player.display_name || 'Player'}
                                                className="w-16 h-16 rounded-full object-cover cursor-pointer hover:opacity-80 transition-opacity"
                                            />
                                        </Link>

                                        {/* Détails */}
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-2">
                                                <Link
                                                    href={`/players/${player.id}`}
                                                    className="font-bold text-lg hover:text-blue-600 transition-colors"
                                                >
                                                    {player.display_name}
                                                </Link>
                                                {injury.is_active && (
                                                    <Badge className="bg-red-100 text-red-800 border-red-200">
                                                        Active
                                                    </Badge>
                                                )}
                                                {injury.severity && (
                                                    <Badge className={getSeverityColor(injury.severity)}>
                                                        {translateSeverity(injury.severity)}
                                                    </Badge>
                                                )}
                                            </div>

                                            <div className="space-y-1">
                                                <p className="font-semibold text-gray-900">
                                                    {injury.injury_type || 'Blessure'}
                                                </p>
                                                <p className="text-sm text-gray-600">
                                                    {injury.injury_description}
                                                </p>
                                            </div>

                                            {/* Dates */}
                                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4 text-sm">
                                                <div>
                                                    <div className="flex items-center gap-1 text-gray-500 mb-1">
                                                        <Calendar className="h-3 w-3" />
                                                        <span className="font-medium">Date de blessure</span>
                                                    </div>
                                                    <p className="text-gray-900">
                                                        {formatDate(injury.injury_date)}
                                                    </p>
                                                    <p className="text-xs text-gray-500">
                                                        {formatRelativeTime(injury.injury_date)}
                                                    </p>
                                                </div>

                                                <div>
                                                    <div className="flex items-center gap-1 text-gray-500 mb-1">
                                                        <Clock className="h-3 w-3" />
                                                        <span className="font-medium">Retour prévu</span>
                                                    </div>
                                                    <p className="text-gray-900">
                                                        {injury.expected_return_date
                                                            ? formatDate(injury.expected_return_date)
                                                            : 'Indéterminé'}
                                                    </p>
                                                    {injury.expected_return_date && (
                                                        <p className="text-xs text-gray-500">
                                                            {formatRelativeTime(injury.expected_return_date)}
                                                        </p>
                                                    )}
                                                </div>

                                                {injury.actual_return_date && (
                                                    <div>
                                                        <div className="flex items-center gap-1 text-gray-500 mb-1">
                                                            <TrendingUp className="h-3 w-3" />
                                                            <span className="font-medium">Retour effectif</span>
                                                        </div>
                                                        <p className="text-gray-900">
                                                            {formatDate(injury.actual_return_date)}
                                                        </p>
                                                        <p className="text-xs text-gray-500">
                                                            {formatRelativeTime(injury.actual_return_date)}
                                                        </p>
                                                    </div>
                                                )}
                                            </div>

                                            {/* Source */}
                                            {injury.source && (
                                                <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
                                                    <ExternalLink className="h-3 w-3" />
                                                    <span>Source: {injury.source}</span>
                                                    {injury.source_url && (
                                                        <Link
                                                            href={injury.source_url}
                                                            target="_blank"
                                                            className="text-blue-600 hover:underline"
                                                        >
                                                            Voir la source
                                                        </Link>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Droite - Actions */}
                                    <div className="flex gap-2">
                                        <Button variant="outline" size="sm">
                                            Modifier
                                        </Button>
                                    </div>
                                </div>
                            </Card>
                        );
                    })}
                </div>
            )}

            {/* Message si aucune blessure du tout */}
            {!injuriesLoading && injuriesData?.total === 0 && (
                <Card className="p-12 text-center">
                    <HeartPulse className="h-16 w-16 mx-auto text-green-500 mb-4" />
                    <h3 className="text-xl font-semibold mb-2">
                        Aucune blessure enregistrée ! 🎉
                    </h3>
                    <p className="text-gray-500 mb-6">
                        Tous tes joueurs sont en pleine forme. Continue comme ça !
                    </p>
                    <Button>
                        <Plus className="h-4 w-4 mr-2" />
                        Ajouter une blessure manuellement
                    </Button>
                </Card>
            )}
        </div>
    );
}