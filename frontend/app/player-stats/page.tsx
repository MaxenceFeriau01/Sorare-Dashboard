'use client';

/**
 * Page des statistiques des joueurs
 * Route: /player-stats
 */

import PlayerStatistics from '@/components/PlayerStatistics';

export default function PlayerStatsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <PlayerStatistics />
    </div>
  );
}