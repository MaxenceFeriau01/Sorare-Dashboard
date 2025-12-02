'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sorareApi, healthApi } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton, Alert, AlertDescription } from '@/components/ui/extras';
import {
    RefreshCw,
    CheckCircle,
    XCircle,
    AlertCircle,
    Loader2,
    Database,
    Users,
    Activity,
    Clock,
} from 'lucide-react';
import { formatRelativeTime, formatNumber } from '@/lib/utils';

export default function SyncPage() {
    const queryClient = useQueryClient();
    const [syncLogs, setSyncLogs] = useState<string[]>([]);

    // Vérifier la connexion au backend
    const { data: health, isLoading: healthLoading } = useQuery({
        queryKey: ['health'],
        queryFn: () => healthApi.check(),
        refetchInterval: 10000,
    });

    // Tester la connexion Sorare
    const {
        data: sorareStatus,
        isLoading: sorareLoading,
        refetch: refetchSorareStatus,
    } = useQuery({
        queryKey: ['sorare-status'],
        queryFn: () => sorareApi.testConnection(),
        retry: false,
    });

    // Mutation pour synchroniser les joueurs
    const syncMutation = useMutation({
        mutationFn: () => sorareApi.syncPlayers(),
        onSuccess: (data) => {
            setSyncLogs((prev) => [
                ...prev,
                `✅ Synchronisation réussie: ${data.players_added} joueurs ajoutés, ${data.players_updated} mis à jour`,
            ]);
            // Invalider les caches pour recharger les données
            queryClient.invalidateQueries({ queryKey: ['players-list'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
        },
        onError: (error: any) => {
            setSyncLogs((prev) => [
                ...prev,
                `❌ Erreur de synchronisation: ${error.response?.data?.detail || error.message}`,
            ]);
        },
    });

    const handleSync = () => {
        setSyncLogs((prev) => [...prev, `🔄 Démarrage de la synchronisation...`]);
        syncMutation.mutate();
    };

    const handleTestConnection = () => {
        setSyncLogs((prev) => [...prev, `🔌 Test de connexion à Sorare...`]);
        refetchSorareStatus();
    };

    const clearLogs = () => {
        setSyncLogs([]);
    };

    const backendConnected = !!health;
    const sorareConnected = sorareStatus?.status === 'connected';

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Synchronisation</h1>
                <p className="text-gray-500 mt-1">
                    Gère la synchronisation avec l'API Sorare
                </p>
            </div>

            {/* Status Cards */}
            <div className="grid gap-6 md:grid-cols-2">
                {/* Backend Status */}
                <Card className="p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold">Backend API</h3>
                        {healthLoading ? (
                            <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
                        ) : backendConnected ? (
                            <Badge className="bg-green-100 text-green-800 border-green-200">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                Connecté
                            </Badge>
                        ) : (
                            <Badge className="bg-red-100 text-red-800 border-red-200">
                                <XCircle className="h-3 w-3 mr-1" />
                                Déconnecté
                            </Badge>
                        )}
                    </div>

                    <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                            <span className="text-gray-500">URL</span>
                            <span className="font-medium">
                                {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                            </span>
                        </div>
                        {health && (
                            <div className="flex justify-between">
                                <span className="text-gray-500">Version</span>
                                <span className="font-medium">{health.version || 'N/A'}</span>
                            </div>
                        )}
                        <div className="flex justify-between">
                            <span className="text-gray-500">État</span>
                            <span className="font-medium">
                                {backendConnected ? '✅ Opérationnel' : '❌ Hors ligne'}
                            </span>
                        </div>
                    </div>

                    {!backendConnected && (
                        <Alert variant="destructive" className="mt-4">
                            <AlertCircle className="h-4 w-4" />
                            <AlertDescription>
                                Le backend n'est pas accessible. Lance-le avec: uvicorn app.main:app --reload
                            </AlertDescription>
                        </Alert>
                    )}
                </Card>

                {/* Sorare Status */}
                <Card className="p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold">API Sorare</h3>
                        {sorareLoading ? (
                            <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
                        ) : sorareConnected ? (
                            <Badge className="bg-green-100 text-green-800 border-green-200">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                Connecté
                            </Badge>
                        ) : (
                            <Badge className="bg-orange-100 text-orange-800 border-orange-200">
                                <AlertCircle className="h-3 w-3 mr-1" />
                                Non configuré
                            </Badge>
                        )}
                    </div>

                    <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                            <span className="text-gray-500">URL</span>
                            <span className="font-medium">https://api.sorare.com/graphql</span>
                        </div>
                        {sorareStatus?.email && (
                            <div className="flex justify-between">
                                <span className="text-gray-500">Email</span>
                                <span className="font-medium">{sorareStatus.email}</span>
                            </div>
                        )}
                        <div className="flex justify-between">
                            <span className="text-gray-500">État</span>
                            <span className="font-medium">
                                {sorareConnected ? '✅ Authentifié' : '⏳ En attente'}
                            </span>
                        </div>
                    </div>

                    <div className="flex gap-2 mt-4">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleTestConnection}
                            disabled={!backendConnected || sorareLoading}
                            className="flex-1"
                        >
                            {sorareLoading ? (
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            ) : (
                                <RefreshCw className="h-4 w-4 mr-2" />
                            )}
                            Tester
                        </Button>
                    </div>

                    {sorareStatus && !sorareConnected && (
                        <Alert className="mt-4">
                            <AlertCircle className="h-4 w-4" />
                            <AlertDescription>
                                {sorareStatus.message || 'Configure tes identifiants Sorare dans le .env'}
                            </AlertDescription>
                        </Alert>
                    )}
                </Card>
            </div>

            {/* Actions de synchronisation */}
            <Card className="p-6">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h3 className="text-lg font-semibold">Actions de synchronisation</h3>
                        <p className="text-sm text-gray-500 mt-1">
                            Synchronise tes données avec Sorare
                        </p>
                    </div>

                    {syncMutation.isPending && (
                        <Badge className="bg-blue-100 text-blue-800 border-blue-200">
                            <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                            En cours...
                        </Badge>
                    )}
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                    {/* Sync joueurs */}
                    <div className="p-4 border border-gray-200 rounded-lg">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="rounded-full p-2 bg-blue-50">
                                <Users className="h-5 w-5 text-blue-600" />
                            </div>
                            <div>
                                <p className="font-semibold">Joueurs</p>
                                <p className="text-xs text-gray-500">Sync cartes Sorare</p>
                            </div>
                        </div>
                        <Button
                            onClick={handleSync}
                            disabled={!backendConnected || !sorareConnected || syncMutation.isPending}
                            className="w-full"
                            size="sm"
                        >
                            {syncMutation.isPending ? (
                                <>
                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                    Synchronisation...
                                </>
                            ) : (
                                <>
                                    <RefreshCw className="h-4 w-4 mr-2" />
                                    Synchroniser
                                </>
                            )}
                        </Button>
                    </div>

                    {/* Sync blessures (à venir) */}
                    <div className="p-4 border border-gray-200 rounded-lg opacity-60">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="rounded-full p-2 bg-red-50">
                                <Activity className="h-5 w-5 text-red-600" />
                            </div>
                            <div>
                                <p className="font-semibold">Blessures</p>
                                <p className="text-xs text-gray-500">Scraping auto</p>
                            </div>
                        </div>
                        <Button disabled className="w-full" size="sm" variant="outline">
                            <Clock className="h-4 w-4 mr-2" />
                            Bientôt disponible
                        </Button>
                    </div>

                    {/* Sync stats (à venir) */}
                    <div className="p-4 border border-gray-200 rounded-lg opacity-60">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="rounded-full p-2 bg-green-50">
                                <Database className="h-5 w-5 text-green-600" />
                            </div>
                            <div>
                                <p className="font-semibold">Statistiques</p>
                                <p className="text-xs text-gray-500">Mise à jour scores</p>
                            </div>
                        </div>
                        <Button disabled className="w-full" size="sm" variant="outline">
                            <Clock className="h-4 w-4 mr-2" />
                            Bientôt disponible
                        </Button>
                    </div>
                </div>

                {!backendConnected && (
                    <Alert variant="destructive" className="mt-4">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                            Le backend doit être connecté pour effectuer une synchronisation.
                        </AlertDescription>
                    </Alert>
                )}

                {backendConnected && !sorareConnected && (
                    <Alert className="mt-4">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                            L'API Sorare n'est pas configurée. Configure tes identifiants dans le fichier .env du backend.
                        </AlertDescription>
                    </Alert>
                )}
            </Card>

            {/* Logs de synchronisation */}
            <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">Logs de synchronisation</h3>
                    {syncLogs.length > 0 && (
                        <Button variant="outline" size="sm" onClick={clearLogs}>
                            Effacer
                        </Button>
                    )}
                </div>

                {syncLogs.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                        <p>Aucun log pour le moment</p>
                        <p className="text-sm mt-1">Lance une synchronisation pour voir les logs</p>
                    </div>
                ) : (
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                        {syncLogs.map((log, index) => (
                            <div
                                key={index}
                                className="p-3 bg-gray-50 rounded-lg text-sm font-mono"
                            >
                                <span className="text-gray-500">
                                    [{new Date().toLocaleTimeString()}]
                                </span>{' '}
                                {log}
                            </div>
                        ))}
                    </div>
                )}
            </Card>

            {/* Informations */}
            <Card className="p-6 bg-blue-50 border-blue-200">
                <div className="flex gap-3">
                    <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-blue-900">
                        <p className="font-semibold mb-2">ℹ️ Informations</p>
                        <ul className="space-y-1 text-blue-800">
                            <li>• La synchronisation récupère tes cartes depuis Sorare</li>
                            <li>• Les joueurs sont automatiquement ajoutés ou mis à jour</li>
                            <li>• Tu dois avoir configuré tes identifiants Sorare dans le .env</li>
                            <li>• En attente de l'API officielle Sorare pour activer la sync</li>
                        </ul>
                    </div>
                </div>
            </Card>
        </div>
    );
}