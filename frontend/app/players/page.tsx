'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { playersApi } from '@/lib/api';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/extras';
import { Alert, AlertDescription } from '@/components/ui/extras';
import {
    AlertCircle,
    Search,
    Filter,
    Users,
    TrendingUp,
    HeartPulse,
    ChevronLeft,
    ChevronRight,
} from 'lucide-react';
import {
    formatScore,
    translatePosition,
    getPositionBadge,
    getFlagEmoji,
    getPlayerAvatar,
    formatNumber,
} from '@/lib/utils';

const ITEMS_PER_PAGE = 12;

export default function PlayersPage() {
    // États pour les filtres
    const [searchTerm, setSearchTerm] = useState('');
    const [positionFilter, setPositionFilter] = useState<string>('all');
    const [injuryFilter, setInjuryFilter] = useState<string>('all');
    const [currentPage, setCurrentPage] = useState(1);

    // Récupérer tous les joueurs
    const {
        data: playersData,
        isLoading,
        error,
    } = useQuery({
        queryKey: ['players-list'],
        queryFn: () => playersApi.getAll({ limit: 500 }),
    });

    // Filtrer les joueurs
    const filteredPlayers = playersData?.players.filter((player) => {
        // Filtre de recherche
        const matchesSearch =
            !searchTerm ||
            player.display_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            player.club_name?.toLowerCase().includes(searchTerm.toLowerCase());

        // Filtre de position
        const matchesPosition =
            positionFilter === 'all' || player.position === positionFilter;

        // Filtre de blessure
        const matchesInjury =
            injuryFilter === 'all' ||
            (injuryFilter === 'injured' && player.is_injured) ||
            (injuryFilter === 'active' && !player.is_injured);

        return matchesSearch && matchesPosition && matchesInjury;
    }) || [];

    // Pagination
    const totalPages = Math.ceil(filteredPlayers.length / ITEMS_PER_PAGE);
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const paginatedPlayers = filteredPlayers.slice(
        startIndex,
        startIndex + ITEMS_PER_PAGE
    );

    // Réinitialiser la page quand on change de filtre
    const handleFilterChange = (filterFunc: () => void) => {
        setCurrentPage(1);
        filterFunc();
    };

    if (error) {
        return (
            <div className="space-y-6">
                <div>
                    <h1 className="text-3xl font-bold">Joueurs</h1>
                    <p className="text-gray-500 mt-1">Gestion de tous tes joueurs</p>
                </div>

                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                        Impossible de charger les joueurs. Vérifie que le backend est lancé.
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
                    <h1 className="text-3xl font-bold">Joueurs</h1>
                    <p className="text-gray-500 mt-1">
                        {filteredPlayers.length} joueur{filteredPlayers.length > 1 ? 's' : ''} trouvé
                        {filteredPlayers.length > 1 ? 's' : ''}
                    </p>
                </div>

                <Button>
                    <Users className="h-4 w-4 mr-2" />
                    Ajouter un joueur
                </Button>
            </div>

            {/* Filtres */}
            <Card className="p-6">
                <div className="grid gap-4 md:grid-cols-3">
                    {/* Recherche */}
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Rechercher un joueur..."
                            value={searchTerm}
                            onChange={(e) => handleFilterChange(() => setSearchTerm(e.target.value))}
                            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    {/* Filtre par position */}
                    <select
                        value={positionFilter}
                        onChange={(e) => handleFilterChange(() => setPositionFilter(e.target.value))}
                        className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">Toutes les positions</option>
                        <option value="Goalkeeper">Gardien</option>
                        <option value="Defender">Défenseur</option>
                        <option value="Midfielder">Milieu</option>
                        <option value="Forward">Attaquant</option>
                    </select>

                    {/* Filtre par statut */}
                    <select
                        value={injuryFilter}
                        onChange={(e) => handleFilterChange(() => setInjuryFilter(e.target.value))}
                        className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">Tous les statuts</option>
                        <option value="active">Actifs uniquement</option>
                        <option value="injured">Blessés uniquement</option>
                    </select>
                </div>

                {/* Stats rapides */}
                {playersData && (
                    <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-3 gap-4">
                        <div className="text-center">
                            <p className="text-sm text-gray-500">Total</p>
                            <p className="text-2xl font-bold">{playersData.total}</p>
                        </div>
                        <div className="text-center">
                            <p className="text-sm text-gray-500">Actifs</p>
                            <p className="text-2xl font-bold text-green-600">
                                {playersData.players.filter((p) => !p.is_injured).length}
                            </p>
                        </div>
                        <div className="text-center">
                            <p className="text-sm text-gray-500">Blessés</p>
                            <p className="text-2xl font-bold text-red-600">
                                {playersData.players.filter((p) => p.is_injured).length}
                            </p>
                        </div>
                    </div>
                )}
            </Card>

            {/* Liste des joueurs */}
            {isLoading ? (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {[...Array(6)].map((_, i) => (
                        <Skeleton key={i} className="h-64" />
                    ))}
                </div>
            ) : filteredPlayers.length === 0 ? (
                <Card className="p-12 text-center">
                    <Filter className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <h3 className="text-lg font-semibold mb-2">Aucun joueur trouvé</h3>
                    <p className="text-gray-500">
                        Essaie de modifier tes filtres ou ta recherche
                    </p>
                </Card>
            ) : (
                <>
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                        {paginatedPlayers.map((player) => (
                            <Link
                                key={player.id}
                                href={`/players/${player.id}`}
                                className="block group"
                            >
                                <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer h-full">
                                    <div className="flex items-start justify-between mb-4">
                                        {/* Avatar */}
                                        <div className="flex items-center space-x-3 flex-1 min-w-0">
                                            <img
                                                src={getPlayerAvatar(player.image_url, player.display_name)}
                                                alt={player.display_name || 'Player'}
                                                className="w-16 h-16 rounded-full object-cover"
                                            />
                                            <div className="flex-1 min-w-0">
                                                <h3 className="font-bold text-lg truncate group-hover:text-blue-600 transition-colors">
                                                    {player.display_name}
                                                </h3>
                                                <p className="text-sm text-gray-500 truncate flex items-center gap-1">
                                                    {player.country_code && (
                                                        <span>{getFlagEmoji(player.country_code)}</span>
                                                    )}
                                                    {player.club_name}
                                                </p>
                                            </div>
                                        </div>

                                        {/* Badge de blessure */}
                                        {player.is_injured && (
                                            <Badge className="bg-red-100 text-red-800 border-red-200">
                                                <HeartPulse className="h-3 w-3 mr-1" />
                                                Blessé
                                            </Badge>
                                        )}
                                    </div>

                                    {/* Position */}
                                    <div className="mb-4">
                                        <Badge className={getPositionBadge(player.position)}>
                                            {translatePosition(player.position)}
                                        </Badge>
                                    </div>

                                    {/* Stats */}
                                    <div className="space-y-2">
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-gray-500">Score moyen</span>
                                            <span className="font-bold flex items-center gap-1">
                                                <TrendingUp className="h-4 w-4 text-blue-600" />
                                                {formatScore(player.average_score)}
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-gray-500">Matchs joués</span>
                                            <span className="font-bold">{formatNumber(player.total_games)}</span>
                                        </div>
                                        {player.last_game_score !== null && (
                                            <div className="flex items-center justify-between text-sm">
                                                <span className="text-gray-500">Dernier match</span>
                                                <span className="font-bold text-green-600">
                                                    {formatScore(player.last_game_score)}
                                                </span>
                                            </div>
                                        )}
                                    </div>

                                    {/* Statut de blessure */}
                                    {player.is_injured && player.injury_status && (
                                        <div className="mt-4 pt-4 border-t border-gray-100">
                                            <p className="text-xs text-red-600 flex items-center gap-1">
                                                <HeartPulse className="h-3 w-3" />
                                                {player.injury_status}
                                            </p>
                                        </div>
                                    )}
                                </Card>
                            </Link>
                        ))}
                    </div>

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="flex items-center justify-center space-x-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                                disabled={currentPage === 1}
                            >
                                <ChevronLeft className="h-4 w-4" />
                            </Button>

                            <div className="flex items-center space-x-1">
                                {[...Array(totalPages)].map((_, i) => (
                                    <Button
                                        key={i}
                                        variant={currentPage === i + 1 ? 'default' : 'outline'}
                                        size="sm"
                                        onClick={() => setCurrentPage(i + 1)}
                                        className="w-10"
                                    >
                                        {i + 1}
                                    </Button>
                                ))}
                            </div>

                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                                disabled={currentPage === totalPages}
                            >
                                <ChevronRight className="h-4 w-4" />
                            </Button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}