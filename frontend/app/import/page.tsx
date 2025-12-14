'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { footballApi } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import {
    Search,
    Plus,
    Check,
    AlertCircle,
    Loader2,
    User,
    MapPin,
    Calendar,
} from 'lucide-react';
import type { FootballAPIPlayer } from '../types/api';
import { useRouter } from 'next/navigation';

export default function ImportPage() {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<FootballAPIPlayer[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const [searchError, setSearchError] = useState<string | null>(null);
    const [addedPlayers, setAddedPlayers] = useState<Set<number>>(new Set());

    const queryClient = useQueryClient();
    const router = useRouter();

    // Rechercher des joueurs
    const handleSearch = async () => {
        if (searchQuery.length < 3) {
            setSearchError('La recherche doit contenir au moins 3 caractères');
            return;
        }

        setIsSearching(true);
        setSearchError(null);
        setSearchResults([]);

        try {
            const result = await footballApi.searchPlayers(searchQuery);

            if (result.success && result.players) {
                setSearchResults(result.players);
                if (result.players.length === 0) {
                    setSearchError('Aucun joueur trouvé. Essaie avec un autre nom.');
                }
            } else {
                setSearchError('Erreur lors de la recherche. Réessaie.');
            }
        } catch (error: any) {
            console.error('Search error:', error);
            setSearchError(
                error.response?.data?.detail || 'Impossible de rechercher les joueurs'
            );
        } finally {
            setIsSearching(false);
        }
    };

    // Mutation pour importer un joueur
    const importMutation = useMutation({
        mutationFn: async (player: FootballAPIPlayer) => {
            return await footballApi.importPlayer({
                football_api_id: player.id,
                sorare_id: `api-football-${player.id}`,
                display_name: player.name,
            });
        },
        onSuccess: (data, player) => {
            // Ajouter à la liste des joueurs ajoutés
            setAddedPlayers((prev) => new Set(prev).add(player.id));

            // Invalider les caches pour rafraîchir les listes
            queryClient.invalidateQueries({ queryKey: ['players-list'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });

            // Message de succès - CORRECTION: data contient directement display_name
            console.log('✅ Joueur ajouté:', data.display_name || player.name);
        },
        onError: (error: any, player) => {
            console.error('❌ Erreur lors de l\'ajout:', error);
            alert(`Erreur: ${error.response?.data?.detail || 'Impossible d\'ajouter le joueur'}`);
        },
    });

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Importer des Joueurs</h1>
                <p className="text-gray-500 mt-1">
                    Recherche et ajoute des joueurs depuis API-Football
                </p>
            </div>

            {/* Barre de recherche */}
            <Card className="p-6">
                <div className="flex gap-4">
                    <div className="flex-1">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Rechercher un joueur (ex: Mbappé, Messi...)"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                            />
                        </div>
                    </div>
                    <Button
                        onClick={handleSearch}
                        disabled={isSearching || searchQuery.length < 3}
                        className="px-8"
                    >
                        {isSearching ? (
                            <Loader2 className="h-5 w-5 animate-spin" />
                        ) : (
                            <>
                                <Search className="h-5 w-5 mr-2" />
                                Rechercher
                            </>
                        )}
                    </Button>
                </div>

                {searchError && (
                    <Alert variant="destructive" className="mt-4">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>{searchError}</AlertDescription>
                    </Alert>
                )}
            </Card>

            {/* Résultats de recherche */}
            {isSearching && (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {[...Array(6)].map((_, i) => (
                        <Skeleton key={i} className="h-48" />
                    ))}
                </div>
            )}

            {!isSearching && searchResults.length > 0 && (
                <div>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold">
                            {searchResults.length} résultat{searchResults.length > 1 ? 's' : ''} trouvé{searchResults.length > 1 ? 's' : ''}
                        </h2>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {searchResults.map((player) => {
                            const isAdded = addedPlayers.has(player.id);
                            const isAdding = importMutation.isPending;

                            return (
                                <Card key={player.id} className="p-6 hover:shadow-lg transition-shadow">
                                    <div className="flex items-start gap-4">
                                        {/* Photo du joueur */}
                                        <div className="flex-shrink-0">
                                            {player.photo ? (
                                                <img
                                                    src={player.photo}
                                                    alt={player.name}
                                                    className="w-16 h-16 rounded-full object-cover border-2 border-gray-200"
                                                    onError={(e) => {
                                                        e.currentTarget.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(player.name)}&background=random`;
                                                    }}
                                                />
                                            ) : (
                                                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                                                    <User className="h-8 w-8 text-white" />
                                                </div>
                                            )}
                                        </div>

                                        {/* Infos joueur */}
                                        <div className="flex-1 min-w-0">
                                            <h3 className="font-bold text-lg truncate">
                                                {player.name}
                                            </h3>

                                            <div className="space-y-1 mt-2 text-sm text-gray-600">
                                                {player.age && (
                                                    <div className="flex items-center gap-1">
                                                        <Calendar className="h-3 w-3" />
                                                        <span>{player.age} ans</span>
                                                    </div>
                                                )}
                                                {player.nationality && (
                                                    <div className="flex items-center gap-1">
                                                        <MapPin className="h-3 w-3" />
                                                        <span>{player.nationality}</span>
                                                    </div>
                                                )}
                                            </div>

                                            {/* Bouton d'ajout */}
                                            <div className="mt-4">
                                                {isAdded ? (
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        className="w-full"
                                                        disabled
                                                    >
                                                        <Check className="h-4 w-4 mr-2" />
                                                        Ajouté
                                                    </Button>
                                                ) : (
                                                    <Button
                                                        size="sm"
                                                        className="w-full"
                                                        onClick={() => importMutation.mutate(player)}
                                                        disabled={isAdding}
                                                    >
                                                        {isAdding ? (
                                                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                                        ) : (
                                                            <Plus className="h-4 w-4 mr-2" />
                                                        )}
                                                        Ajouter
                                                    </Button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </Card>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Message si joueurs ajoutés */}
            {addedPlayers.size > 0 && (
                <Alert className="bg-green-50 border-green-200">
                    <Check className="h-4 w-4 text-green-600" />
                    <AlertDescription className="text-green-800">
                        {addedPlayers.size} joueur{addedPlayers.size > 1 ? 's' : ''} ajouté{addedPlayers.size > 1 ? 's' : ''} avec succès !{' '}
                        <Button
                            variant="link"
                            className="p-0 h-auto text-green-600"
                            onClick={() => router.push('/players')}
                        >
                            Voir mes joueurs →
                        </Button>
                    </AlertDescription>
                </Alert>
            )}
        </div>
    );
}