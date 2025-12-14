'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
    LayoutDashboard,
    Users,
    HeartPulse,
    Settings,
    RefreshCw,
    Plus,
} from 'lucide-react';

const menuItems = [
    {
        title: 'Dashboard',
        href: '/',
        icon: LayoutDashboard,
    },
    {
        title: 'Joueurs',
        href: '/players',
        icon: Users,
    },
    {
        title: 'Import Joueurs',
        href: '/import',
        icon: Plus,
    },
    {
        title: 'Blessures',
        href: '/injuries',
        icon: HeartPulse,
    },
    {
        title: 'Synchronisation',
        href: '/sync',
        icon: RefreshCw,
    },
    {
        title: 'Paramètres',
        href: '/settings',
        icon: Settings,
    },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="hidden w-64 border-r bg-white lg:block">
            <div className="flex h-full flex-col">
                {/* Logo */}
                <div className="flex h-16 items-center border-b px-6">
                    <Link href="/" className="flex items-center space-x-2">
                        <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600" />
                        <span className="text-xl font-bold">Sorare Dashboard</span>
                    </Link>
                </div>

                {/* Navigation */}
                <nav className="flex-1 space-y-1 p-4">
                    {menuItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = pathname === item.href;

                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    'flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                                    isActive
                                        ? 'bg-blue-50 text-blue-600'
                                        : 'text-gray-700 hover:bg-gray-100'
                                )}
                            >
                                <Icon className="h-5 w-5" />
                                <span>{item.title}</span>
                            </Link>
                        );
                    })}
                </nav>

                {/* Footer */}
                <div className="border-t p-4">
                    <div className="text-xs text-gray-500">
                        <p>Sorare Dashboard</p>
                        <p className="mt-1">Version 1.0.0</p>
                    </div>
                </div>
            </div>
        </aside>
    );
}