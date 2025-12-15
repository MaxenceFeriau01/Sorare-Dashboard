'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { playersApi, footballApi } from '@/lib/api';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
    AlertCircle,
    Search,
    HeartPulse,
    Clock,
    User,
    Shield,
    Activity,
    RefreshCw,
    Loader2,
    CheckCircle,
    XCircle,
} from 'lucide-react';
import { formatRelativeTime } from '@/lib/utils';
import type { Player } from '../types/api';

export default function InjuriesPage() {
    const [searchTerm, setSearchTerm] = useState('');
    const queryClient = useQueryClient();

    // Récupérer tous les joueurs
    const {
        data: playersData,
        isLoading,
        error,
    } = useQuery({
        queryKey: ['players-list'],
        queryFn: () => playersApi.getAll({ limit: 500 }),
    });

    // Mutation pour synchroniser les blessures
    const syncMutation = useMutation({
        mutationFn: async () => {
            return await footballApi.syncInjuries();
        },
        onSuccess: (data) => {
            console.log('✅ Synchronisation terminée:', data);
            // Rafraîchir les données
            queryClient.invalidateQueries({ queryKey: ['players-list'] });
            queryClient.invalidateQueries({ queryKey: ['injuries-list'] });
        },
        onError: (error: any) => {
            console.error('❌ Erreur sync:', error);
            alert(`Erreur lors de la synchronisation: ${error.response?.data?.detail || error.message}`);
        },
    });

    // Filtrer pour n'afficher que les joueurs blessés
    const injuredPlayers = (playersData?.players || []).filter((player) => player.is_injured);

    // Filtrer par recherche
    const filteredPlayers = injuredPlayers.filter((player) => {
        if (!searchTerm) return true;
        
        const term = searchTerm.toLowerCase();
        return (
            player.display_name?.toLowerCase().includes(term) ||
            player.club_name?.toLowerCase().includes(term) ||
            player.injury_status?.toLowerCase().includes(term) ||
            player.position?.toLowerCase().includes(term)
        );
    });

    if (error) {
        return (
            <div className="space-y-6">
                <div>
                    <h1 className="text-3xl font-bold">Blessures</h1>
                    <p className="text-gray-500 mt-1">Suivi des blessures de tes joueurs</p>
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
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <HeartPulse className="h-8 w-8 text-red-500" />
                        Blessures
                    </h1>
                    <p className="text-gray-500 mt-1">
                        {filteredPlayers.length} joueur{filteredPlayers.length > 1 ? 's' : ''} blessé
                        {filteredPlayers.length > 1 ? 's' : ''}
                    </p>
                </div>

                {/* ✅ BOUTON DE SYNCHRONISATION INTELLIGENTE */}
                <Button
                    onClick={() => syncMutation.mutate()}
                    disabled={syncMutation.isPending}
                    className="flex items-center gap-2"
                >
                    {syncMutation.isPending ? (
                        <>
                            <Loader2 className="h-4 w-4 animate-spin" />
                            Synchronisation...
                        </>
                    ) : (
                        <>
                            <RefreshCw className="h-4 w-4" />
                            Actualiser les blessures
                        </>
                    )}
                </Button>
            </div>

            {/* Message de résultat après sync */}
            {syncMutation.isSuccess && syncMutation.data && (
                <Alert className="bg-green-50 border-green-200">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <AlertDescription className="text-green-800">
                        <div className="font-medium mb-1">Synchronisation terminée !</div>
                        <div className="text-sm space-y-1">
                            <div>• {syncMutation.data.stats.total_checked} joueur(s) vérifiés</div>
                            <div>• {syncMutation.data.stats.injuries_found} nouvelle(s) blessure(s)</div>
                            <div>• {syncMutation.data.stats.injuries_cleared} blessure(s) invalidée(s)</div>
                        </div>
                    </AlertDescription>
                </Alert>
            )}

            {/* Stats rapides */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card className="p-6">
                    <div className="flex items-center gap-4">
                        <div className="rounded-full p-3 bg-red-50">
                            <HeartPulse className="h-6 w-6 text-red-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Joueurs blessés</p>
                            <p className="text-3xl font-bold text-red-600">{injuredPlayers.length}</p>
                        </div>
                    </div>
                </Card>

                <Card className="p-6">
                    <div className="flex items-center gap-4">
                        <div className="rounded-full p-3 bg-green-50">
                            <Activity className="h-6 w-6 text-green-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Joueurs actifs</p>
                            <p className="text-3xl font-bold text-green-600">
                                {(playersData?.players || []).filter((p) => !p.is_injured).length}
                            </p>
                        </div>
                    </div>
                </Card>

                <Card className="p-6">
                    <div className="flex items-center gap-4">
                        <div className="rounded-full p-3 bg-blue-50">
                            <User className="h-6 w-6 text-blue-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Total joueurs</p>
                            <p className="text-3xl font-bold text-blue-600">
                                {playersData?.total || 0}
                            </p>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Barre de recherche */}
            <Card className="p-4">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Rechercher un joueur blessé..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    />
                </div>
            </Card>

            {/* Liste des joueurs blessés */}
            {isLoading ? (
                <div className="space-y-4">
                    {[...Array(3)].map((_, i) => (
                        <Skeleton key={i} className="h-32" />
                    ))}
                </div>
            ) : filteredPlayers.length === 0 ? (
                <Card className="p-12 text-center">
                    <div className="rounded-full w-16 h-16 bg-green-50 flex items-center justify-center mx-auto mb-4">
                        <Shield className="h-8 w-8 text-green-600" />
                    </div>
                    <h3 className="text-xl font-semibold mb-2">
                        {injuredPlayers.length === 0 ? 'Aucune blessure ! 🎉' : 'Aucun résultat'}
                    </h3>
                    <p className="text-gray-500">
                        {injuredPlayers.length === 0
                            ? 'Tous tes joueurs sont en forme !'
                            : 'Essaie avec une autre recherche'}
                    </p>
                    {injuredPlayers.length === 0 && (
                        <Button
                            variant="outline"
                            className="mt-4"
                            onClick={() => syncMutation.mutate()}
                            disabled={syncMutation.isPending}
                        >
                            {syncMutation.isPending ? (
                                <>
                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                    Vérification...
                                </>
                            ) : (
                                <>
                                    <RefreshCw className="h-4 w-4 mr-2" />
                                    Vérifier les blessures
                                </>
                            )}
                        </Button>
                    )}
                </Card>
            ) : (
                <div className="space-y-4">
                    {filteredPlayers.map((player) => (
                        <Card
                            key={player.id}
                            className="p-6 border-l-4 border-l-red-500 hover:shadow-lg transition-shadow"
                        >
                            <div className="flex items-start justify-between">
                                {/* Gauche - Info joueur */}
                                <div className="flex items-start gap-4 flex-1">
                                    {/* Avatar joueur */}
                                    <Link href={`/players/${player.id}`}>
                                        <img
                                            src={
                                                player.image_url ||
                                                `https://ui-avatars.com/api/?name=${encodeURIComponent(
                                                    player.display_name || 'Player'
                                                )}&background=random`
                                            }
                                            alt={player.display_name || 'Player'}
                                            className="w-16 h-16 rounded-full object-cover cursor-pointer hover:opacity-80 transition-opacity border-2 border-gray-200"
                                            onError={(e) => {
                                                e.currentTarget.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(
                                                    player.display_name || 'Player'
                                                )}&background=random`;
                                            }}
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
                                            <Badge variant="destructive" className="gap-1">
                                                <HeartPulse className="h-3 w-3" />
                                                Blessé
                                            </Badge>
                                        </div>

                                        <div className="space-y-2">
                                            {/* Infos générales */}
                                            <div className="flex items-center gap-4 text-sm text-gray-600 flex-wrap">
                                                <span className="flex items-center gap-1">
                                                    <Shield className="h-4 w-4" />
                                                    {player.position || 'Position inconnue'}
                                                </span>
                                                <span>•</span>
                                                <span>{player.club_name || 'Club inconnu'}</span>
                                                {player.country && (
                                                    <>
                                                        <span>•</span>
                                                        <span>{player.country}</span>
                                                    </>
                                                )}
                                            </div>

                                            {/* Statut de blessure */}
                                            {player.injury_status && (
                                                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                                                    <p className="text-sm font-medium text-red-900">
                                                        {player.injury_status}
                                                    </p>
                                                </div>
                                            )}

                                            {/* Dernière mise à jour */}
                                            <div className="flex items-center gap-1 text-xs text-gray-500">
                                                <Clock className="h-3 w-3" />
                                                <span>
                                                    Mis à jour {formatRelativeTime(player.updated_at)}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Droite - Actions */}
                                <div>
                                    <Link href={`/players/${player.id}`}>
                                        <Button variant="outline" size="sm">
                                            Voir détails
                                        </Button>
                                    </Link>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            )}

            {/* Note explicative */}
            <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                    <div className="font-medium mb-1">Comment ça marche ?</div>
                    <div className="text-sm text-gray-600">
                        Le système vérifie si les joueurs ont réellement joué dans leurs derniers matchs.
                        Si un joueur marqué "blessé" par l'API a joué récemment, la blessure est automatiquement invalidée.
                    </div>
                </AlertDescription>
            </Alert>
        </div>
    );
}