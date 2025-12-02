'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatRelativeTime } from '@/lib/utils';
import type { DashboardStats } from '@/types/api';
import { Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface RecentUpdatesProps {
    lastUpdate: DashboardStats['last_update'];
}

export function RecentUpdates({ lastUpdate }: RecentUpdatesProps) {
    if (!lastUpdate) {
        return null;
    }

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'completed':
                return (
                    <Badge className="bg-green-100 text-green-800 border-green-200">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Terminé
                    </Badge>
                );
            case 'failed':
                return (
                    <Badge className="bg-red-100 text-red-800 border-red-200">
                        <XCircle className="h-3 w-3 mr-1" />
                        Échoué
                    </Badge>
                );
            case 'running':
                return (
                    <Badge className="bg-blue-100 text-blue-800 border-blue-200">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        En cours
                    </Badge>
                );
            default:
                return (
                    <Badge variant="outline">
                        {status}
                    </Badge>
                );
        }
    };

    const getUpdateTypeLabel = (type: string) => {
        const labels: Record<string, string> = {
            'players': 'Synchronisation des joueurs',
            'injuries': 'Mise à jour des blessures',
            'twitter': 'Scraping Twitter',
            'scraping': 'Scraping général',
        };
        return labels[type] || type;
    };

    return (
        <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                    <Clock className="h-5 w-5 text-gray-500" />
                    Dernière mise à jour
                </h3>
                {getStatusBadge(lastUpdate.status)}
            </div>

            <div className="space-y-3">
                <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">Type</span>
                    <span className="font-medium">{getUpdateTypeLabel(lastUpdate.type)}</span>
                </div>

                <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">Éléments traités</span>
                    <span className="font-medium">{lastUpdate.items_processed}</span>
                </div>

                <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">Date</span>
                    <span className="font-medium">{formatRelativeTime(lastUpdate.date)}</span>
                </div>
            </div>
        </Card>
    );
}