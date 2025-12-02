'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { formatScore, translatePosition, getPositionBadge, getInitials } from '@/lib/utils';
import type { DashboardStats } from '@/types/api';
import { Trophy } from 'lucide-react';

interface TopPlayersProps {
    players: DashboardStats['top_players'];
    isLoading?: boolean;
}

export function TopPlayers({ players, isLoading }: TopPlayersProps) {
    if (isLoading) {
        return (
            <Card className="p-6">
                <div className="animate-pulse space-y-4">
                    <div className="h-6 w-32 bg-gray-200 rounded" />
                    <div className="space-y-3">
                        {[...Array(5)].map((_, i) => (
                            <div key={i} className="h-16 bg-gray-100 rounded" />
                        ))}
                    </div>
                </div>
            </Card>
        );
    }

    return (
        <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                    <Trophy className="h-5 w-5 text-yellow-500" />
                    Top 5 Joueurs
                </h3>
            </div>

            {players.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                    <p>Aucun joueur avec un score</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {players.map((player, index) => (
                        <div
                            key={player.id}
                            className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                            <div className="flex items-center space-x-3 flex-1">
                                {/* Rang */}
                                <div className="flex-shrink-0 w-6 text-center">
                                    <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                                </div>

                                {/* Avatar */}
                                <Avatar className="h-10 w-10">
                                    <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white">
                                        {getInitials(player.name)}
                                    </AvatarFallback>
                                </Avatar>

                                {/* Infos joueur */}
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium truncate">{player.name}</p>
                                    <p className="text-sm text-gray-500 truncate">{player.club}</p>
                                </div>

                                {/* Position */}
                                <Badge className={getPositionBadge(player.position)} variant="outline">
                                    {translatePosition(player.position)}
                                </Badge>

                                {/* Score */}
                                <div className="text-right">
                                    <p className="text-lg font-bold text-blue-600">{formatScore(player.score)}</p>
                                    <p className="text-xs text-gray-500">{player.games} matchs</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </Card>
    );
}