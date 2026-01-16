/**
 * Composant modal pour afficher les détails avancés d'un joueur
 */
'use client';

import React from 'react';
import { X, TrendingUp, Target, ShieldCheck, Activity, Footprints, AlertCircle } from 'lucide-react';

interface PlayerDetailsModalProps {
  player: any;
  isOpen: boolean;
  onClose: () => void;
}

export default function PlayerDetailsModal({ player, isOpen, onClose }: PlayerDetailsModalProps) {
  if (!isOpen || !player) return null;

  const stats = player.statistics;
  
  // Calcul des pourcentages
  const shotAccuracy = stats.shots.total > 0 
    ? ((stats.shots.on / stats.shots.total) * 100).toFixed(1)
    : 0;
  
  const duelSuccessRate = stats.duels.total > 0
    ? ((stats.duels.won / stats.duels.total) * 100).toFixed(1)
    : 0;
  
  const dribbleSuccessRate = stats.dribbles.attempts > 0
    ? ((stats.dribbles.success / stats.dribbles.attempts) * 100).toFixed(1)
    : 0;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* En-tête */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-800 text-white p-6">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white hover:text-gray-200"
          >
            <X className="w-6 h-6" />
          </button>
          
          <div className="flex items-start gap-4">
            <img
              src={player.player.photo}
              alt={player.player.name}
              className="w-24 h-24 rounded-full border-4 border-white"
              onError={(e) => {
                e.currentTarget.src = '/placeholder-player.png';
              }}
            />
            <div className="flex-1">
              <h2 className="text-3xl font-bold mb-2">{player.player.name}</h2>
              <div className="flex flex-wrap gap-4 text-sm">
                <div>
                  <span className="opacity-75">Équipe: </span>
                  <span className="font-semibold">{player.team.name}</span>
                </div>
                <div>
                  <span className="opacity-75">Position: </span>
                  <span className="font-semibold">{stats.games.position}</span>
                </div>
                <div>
                  <span className="opacity-75">Âge: </span>
                  <span className="font-semibold">{player.player.age} ans</span>
                </div>
                <div>
                  <span className="opacity-75">Nationalité: </span>
                  <span className="font-semibold">{player.player.nationality}</span>
                </div>
              </div>
              {stats.games.rating && (
                <div className="mt-3 inline-flex items-center gap-2 bg-white bg-opacity-20 px-4 py-2 rounded-full">
                  <Activity className="w-5 h-5" />
                  <span className="text-lg font-bold">Note: {stats.games.rating.toFixed(2)}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Corps du modal */}
        <div className="p-6 space-y-6">
          {/* Section 1: Vue d'ensemble */}
          <section>
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Activity className="w-6 h-6 text-blue-600" />
              Vue d'ensemble
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                label="Matchs joués"
                value={stats.games.appearences}
                icon="🏃"
              />
              <StatCard
                label="Titularisations"
                value={stats.games.lineups}
                icon="⭐"
              />
              <StatCard
                label="Minutes"
                value={stats.games.minutes}
                icon="⏱️"
              />
              <StatCard
                label="Remplaçant"
                value={stats.substitutes.bench}
                icon="🪑"
              />
            </div>
          </section>

          {/* Section 2: Performance offensive */}
          <section>
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Target className="w-6 h-6 text-red-600" />
              Performance offensive
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gradient-to-br from-red-50 to-orange-50 p-4 rounded-lg">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <p className="text-sm text-gray-600">Buts marqués</p>
                    <p className="text-3xl font-bold text-red-600">{stats.goals.total || 0}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Passes décisives</p>
                    <p className="text-3xl font-bold text-orange-600">{stats.goals.assists || 0}</p>
                  </div>
                </div>
                <div className="text-sm text-gray-600">
                  Ratio: {stats.games.appearences > 0 
                    ? ((stats.goals.total + stats.goals.assists) / stats.games.appearences).toFixed(2)
                    : '0.00'
                  } par match
                </div>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-purple-50 p-4 rounded-lg">
                <div className="mb-3">
                  <p className="text-sm text-gray-600">Tirs</p>
                  <div className="flex items-end gap-2">
                    <p className="text-3xl font-bold text-blue-600">{stats.shots.total || 0}</p>
                    <p className="text-lg text-purple-600 mb-1">({stats.shots.on || 0} cadrés)</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${shotAccuracy}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-gray-700">{shotAccuracy}%</span>
                </div>
              </div>
            </div>
          </section>

          {/* Section 3: Jeu de passes */}
          <section>
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Footprints className="w-6 h-6 text-green-600" />
              Jeu de passes
            </h3>
            <div className="bg-gradient-to-br from-green-50 to-teal-50 p-6 rounded-lg">
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <p className="text-sm text-gray-600">Total</p>
                  <p className="text-2xl font-bold text-green-600">{stats.passes.total || 0}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Passes clés</p>
                  <p className="text-2xl font-bold text-teal-600">{stats.passes.key || 0}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Précision</p>
                  <p className="text-2xl font-bold text-blue-600">{stats.passes.accuracy || 0}%</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-green-500 to-teal-500 h-3 rounded-full"
                    style={{ width: `${stats.passes.accuracy || 0}%` }}
                  />
                </div>
              </div>
            </div>
          </section>

          {/* Section 4: Défense et duels */}
          <section>
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <ShieldCheck className="w-6 h-6 text-indigo-600" />
              Défense et duels
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-indigo-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Tacles</p>
                <p className="text-2xl font-bold text-indigo-600">{stats.tackles.total || 0}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {stats.tackles.interceptions || 0} interceptions
                </p>
              </div>

              <div className="bg-purple-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Duels</p>
                <p className="text-2xl font-bold text-purple-600">
                  {stats.duels.won || 0}/{stats.duels.total || 0}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-purple-600 h-2 rounded-full"
                      style={{ width: `${duelSuccessRate}%` }}
                    />
                  </div>
                  <span className="text-xs font-semibold">{duelSuccessRate}%</span>
                </div>
              </div>

              <div className="bg-pink-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Dribbles</p>
                <p className="text-2xl font-bold text-pink-600">
                  {stats.dribbles.success || 0}/{stats.dribbles.attempts || 0}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-pink-600 h-2 rounded-full"
                      style={{ width: `${dribbleSuccessRate}%` }}
                    />
                  </div>
                  <span className="text-xs font-semibold">{dribbleSuccessRate}%</span>
                </div>
              </div>
            </div>
          </section>

          {/* Section 5: Discipline */}
          <section>
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <AlertCircle className="w-6 h-6 text-yellow-600" />
              Discipline
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <StatCard
                label="Cartons jaunes"
                value={stats.cards.yellow || 0}
                icon="🟨"
                color="yellow"
              />
              <StatCard
                label="Cartons rouges"
                value={stats.cards.red || 0}
                icon="🟥"
                color="red"
              />
              <StatCard
                label="Fautes commises"
                value={stats.fouls.committed || 0}
                icon="🚫"
              />
              <StatCard
                label="Fautes subies"
                value={stats.fouls.drawn || 0}
                icon="💢"
              />
              <StatCard
                label="Pénaltys obtenus"
                value={stats.penalty.won || 0}
                icon="🎯"
                color="green"
              />
            </div>
          </section>

          {/* Section 6: Informations complémentaires */}
          <section className="border-t pt-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Taille</p>
                <p className="font-semibold">{player.player.height || 'N/A'}</p>
              </div>
              <div>
                <p className="text-gray-600">Poids</p>
                <p className="font-semibold">{player.player.weight || 'N/A'}</p>
              </div>
              <div>
                <p className="text-gray-600">N° de maillot</p>
                <p className="font-semibold">{stats.games.number || 'N/A'}</p>
              </div>
              <div>
                <p className="text-gray-600">Capitaine</p>
                <p className="font-semibold">{stats.games.captain ? 'Oui' : 'Non'}</p>
              </div>
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="border-t p-4 bg-gray-50 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Saison {player.league.season} • {player.league.name}
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
}

// Composant helper pour les cartes de stats
function StatCard({ 
  label, 
  value, 
  icon, 
  color = 'blue' 
}: { 
  label: string; 
  value: number | string; 
  icon: string;
  color?: 'blue' | 'red' | 'green' | 'yellow';
}) {
  const colorClasses = {
    blue: 'from-blue-50 to-blue-100 text-blue-600',
    red: 'from-red-50 to-red-100 text-red-600',
    green: 'from-green-50 to-green-100 text-green-600',
    yellow: 'from-yellow-50 to-yellow-100 text-yellow-600',
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} p-4 rounded-lg`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
        <p className={`text-2xl font-bold ${colorClasses[color].split(' ')[2]}`}>
          {value}
        </p>
      </div>
      <p className="text-sm text-gray-600">{label}</p>
    </div>
  );
}