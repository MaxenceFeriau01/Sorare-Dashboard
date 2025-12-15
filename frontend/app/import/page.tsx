'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { footballApi } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import {
    Search,
    Plus,
    Check,
    AlertCircle,
    Loader2,
    User,
    Shield,
    ArrowLeft,
    Users,
} from 'lucide-react';
import { useRouter } from 'next/navigation';

interface Team {
    id: number;
    name: string;
    logo: string | null;
    country: string | null;
}

interface Player {
    id: number;
    name: string;
    firstname: string;
    lastname: string;
    age: number | null;
    position: string;
    photo: string | null;
    nationality: string | null;
    number: number | null;
}

export default function ImportPage() {
    // État de recherche d'équipes
    const [searchQuery, setSearchQuery] = useState('');
    const [teams, setTeams] = useState<Team[]>([]);
    const [isSearchingTeams, setIsSearchingTeams] = useState(false);
    const [searchError, setSearchError] = useState<string | null>(null);

    // État de l'équipe sélectionnée
    const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
    const [players, setPlayers] = useState<Player[]>([]);
    const [isLoadingPlayers, setIsLoadingPlayers] = useState(false);
    const [addedPlayers, setAddedPlayers] = useState<Set<number>>(new Set());

    const queryClient = useQueryClient();
    const router = useRouter();

    // Rechercher des équipes
    const handleSearchTeams = async () => {
        if (searchQuery.length < 3) {
            setSearchError('La recherche doit contenir au moins 3 caractères');
            return;
        }

        setIsSearchingTeams(true);
        setSearchError(null);
        setTeams([]);
        setSelectedTeam(null);
        setPlayers([]);

        try {
            const result = await footballApi.searchTeams(searchQuery);

            if (result.success && result.teams) {
                setTeams(result.teams);
                if (result.teams.length === 0) {
                    setSearchError('Aucune équipe trouvée. Essaie avec un autre nom.');
                }
            } else {
                setSearchError('Erreur lors de la recherche.');
            }
        } catch (error: any) {
            console.error('Search teams error:', error);
            setSearchError(
                error.response?.data?.detail || 'Impossible de rechercher les équipes'
            );
        } finally {
            setIsSearchingTeams(false);
        }
    };

    // Charger l'effectif d'une équipe
    const handleSelectTeam = async (team: Team) => {
        setSelectedTeam(team);
        setIsLoadingPlayers(true);
        setPlayers([]);
        setSearchError(null);

        try {
            const result = await footballApi.getTeamSquad(team.id);

            console.log('📋 Squad loaded:', result);

            if (result.success && result.players) {
                setPlayers(result.players);
            } else {
                setSearchError('Impossible de charger l\'effectif');
            }
        } catch (error: any) {
            console.error('Load squad error:', error);
            setSearchError(
                error.response?.data?.detail || 'Impossible de charger l\'effectif'
            );
        } finally {
            setIsLoadingPlayers(false);
        }
    };

    // Retour à la recherche
    const handleBackToSearch = () => {
        setSelectedTeam(null);
        setPlayers([]);
        setSearchError(null);
    };

    // Mutation pour importer un joueur
    const importMutation = useMutation({
        mutationFn: async (player: Player) => {
            return await footballApi.importPlayer({
                football_api_id: player.id,
                sorare_id: `${player.firstname}-${player.lastname}-${player.id}`.toLowerCase().replace(/\s+/g, '-'),
                display_name: player.name,
            });
        },
        onSuccess: (data, player) => {
            setAddedPlayers((prev) => new Set(prev).add(player.id));
            queryClient.invalidateQueries({ queryKey: ['players-list'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
            console.log('✅ Joueur ajouté:', data.display_name || player.name);
        },
        onError: (error: any, player) => {
            console.error('❌ Erreur import:', error);
            alert(`Erreur: ${error.response?.data?.detail || 'Impossible d\'ajouter le joueur'}`);
        },
    });

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Importer des Joueurs</h1>
                <p className="text-gray-500 mt-1">
                    Recherche une équipe et ajoute ses joueurs un par un
                </p>
            </div>

            {/* Barre de recherche d'équipes */}
            {!selectedTeam && (
                <Card className="p-6">
                    <div className="flex gap-4">
                        <div className="flex-1">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Rechercher une équipe (ex: Arsenal, Real Madrid...)"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSearchTeams()}
                                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                                />
                            </div>
                        </div>
                        <Button
                            onClick={handleSearchTeams}
                            disabled={isSearchingTeams || searchQuery.length < 3}
                            className="px-8"
                        >
                            {isSearchingTeams ? (
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
            )}

            {/* Liste des équipes */}
            {!selectedTeam && teams.length > 0 && (
                <div>
                    <h2 className="text-xl font-semibold mb-4">
                        {teams.length} équipe{teams.length > 1 ? 's' : ''} trouvée{teams.length > 1 ? 's' : ''}
                    </h2>
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {teams.map((team) => (
                            <Card
                                key={team.id}
                                className="p-6 hover:shadow-lg transition-shadow cursor-pointer"
                                onClick={() => handleSelectTeam(team)}
                            >
                                <div className="flex items-center gap-4">
                                    {team.logo ? (
                                        <img
                                            src={team.logo}
                                            alt={team.name}
                                            className="w-16 h-16 object-contain"
                                        />
                                    ) : (
                                        <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
                                            <Shield className="h-8 w-8 text-gray-400" />
                                        </div>
                                    )}
                                    <div className="flex-1">
                                        <h3 className="font-bold text-lg">{team.name}</h3>
                                        {team.country && (
                                            <p className="text-sm text-gray-500">{team.country}</p>
                                        )}
                                    </div>
                                    <Users className="h-5 w-5 text-gray-400" />
                                </div>
                            </Card>
                        ))}
                    </div>
                </div>
            )}

            {/* Effectif de l'équipe sélectionnée */}
            {selectedTeam && (
                <div className="space-y-6">
                    {/* Header de l'équipe */}
                    <Card className="p-6">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={handleBackToSearch}
                                >
                                    <ArrowLeft className="h-4 w-4 mr-2" />
                                    Retour
                                </Button>
                                {selectedTeam.logo && (
                                    <img
                                        src={selectedTeam.logo}
                                        alt={selectedTeam.name}
                                        className="w-12 h-12 object-contain"
                                    />
                                )}
                                <div>
                                    <h2 className="text-2xl font-bold">{selectedTeam.name}</h2>
                                    {selectedTeam.country && (
                                        <p className="text-gray-500">{selectedTeam.country}</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    </Card>

                    {/* Liste des joueurs */}
                    {isLoadingPlayers ? (
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {[...Array(12)].map((_, i) => (
                                <Skeleton key={i} className="h-48" />
                            ))}
                        </div>
                    ) : players.length > 0 ? (
                        <div>
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-xl font-semibold">
                                    {players.length} joueur{players.length > 1 ? 's' : ''}
                                </h3>
                            </div>

                            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                                {players.map((player) => {
                                    const isAdded = addedPlayers.has(player.id);
                                    const isAdding = importMutation.isPending;

                                    return (
                                        <Card key={player.id} className="p-6 hover:shadow-lg transition-shadow">
                                            <div className="flex items-start gap-4">
                                                {/* Photo */}
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

                                                {/* Infos */}
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-start justify-between gap-2">
                                                        <h4 className="font-bold truncate">{player.name}</h4>
                                                        {player.number && (
                                                            <Badge variant="outline" className="flex-shrink-0">
                                                                #{player.number}
                                                            </Badge>
                                                        )}
                                                    </div>

                                                    <div className="space-y-1 mt-2 text-sm text-gray-600">
                                                        {player.position && (
                                                            <p className="font-medium">{player.position}</p>
                                                        )}
                                                        {player.age && (
                                                            <p>{player.age} ans</p>
                                                        )}
                                                        {player.nationality && (
                                                            <p className="truncate">{player.nationality}</p>
                                                        )}
                                                    </div>

                                                    {/* Bouton d'import */}
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
                    ) : (
                        <Alert>
                            <AlertCircle className="h-4 w-4" />
                            <AlertDescription>
                                Aucun joueur trouvé pour cette équipe.
                            </AlertDescription>
                        </Alert>
                    )}
                </div>
            )}

            {/* Message de succès */}
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