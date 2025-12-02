'use client';

import { Card } from '@/components/ui/card';
import { Users, UserCheck, HeartPulse, TrendingUp } from 'lucide-react';
import { formatNumber, formatScore } from '@/lib/utils';
import type { DashboardStats } from '@/types/api';

interface StatsCardsProps {
    stats: DashboardStats['overview'];
}

export function StatsCards({ stats }: StatsCardsProps) {
    const cards = [
        {
            title: 'Total Joueurs',
            value: formatNumber(stats.total_players),
            icon: Users,
            color: 'text-blue-600',
            bgColor: 'bg-blue-50',
        },
        {
            title: 'Joueurs Actifs',
            value: formatNumber(stats.active_players),
            icon: UserCheck,
            color: 'text-green-600',
            bgColor: 'bg-green-50',
        },
        {
            title: 'Joueurs Blessés',
            value: formatNumber(stats.injured_players),
            icon: HeartPulse,
            color: 'text-red-600',
            bgColor: 'bg-red-50',
        },
        {
            title: 'Score Moyen',
            value: formatScore(stats.avg_team_score),
            icon: TrendingUp,
            color: 'text-purple-600',
            bgColor: 'bg-purple-50',
        },
    ];

    return (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {cards.map((card) => {
                const Icon = card.icon;
                return (
                    <Card key={card.title} className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-500">{card.title}</p>
                                <p className="mt-2 text-3xl font-bold">{card.value}</p>
                            </div>
                            <div className={`rounded-full p-3 ${card.bgColor}`}>
                                <Icon className={`h-6 w-6 ${card.color}`} />
                            </div>
                        </div>
                    </Card>
                );
            })}
        </div>
    );
}