'use client';

import { useQuery } from '@tanstack/react-query';
import { statsApi, playersApi } from '@/lib/api';
import { StatsCards } from '@/components/dashboard/stats-cards';
import { PositionChart } from '@/components/dashboard/position-chart';
import { RecentUpdates } from '@/components/dashboard/recent-updates';
import { UpcomingMatchesPredictions } from '@/components/dashboard/upcoming-matches-predictions';
import UpcomingMatchesWithResults from '@/components/dashboard/UpcomingMatchesWithResults';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

export default function DashboardPage() {
  // Récupérer les stats du dashboard
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
  } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => statsApi.getDashboard(),
    refetchInterval: 60000, // Actualiser toutes les minutes
  });

  // Récupérer tous les joueurs pour avoir la liste complète
  const {
    data: playersData,
    isLoading: playersLoading,
  } = useQuery({
    queryKey: ['players-list'],
    queryFn: () => playersApi.getAll({ limit: 500 }),
  });

  if (statsError) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-gray-500 mt-1">Vue d'ensemble de ton équipe Sorare</p>
        </div>

        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Impossible de charger les données du dashboard. Vérifie que le backend est lancé sur http://localhost:8000
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (statsLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-gray-500 mt-1">Vue d'ensemble de ton équipe Sorare</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Skeleton className="h-96" />
          <Skeleton className="h-96" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-500 mt-1">Vue d'ensemble de ton équipe Sorare</p>
      </div>

      {/* Message si pas de données */}
      {stats && stats.overview.total_players === 0 && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Aucun joueur trouvé. Commence par synchroniser tes joueurs Sorare ou ajoute-les manuellement.
          </AlertDescription>
        </Alert>
      )}

      {/* Cartes de stats */}
      {stats && <StatsCards stats={stats.overview} />}

      {/* Prédictions des prochains matchs */}
      <UpcomingMatchesPredictions />

      {/* Graphiques et listes */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* 🆕 PROCHAINS MATCHS AVEC RÉSULTATS */}
        <UpcomingMatchesWithResults />

        {/* Distribution par position */}
        {stats && (
          <PositionChart
            distribution={stats.position_distribution}
            isLoading={statsLoading}
          />
        )}
      </div>

      {/* Dernières mises à jour */}
      {stats && stats.last_update && (
        <RecentUpdates lastUpdate={stats.last_update} />
      )}
    </div>
  );
}