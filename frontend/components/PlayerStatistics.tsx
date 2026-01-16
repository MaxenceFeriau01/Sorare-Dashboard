/**
 * Composant principal pour afficher les statistiques des joueurs
 */
'use client';

import React, { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, RefreshCw, Filter, TrendingUp, TrendingDown, Award, Target, Users } from 'lucide-react';

// Types
interface PlayerStats {
  id: number;
  player: {
    id: number;
    name: string;
    firstname: string;
    lastname: string;
    age: number;
    nationality: string;
    photo: string;
  };
  team: {
    id: number;
    name: string;
    logo: string;
  };
  league: {
    id: number;
    name: string;
    country: string;
    logo: string;
    season: number;
  };
  statistics: {
    games: {
      appearences: number;
      lineups: number;
      minutes: number;
      position: string;
      rating: number | null;
      captain: boolean;
    };
    goals: {
      total: number;
      assists: number;
    };
    shots: {
      total: number;
      on: number;
    };
    passes: {
      total: number;
      accuracy: number;
    };
    cards: {
      yellow: number;
      red: number;
    };
    tackles: {
      total: number;
      interceptions: number;
    };
    duels: {
      total: number;
      won: number;
    };
  };
}

interface PlayerStatsResponse {
  cached: boolean;
  results: number;
  paging?: any;
  response: PlayerStats[];
}

// API Functions
const fetchPlayerStats = async (params: {
  league_id?: number;
  team_id?: number;
  season?: number;
  search?: string;
  page?: number;
  force_refresh?: boolean;
}): Promise<PlayerStatsResponse> => {
  const queryParams = new URLSearchParams();
  
  if (params.league_id) queryParams.append('league_id', params.league_id.toString());
  if (params.team_id) queryParams.append('team_id', params.team_id.toString());
  if (params.season) queryParams.append('season', params.season.toString());
  if (params.search) queryParams.append('search', params.search);
  if (params.page) queryParams.append('page', params.page.toString());
  if (params.force_refresh) queryParams.append('force_refresh', 'true');
  
  const response = await fetch(`/api/v1/player-stats/fetch?${queryParams}`);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Erreur lors de la récupération des statistiques');
  }
  return response.json();
};

const fetchAvailableLeagues = async () => {
  const response = await fetch('/api/v1/player-stats/leagues');
  if (!response.ok) throw new Error('Erreur lors de la récupération des ligues');
  return response.json();
};

export default function PlayerStatistics() {
  const queryClient = useQueryClient();
  
  // États locaux
  const [selectedLeague, setSelectedLeague] = useState<number | null>(null);
  const [selectedSeason, setSelectedSeason] = useState<number>(2024);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState<'rating' | 'goals' | 'assists' | 'minutes'>('rating');
  const [filterPosition, setFilterPosition] = useState<string>('all');

  // Récupération des ligues disponibles
  const { data: leaguesData } = useQuery({
    queryKey: ['available-leagues'],
    queryFn: fetchAvailableLeagues,
    staleTime: 1000 * 60 * 60, // 1 heure
  });

  // Récupération des statistiques
  const {
    data: statsData,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['player-stats', selectedLeague, selectedSeason, searchTerm, currentPage],
    queryFn: () => fetchPlayerStats({
      league_id: selectedLeague || undefined,
      season: selectedSeason,
      search: searchTerm.length >= 4 ? searchTerm : undefined,
      page: currentPage,
    }),
    enabled: !!selectedLeague,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Mutation pour forcer le rafraîchissement
  const refreshMutation = useMutation({
    mutationFn: () => fetchPlayerStats({
      league_id: selectedLeague || undefined,
      season: selectedSeason,
      search: searchTerm.length >= 4 ? searchTerm : undefined,
      page: currentPage,
      force_refresh: true,
    }),
    onSuccess: (data) => {
      queryClient.setQueryData(
        ['player-stats', selectedLeague, selectedSeason, searchTerm, currentPage],
        data
      );
    },
  });

  // Filtrage et tri des joueurs avec gestion complète des valeurs nulles
  const filteredAndSortedPlayers = useMemo(() => {
    if (!statsData?.response) return [];
    
    let players = [...statsData.response];
    
    // Filtrer par position avec protection complète
    if (filterPosition !== 'all') {
      players = players.filter(p => p?.statistics?.games?.position === filterPosition);
    }
    
    // Trier avec gestion complète des valeurs nulles/undefined
    players.sort((a, b) => {
      let aVal = 0;
      let bVal = 0;
      
      if (sortBy === 'rating') {
        aVal = a?.statistics?.games?.rating || 0;
        bVal = b?.statistics?.games?.rating || 0;
      } else if (sortBy === 'goals') {
        aVal = a?.statistics?.goals?.total || 0;
        bVal = b?.statistics?.goals?.total || 0;
      } else if (sortBy === 'assists') {
        aVal = a?.statistics?.goals?.assists || 0;
        bVal = b?.statistics?.goals?.assists || 0;
      } else {
        aVal = a?.statistics?.games?.minutes || 0;
        bVal = b?.statistics?.games?.minutes || 0;
      }
      
      return bVal - aVal;
    });
    
    return players;
  }, [statsData, filterPosition, sortBy]);

  // Positions uniques pour le filtre
  const availablePositions = useMemo(() => {
    if (!statsData?.response) return [];
    const positions = new Set(
      statsData.response
        .map(p => p?.statistics?.games?.position)
        .filter(Boolean)
    );
    return Array.from(positions);
  }, [statsData]);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* En-tête */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Award className="w-8 h-8 text-blue-600" />
              <h1 className="text-3xl font-bold text-gray-800">
                Statistiques des Joueurs
              </h1>
            </div>
            
            {statsData?.cached && (
              <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                Données en cache
              </span>
            )}
          </div>

          {/* Filtres */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Sélection de la ligue */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ligue
              </label>
              <select
                value={selectedLeague || ''}
                onChange={(e) => {
                  setSelectedLeague(e.target.value ? parseInt(e.target.value) : null);
                  setCurrentPage(1);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Sélectionner une ligue</option>
                {leaguesData?.response?.map((league: any) => (
                  <option key={league.id} value={league.id}>
                    {league.name} ({league.country})
                  </option>
                ))}
              </select>
            </div>

            {/* Sélection de la saison */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Saison
              </label>
              <select
                value={selectedSeason}
                onChange={(e) => {
                  setSelectedSeason(parseInt(e.target.value));
                  setCurrentPage(1);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                {[2024, 2023, 2022, 2021, 2020].map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>

            {/* Recherche */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rechercher un joueur
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setCurrentPage(1);
                  }}
                  disabled={!selectedLeague}
                  placeholder={selectedLeague ? "Min. 4 caractères..." : "Sélectionnez une ligue"}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                />
              </div>
            </div>

            {/* Bouton refresh */}
            <div className="flex items-end">
              <button
                onClick={() => refreshMutation.mutate()}
                disabled={refreshMutation.isPending || !selectedLeague}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center gap-2"
              >
                <RefreshCw className={`w-5 h-5 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
                Actualiser
              </button>
            </div>
          </div>

          {/* Tri et filtres secondaires */}
          {selectedLeague && (
            <div className="flex flex-wrap gap-4 mt-4">
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-600" />
                <span className="text-sm font-medium text-gray-700">Trier par:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="rating">Note</option>
                  <option value="goals">Buts</option>
                  <option value="assists">Passes décisives</option>
                  <option value="minutes">Minutes jouées</option>
                </select>
              </div>

              {availablePositions.length > 0 && (
                <div className="flex items-center gap-2">
                  <Users className="w-5 h-5 text-gray-600" />
                  <span className="text-sm font-medium text-gray-700">Position:</span>
                  <select
                    value={filterPosition}
                    onChange={(e) => setFilterPosition(e.target.value)}
                    className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="all">Toutes</option>
                    {availablePositions.map(pos => (
                      <option key={pos} value={pos}>{pos}</option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Message d'erreur */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{(error as Error).message}</p>
          </div>
        )}

        {/* Chargement */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        )}

        {/* Liste des joueurs */}
        {!isLoading && filteredAndSortedPlayers.length > 0 && (
          <>
            <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Joueur
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Équipe
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Position
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Note
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Matchs
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Buts
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Assists
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Minutes
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Précision
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredAndSortedPlayers.map((player, index) => (
                      <tr 
                        key={player?.id ? `${player.id}-${player?.team?.id || index}` : `player-${index}`} 
                        className="hover:bg-gray-50"
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <img
                              src={player?.player?.photo || '/placeholder-player.png'}
                              alt={player?.player?.name || 'Player'}
                              className="w-10 h-10 rounded-full mr-3"
                              onError={(e) => {
                                e.currentTarget.src = '/placeholder-player.png';
                              }}
                            />
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {player?.player?.name || 'N/A'}
                              </div>
                              <div className="text-sm text-gray-500">
                                {player?.player?.age || '?'} ans • {player?.player?.nationality || 'N/A'}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <img
                              src={player?.team?.logo || '/placeholder-team.png'}
                              alt={player?.team?.name || 'Team'}
                              className="w-8 h-8 mr-2"
                              onError={(e) => {
                                e.currentTarget.src = '/placeholder-team.png';
                              }}
                            />
                            <span className="text-sm text-gray-900">{player?.team?.name || 'N/A'}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                            {player?.statistics?.games?.position || 'N/A'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          {player?.statistics?.games?.rating ? (
                            <div className="flex items-center justify-center gap-1">
                              <span className={`text-sm font-semibold ${
                                player.statistics.games.rating >= 7 ? 'text-green-600' :
                                player.statistics.games.rating >= 6 ? 'text-blue-600' :
                                'text-orange-600'
                              }`}>
                                {player.statistics.games.rating.toFixed(2)}
                              </span>
                              {player.statistics.games.rating >= 7 && (
                                <TrendingUp className="w-4 h-4 text-green-600" />
                              )}
                              {player.statistics.games.rating < 6 && (
                                <TrendingDown className="w-4 h-4 text-orange-600" />
                              )}
                            </div>
                          ) : (
                            <span className="text-sm text-gray-400">-</span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-900">
                          {player?.statistics?.games?.appearences || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          <div className="flex items-center justify-center gap-1">
                            <Target className="w-4 h-4 text-gray-400" />
                            <span className="text-sm font-semibold text-gray-900">
                              {player?.statistics?.goals?.total || 0}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-900">
                          {player?.statistics?.goals?.assists || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-900">
                          {player?.statistics?.games?.minutes || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center text-sm">
                          {player?.statistics?.passes?.accuracy ? (
                            <span className={`font-semibold ${
                              player.statistics.passes.accuracy >= 80 ? 'text-green-600' :
                              player.statistics.passes.accuracy >= 70 ? 'text-blue-600' :
                              'text-orange-600'
                            }`}>
                              {player.statistics.passes.accuracy}%
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pagination */}
            {statsData?.paging && (
              <div className="flex justify-center gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Précédent
                </button>
                <span className="px-4 py-2 bg-white border border-gray-300 rounded-lg">
                  Page {currentPage} / {statsData.paging.total}
                </span>
                <button
                  onClick={() => setCurrentPage(p => p + 1)}
                  disabled={currentPage >= statsData.paging.total}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Suivant
                </button>
              </div>
            )}
          </>
        )}

        {/* Aucun résultat */}
        {!isLoading && !error && filteredAndSortedPlayers.length === 0 && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <Award className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Aucune statistique trouvée
            </h3>
            <p className="text-gray-500">
              {!selectedLeague 
                ? "Sélectionnez une ligue pour voir les statistiques"
                : "Essayez de modifier vos filtres de recherche"
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
}