'use client';

import { Card } from '@/components/ui/card';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { translatePosition } from '@/lib/utils';
import type { DashboardStats } from '@/types/api';

interface PositionChartProps {
    distribution: DashboardStats['position_distribution'];
    isLoading?: boolean;
}

const COLORS = {
    'Goalkeeper': '#fbbf24',
    'Defender': '#3b82f6',
    'Midfielder': '#10b981',
    'Forward': '#ef4444',
};

export function PositionChart({ distribution, isLoading }: PositionChartProps) {
    if (isLoading) {
        return (
            <Card className="p-6">
                <div className="animate-pulse">
                    <div className="h-6 w-48 bg-gray-200 rounded mb-4" />
                    <div className="h-64 bg-gray-100 rounded" />
                </div>
            </Card>
        );
    }

    // Transformer les données pour Recharts
    const chartData = Object.entries(distribution).map(([position, count]) => ({
        name: translatePosition(position),
        value: count,
        color: COLORS[position as keyof typeof COLORS] || '#6b7280',
    }));

    const total = chartData.reduce((sum, item) => sum + item.value, 0);

    return (
        <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Distribution par Position</h3>

            {total === 0 ? (
                <div className="text-center py-16 text-gray-500">
                    <p>Aucune donnée de position</p>
                </div>
            ) : (
                <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={chartData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            )}

            {/* Stats détaillées */}
            {total > 0 && (
                <div className="mt-4 grid grid-cols-2 gap-3">
                    {chartData.map((item) => (
                        <div key={item.name} className="flex items-center justify-between p-2 rounded-lg bg-gray-50">
                            <div className="flex items-center gap-2">
                                <div
                                    className="w-3 h-3 rounded-full"
                                    style={{ backgroundColor: item.color }}
                                />
                                <span className="text-sm font-medium">{item.name}</span>
                            </div>
                            <span className="text-sm font-bold">{item.value}</span>
                        </div>
                    ))}
                </div>
            )}
        </Card>
    );
}