'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton, Alert, AlertDescription } from '@/components/ui/extras';
import {
    Search,
    Users,
    Download,
    CheckCircle,
    AlertCircle,
    Flag,
    Calendar,
} from 'lucide-react';
import api from '@/lib/api';

interface Team {
    id: number;
    name: string;
    logo: string;
}

// ✅ CORRECTION: Interface corrigée pour correspondre aux données réelles du backend
interface Player {
    id: number;
    name: string;
    firstname: string;
    lastname: string;
    age: number | null;
    number: number | null;
    position: string;
    photo: string | null;
    nationality: string | null;
    is_imported?: boolean;
    dashboard_player_id?: number | null;
}

interface TeamSquadResponse {
    success: boolean;
    team: Team;
    players: Player[];
    count: number;
    imported_count: number;
}

export default function TeamsPage() {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
    const [positionFilter, setPositionFilter] = useState<string>('all');
    const queryClient = useQueryClient();

    // Recherche d'équipes
    const { data: teamsData, isLoading: teamsLoading } = useQuery({
        queryKey: ['search-teams', searchQuery],
        queryFn: async () => {
            if (searchQuery.length < 3) return null;
            const { data } = await api.get(`/football/search-teams?query=${searchQuery}`);
            return data;
        },
        enabled: searchQuery.length >= 3,
    });

    // Récupérer l'effectif d'une équipe
    const {
        data: squadData,
        isLoading: squadLoading,
        error: squadError,
    } = useQuery<TeamSquadResponse>({
        queryKey: ['team-squad', selectedTeam?.id],
        queryFn: async () => {
            const { data } = await api.get(`/football/team/${selectedTeam?.id}/squad`);
            return data;
        },
        enabled: !!selectedTeam,
    });

    // Mutation pour importer un joueur
    const importPlayerMutation = useMutation({
        mutationFn: async ({ teamId, playerId }: { teamId: number; playerId: number }) => {
            const { data } = await api.post(
                `/football/team/${teamId}/import-player/${playerId}`
            );
            return data;
        },
        onSuccess: (data, variables) => {
            queryClient.setQueryData<TeamSquadResponse>(
                ['team-squad', selectedTeam?.id],
                (old) => {
                    if (!old) return old;
                    
                    return {
                        ...old,
                        players: old.players.map((player) =>
                            player.id === variables.playerId
                                ? { ...player, is_imported: true }
                                : player
                        ),
                        imported_count: old.imported_count + 1,
                    };
                }
            );
            
            queryClient.invalidateQueries({ queryKey: ['players-list'] });
        },
    });

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
    };

    const handleTeamSelect = (team: Team) => {
        setSelectedTeam(team);
    };

    const handleImportPlayer = (playerId: number) => {
        if (!selectedTeam) return;
        importPlayerMutation.mutate({ teamId: selectedTeam.id, playerId });
    };

    // Filtrer les joueurs par position
    const filteredPlayers = squadData?.players.filter((player) => {
        if (positionFilter === 'all') return true;
        return player.position === positionFilter;
    }) || [];

    const positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Attacker'];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Importer par équipe</h1>
                <p className="text-gray-500 mt-1">
                    Recherche une équipe et importe ses joueurs dans ton dashboard
                </p>
            </div>

            {/* Recherche d'équipe */}
            <Card className="p-6">
                <form onSubmit={handleSearch} className="space-y-4">
                    <div className="flex gap-4">
                        <div className="flex-1">
                            <label className="block text-sm font-medium mb-2">
                                🔍 Nom de l'équipe
                            </label>
                            <Input
                                type="text"
                                placeholder="Real Madrid, PSG, Arsenal..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full"
                            />
                            {searchQuery.length > 0 && searchQuery.length < 3 && (
                                <p className="text-sm text-amber-600 mt-1">
                                    Minimum 3 caractères
                                </p>
                            )}
                        </div>
                    </div>

                    {/* Résultats de recherche */}
                    {teamsLoading && <p>Recherche en cours...</p>}

                    {teamsData && teamsData.teams && (
                        <div className="space-y-2">
                            <p className="text-sm text-gray-600">
                                {teamsData.count} équipe(s) trouvée(s)
                            </p>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                {teamsData.teams.map((team: any) => (
                                    <Card
                                        key={team.id}
                                        className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                                            selectedTeam?.id === team.id
                                                ? 'ring-2 ring-blue-500'
                                                : ''
                                        }`}
                                        onClick={() => handleTeamSelect(team)}
                                    >
                                        <div className="flex items-center gap-3">
                                            <img
                                                src={team.logo}
                                                alt={team.name}
                                                className="w-12 h-12 object-contain"
                                            />
                                            <div>
                                                <p className="font-semibold">{team.name}</p>
                                                <p className="text-sm text-gray-500">
                                                    {team.country}
                                                </p>
                                            </div>
                                        </div>
                                    </Card>
                                ))}
                            </div>
                        </div>
                    )}
                </form>
            </Card>

            {/* Effectif de l'équipe sélectionnée */}
            {selectedTeam && (
                <Card className="p-6">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <img
                                src={selectedTeam.logo}
                                alt={selectedTeam.name}
                                className="w-16 h-16 object-contain"
                            />
                            <div>
                                <h2 className="text-2xl font-bold">{selectedTeam.name}</h2>
                                {squadData && (
                                    <p className="text-gray-600">
                                        {squadData.count} joueurs •{' '}
                                        {squadData.imported_count} déjà importés
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Filtres par position */}
                    <div className="flex gap-2 mb-6 flex-wrap">
                        <Button
                            variant={positionFilter === 'all' ? 'default' : 'outline'}
                            onClick={() => setPositionFilter('all')}
                            size="sm"
                        >
                            Tous ({squadData?.players.length || 0})
                        </Button>
                        {positions.map((pos) => {
                            const count =
                                squadData?.players.filter((p) => p.position === pos).length ||
                                0;
                            return (
                                <Button
                                    key={pos}
                                    variant={positionFilter === pos ? 'default' : 'outline'}
                                    onClick={() => setPositionFilter(pos)}
                                    size="sm"
                                >
                                    {pos} ({count})
                                </Button>
                            );
                        })}
                    </div>

                    {/* Liste des joueurs */}
                    {squadLoading && <Skeleton className="h-64" />}

                    {squadError && (
                        <Alert variant="destructive">
                            <AlertCircle className="h-4 w-4" />
                            <AlertDescription>
                                Impossible de charger l'effectif
                            </AlertDescription>
                        </Alert>
                    )}

                    {squadData && (
                        <div className="space-y-3">
                            {filteredPlayers.map((player) => (
                                <Card
                                    key={player.id}
                                    className={`p-4 ${
                                        player.is_imported ? 'bg-green-50' : ''
                                    }`}
                                >
                                    <div className="flex items-start gap-4">
                                        {/* Photo */}
                                        <img
                                            src={player.photo || '/default-avatar.png'}
                                            alt={player.name}
                                            className="w-20 h-20 rounded-full object-cover"
                                            onError={(e) => {
                                                e.currentTarget.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(player.name)}&background=random`;
                                            }}
                                        />

                                        {/* Infos principales */}
                                        <div className="flex-1">
                                            <div className="flex items-start justify-between mb-2">
                                                <div>
                                                    <h3 className="font-bold text-lg">
                                                        {player.name}
                                                        {player.number && (
                                                            <span className="ml-2 text-gray-500">
                                                                #{player.number}
                                                            </span>
                                                        )}
                                                    </h3>
                                                    <div className="flex items-center gap-3 text-sm text-gray-600 mt-1 flex-wrap">
                                                        <span className="flex items-center gap-1">
                                                            <Users className="w-4 h-4" />
                                                            {player.position}
                                                        </span>
                                                        {player.age && (
                                                            <span className="flex items-center gap-1">
                                                                <Calendar className="w-4 h-4" />
                                                                {player.age} ans
                                                            </span>
                                                        )}
                                                        {player.nationality && (
                                                            <span className="flex items-center gap-1">
                                                                <Flag className="w-4 h-4" />
                                                                {player.nationality}
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>

                                                {/* Bouton Import */}
                                                <div>
                                                    {player.is_imported ? (
                                                        <Badge className="bg-green-100 text-green-800">
                                                            <CheckCircle className="w-4 h-4 mr-1" />
                                                            Importé
                                                        </Badge>
                                                    ) : (
                                                        <Button
                                                            size="sm"
                                                            onClick={() =>
                                                                handleImportPlayer(player.id)
                                                            }
                                                            disabled={
                                                                importPlayerMutation.isPending
                                                            }
                                                        >
                                                            <Download className="w-4 h-4 mr-1" />
                                                            Importer
                                                        </Button>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </Card>
                            ))}

                            {filteredPlayers.length === 0 && (
                                <p className="text-center text-gray-500 py-8">
                                    Aucun joueur dans cette position
                                </p>
                            )}
                        </div>
                    )}
                </Card>
            )}
        </div>
    );
}