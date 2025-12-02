'use client';

import { useQuery } from '@tanstack/react-query';
import { healthApi } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Bell, Menu } from 'lucide-react';

export function Header() {
    // Vérifier la connexion au backend
    const { data: health, isLoading } = useQuery({
        queryKey: ['health'],
        queryFn: () => healthApi.check(),
        refetchInterval: 30000, // Vérifier toutes les 30 secondes
        retry: false,
    });

    return (
        <header className="flex h-16 items-center justify-between border-b bg-white px-6">
            {/* Left side */}
            <div className="flex items-center space-x-4">
                <Button variant="ghost" size="icon" className="lg:hidden">
                    <Menu className="h-5 w-5" />
                </Button>

                {/* Status du backend */}
                {isLoading ? (
                    <Badge variant="outline" className="animate-pulse">
                        Connexion...
                    </Badge>
                ) : health ? (
                    <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                        ● Backend connecté
                    </Badge>
                ) : (
                    <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
                        ● Backend déconnecté
                    </Badge>
                )}
            </div>

            {/* Right side */}
            <div className="flex items-center space-x-4">
                {/* Notifications (à implémenter plus tard) */}
                <Button variant="ghost" size="icon">
                    <Bell className="h-5 w-5" />
                </Button>

                {/* Avatar utilisateur (à implémenter plus tard) */}
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-600 to-purple-600" />
            </div>
        </header>
    );
}