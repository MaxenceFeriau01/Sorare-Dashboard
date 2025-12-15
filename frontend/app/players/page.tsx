"use client";

import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import PlayersTabs from "@/components/players/PlayersTabs";
import { Player } from "@/app/types/api";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function PlayersPage() {
    const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const queryClient = useQueryClient();

    const handleDelete = async () => {
        if (!selectedPlayer) return;
        
        setIsDeleting(true);
        
        try {
            await axios.delete(`${API_URL}/api/v1/players/${selectedPlayer.id}`);
            alert("✅ Joueur supprimé avec succès !");
            
            // Fermer les modals
            setShowDeleteConfirm(false);
            setSelectedPlayer(null);
            
            // Rafraîchir
            queryClient.invalidateQueries({ queryKey: ["players"] });
            queryClient.invalidateQueries({ queryKey: ["leagues-stats"] });
        } catch (error: any) {
            alert("❌ Erreur: " + (error.response?.data?.detail || error.message));
        } finally {
            setIsDeleting(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* En-tête */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Mes Joueurs</h1>
                <p className="mt-2 text-gray-600">
                    Gérez votre équipe organisée par championnat
                </p>
            </div>

            {/* Onglets des joueurs */}
            <PlayersTabs onPlayerSelect={setSelectedPlayer} />

            {/* Modal de détails du joueur */}
            <Dialog open={!!selectedPlayer && !showDeleteConfirm} onOpenChange={() => setSelectedPlayer(null)}>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-white z-50">
                    {selectedPlayer && (
                        <>
                            <DialogHeader>
                                <DialogTitle className="text-2xl text-gray-900">
                                    {selectedPlayer.display_name}
                                </DialogTitle>
                            </DialogHeader>

                            <div className="space-y-6 mt-4">
                                {/* Image */}
                                {selectedPlayer.image_url && (
                                    <div className="flex justify-center">
                                        <img
                                            src={selectedPlayer.image_url}
                                            alt={selectedPlayer.display_name || "Joueur"}
                                            className="w-32 h-32 rounded-full object-cover border-4 border-gray-100"
                                        />
                                    </div>
                                )}

                                {/* Infos de base */}
                                <div>
                                    <h3 className="font-semibold text-lg mb-3 text-gray-900">Informations</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <p className="text-sm text-gray-500">Club</p>
                                            <p className="font-semibold text-gray-900">
                                                {selectedPlayer.club_name || "N/A"}
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-500">Position</p>
                                            <p className="font-semibold text-gray-900">
                                                {selectedPlayer.position || "N/A"}
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-500">Ligue</p>
                                            <p className="font-semibold text-gray-900">
                                                {selectedPlayer.league_name || "N/A"}
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-500">Pays de la ligue</p>
                                            <p className="font-semibold text-gray-900">
                                                {selectedPlayer.league_country || "N/A"}
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-500">Âge</p>
                                            <p className="font-semibold text-gray-900">
                                                {selectedPlayer.age ? `${selectedPlayer.age} ans` : "N/A"}
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-500">Nationalité</p>
                                            <p className="font-semibold text-gray-900">
                                                {selectedPlayer.country || "N/A"}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                {/* Statistiques */}
                                <div>
                                    <h3 className="font-semibold text-lg mb-3 text-gray-900">Statistiques</h3>
                                    <div className="grid grid-cols-3 gap-4 text-center">
                                        <div className="bg-blue-50 rounded-lg p-4">
                                            <p className="text-3xl font-bold text-blue-600">
                                                {selectedPlayer.average_score.toFixed(1)}
                                            </p>
                                            <p className="text-xs text-gray-600 mt-1">Score moyen</p>
                                        </div>
                                        <div className="bg-green-50 rounded-lg p-4">
                                            <p className="text-3xl font-bold text-green-600">
                                                {selectedPlayer.total_games}
                                            </p>
                                            <p className="text-xs text-gray-600 mt-1">Matchs totaux</p>
                                        </div>
                                        <div className="bg-purple-50 rounded-lg p-4">
                                            <p className="text-3xl font-bold text-purple-600">
                                                {selectedPlayer.season_games}
                                            </p>
                                            <p className="text-xs text-gray-600 mt-1">Cette saison</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Statut blessure */}
                                {selectedPlayer.is_injured && (
                                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Badge variant="destructive">🚑 Joueur blessé</Badge>
                                        </div>
                                        {selectedPlayer.injury_status && (
                                            <p className="text-sm text-red-700">
                                                {selectedPlayer.injury_status}
                                            </p>
                                        )}
                                    </div>
                                )}

                                {/* IDs */}
                                <div className="text-xs text-gray-500 space-y-1">
                                    <p>Sorare ID: {selectedPlayer.sorare_id}</p>
                                    {selectedPlayer.slug && <p>Slug: {selectedPlayer.slug}</p>}
                                </div>
                            </div>

                            {/* BOUTONS EN BAS - BIEN VISIBLES */}
                            <div className="mt-6 pt-4 border-t border-gray-200 flex justify-between gap-3">
                                <Button
                                    variant="destructive"
                                    onClick={() => setShowDeleteConfirm(true)}
                                    disabled={isDeleting}
                                    className="bg-red-600 hover:bg-red-700 text-white font-semibold"
                                >
                                    <Trash2 className="h-4 w-4 mr-2" />
                                    Supprimer
                                </Button>
                                <Button 
                                    variant="outline" 
                                    onClick={() => setSelectedPlayer(null)}
                                    className="border-gray-300"
                                >
                                    Fermer
                                </Button>
                            </div>
                        </>
                    )}
                </DialogContent>
            </Dialog>

            {/* Modal de confirmation de suppression */}
            <Dialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
                <DialogContent className="bg-white z-50">
                    <DialogHeader>
                        <DialogTitle className="text-xl text-gray-900">
                            ⚠️ Confirmer la suppression
                        </DialogTitle>
                    </DialogHeader>
                    <div className="py-4">
                        <p className="text-gray-700 text-base">
                            Êtes-vous sûr de vouloir supprimer{" "}
                            <span className="font-bold text-red-600">
                                {selectedPlayer?.display_name}
                            </span>{" "}
                            ?
                        </p>
                        <p className="text-sm text-red-600 mt-3 font-medium">
                            ⚠️ Cette action est irréversible !
                        </p>
                    </div>
                    <div className="flex justify-end gap-3 mt-4">
                        <Button
                            variant="outline"
                            onClick={() => setShowDeleteConfirm(false)}
                            disabled={isDeleting}
                        >
                            Annuler
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={handleDelete}
                            disabled={isDeleting}
                            className="bg-red-600 hover:bg-red-700"
                        >
                            {isDeleting ? "Suppression..." : "Supprimer définitivement"}
                        </Button>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}