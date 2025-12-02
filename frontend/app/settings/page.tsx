'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/extras';
import {
    Settings,
    User,
    Bell,
    Database,
    Palette,
    Globe,
    Shield,
    Info,
    Github,
    Mail,
    ExternalLink,
    Save,
    CheckCircle,
} from 'lucide-react';

export default function SettingsPage() {
    const [saved, setSaved] = useState(false);

    // États pour les paramètres (à connecter plus tard avec un vrai backend)
    const [notifications, setNotifications] = useState({
        injuries: true,
        scores: true,
        sync: false,
    });

    const [preferences, setPreferences] = useState({
        language: 'fr',
        theme: 'light',
        dateFormat: 'dd/MM/yyyy',
    });

    const handleSave = () => {
        // TODO: Sauvegarder les paramètres dans le backend
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Paramètres</h1>
                <p className="text-gray-500 mt-1">
                    Configure ton dashboard Sorare
                </p>
            </div>

            {/* Message de succès */}
            {saved && (
                <Alert className="bg-green-50 border-green-200">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <AlertDescription className="text-green-800">
                        Paramètres sauvegardés avec succès !
                    </AlertDescription>
                </Alert>
            )}

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Colonne principale */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Profil */}
                    <Card className="p-6">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="rounded-full p-2 bg-blue-50">
                                <User className="h-5 w-5 text-blue-600" />
                            </div>
                            <div>
                                <h2 className="text-lg font-semibold">Profil</h2>
                                <p className="text-sm text-gray-500">
                                    Informations de ton compte
                                </p>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Email Sorare
                                </label>
                                <input
                                    type="email"
                                    placeholder="ton-email@sorare.com"
                                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    disabled
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    Configure ton email dans le fichier .env du backend
                                </p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Pseudo
                                </label>
                                <input
                                    type="text"
                                    placeholder="Ton pseudo"
                                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                    </Card>

                    {/* Notifications */}
                    <Card className="p-6">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="rounded-full p-2 bg-purple-50">
                                <Bell className="h-5 w-5 text-purple-600" />
                            </div>
                            <div>
                                <h2 className="text-lg font-semibold">Notifications</h2>
                                <p className="text-sm text-gray-500">
                                    Gère tes alertes et notifications
                                </p>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                                <div>
                                    <p className="font-medium">Alertes de blessures</p>
                                    <p className="text-sm text-gray-500">
                                        Reçois une notification quand un joueur se blesse
                                    </p>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={notifications.injuries}
                                        onChange={(e) =>
                                            setNotifications({ ...notifications, injuries: e.target.checked })
                                        }
                                        className="sr-only peer"
                                    />
                                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                                </label>
                            </div>

                            <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                                <div>
                                    <p className="font-medium">Scores des matchs</p>
                                    <p className="text-sm text-gray-500">
                                        Notifie quand les scores sont mis à jour
                                    </p>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={notifications.scores}
                                        onChange={(e) =>
                                            setNotifications({ ...notifications, scores: e.target.checked })
                                        }
                                        className="sr-only peer"
                                    />
                                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                                </label>
                            </div>

                            <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                                <div>
                                    <p className="font-medium">Synchronisation automatique</p>
                                    <p className="text-sm text-gray-500">
                                        Sync automatique toutes les heures
                                    </p>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={notifications.sync}
                                        onChange={(e) =>
                                            setNotifications({ ...notifications, sync: e.target.checked })
                                        }
                                        className="sr-only peer"
                                    />
                                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                                </label>
                            </div>
                        </div>
                    </Card>

                    {/* Préférences */}
                    <Card className="p-6">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="rounded-full p-2 bg-green-50">
                                <Palette className="h-5 w-5 text-green-600" />
                            </div>
                            <div>
                                <h2 className="text-lg font-semibold">Préférences</h2>
                                <p className="text-sm text-gray-500">
                                    Personnalise l'apparence de ton dashboard
                                </p>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    <Globe className="h-4 w-4 inline mr-1" />
                                    Langue
                                </label>
                                <select
                                    value={preferences.language}
                                    onChange={(e) =>
                                        setPreferences({ ...preferences, language: e.target.value })
                                    }
                                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="fr">🇫🇷 Français</option>
                                    <option value="en">🇬🇧 English</option>
                                    <option value="es">🇪🇸 Español</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    <Palette className="h-4 w-4 inline mr-1" />
                                    Thème
                                </label>
                                <select
                                    value={preferences.theme}
                                    onChange={(e) =>
                                        setPreferences({ ...preferences, theme: e.target.value })
                                    }
                                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="light">☀️ Clair</option>
                                    <option value="dark">🌙 Sombre (Bientôt)</option>
                                    <option value="auto">🔄 Automatique (Bientôt)</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Format de date
                                </label>
                                <select
                                    value={preferences.dateFormat}
                                    onChange={(e) =>
                                        setPreferences({ ...preferences, dateFormat: e.target.value })
                                    }
                                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="dd/MM/yyyy">DD/MM/YYYY (31/12/2024)</option>
                                    <option value="MM/dd/yyyy">MM/DD/YYYY (12/31/2024)</option>
                                    <option value="yyyy-MM-dd">YYYY-MM-DD (2024-12-31)</option>
                                </select>
                            </div>
                        </div>
                    </Card>

                    {/* Base de données */}
                    <Card className="p-6">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="rounded-full p-2 bg-red-50">
                                <Database className="h-5 w-5 text-red-600" />
                            </div>
                            <div>
                                <h2 className="text-lg font-semibold">Données</h2>
                                <p className="text-sm text-gray-500">
                                    Gestion de ta base de données
                                </p>
                            </div>
                        </div>

                        <div className="space-y-3">
                            <Button variant="outline" className="w-full justify-start">
                                <Database className="h-4 w-4 mr-2" />
                                Exporter les données
                            </Button>

                            <Button variant="outline" className="w-full justify-start">
                                <Shield className="h-4 w-4 mr-2" />
                                Sauvegarder la base
                            </Button>

                            <Button
                                variant="outline"
                                className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                            >
                                <Database className="h-4 w-4 mr-2" />
                                Réinitialiser toutes les données
                            </Button>
                        </div>

                        <Alert className="mt-4 bg-red-50 border-red-200">
                            <AlertDescription className="text-red-800 text-sm">
                                ⚠️ La réinitialisation supprimera toutes tes données de manière irréversible.
                            </AlertDescription>
                        </Alert>
                    </Card>

                    {/* Bouton de sauvegarde */}
                    <div className="flex justify-end gap-3">
                        <Button variant="outline">
                            Annuler
                        </Button>
                        <Button onClick={handleSave}>
                            <Save className="h-4 w-4 mr-2" />
                            Sauvegarder les modifications
                        </Button>
                    </div>
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    {/* À propos */}
                    <Card className="p-6">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="rounded-full p-2 bg-gray-50">
                                <Info className="h-5 w-5 text-gray-600" />
                            </div>
                            <h3 className="font-semibold">À propos</h3>
                        </div>

                        <div className="space-y-3 text-sm">
                            <div>
                                <p className="text-gray-500">Version</p>
                                <p className="font-medium">1.0.0</p>
                            </div>

                            <div>
                                <p className="text-gray-500">Plateforme</p>
                                <p className="font-medium">Sorare Dashboard</p>
                            </div>

                            <div>
                                <p className="text-gray-500">Développé par</p>
                                <p className="font-medium">Maxence</p>
                            </div>
                        </div>

                        <div className="mt-4 pt-4 border-t border-gray-100">
                            <Badge variant="outline" className="w-full justify-center">
                                Made with ❤️
                            </Badge>
                        </div>
                    </Card>

                    {/* Liens utiles */}
                    <Card className="p-6">
                        <h3 className="font-semibold mb-4">Liens utiles</h3>

                        <div className="space-y-2">
                            <a
                                href="https://sorare.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                <span className="text-sm">Site Sorare</span>
                                <ExternalLink className="h-4 w-4 text-gray-400" />
                            </a>

                            <a
                                href="https://github.com/sorare/api"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                <div className="flex items-center gap-2">
                                    <Github className="h-4 w-4" />
                                    <span className="text-sm">API Sorare</span>
                                </div>
                                <ExternalLink className="h-4 w-4 text-gray-400" />
                            </a>

                            <a
                                href="mailto:support@example.com"
                                className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                <div className="flex items-center gap-2">
                                    <Mail className="h-4 w-4" />
                                    <span className="text-sm">Support</span>
                                </div>
                                <ExternalLink className="h-4 w-4 text-gray-400" />
                            </a>
                        </div>
                    </Card>

                    {/* Technologies */}
                    <Card className="p-6">
                        <h3 className="font-semibold mb-4">Technologies</h3>

                        <div className="space-y-2 text-sm">
                            <div className="flex items-center justify-between">
                                <span className="text-gray-600">Frontend</span>
                                <Badge variant="outline">Next.js 14</Badge>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-gray-600">Backend</span>
                                <Badge variant="outline">FastAPI</Badge>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-gray-600">Database</span>
                                <Badge variant="outline">PostgreSQL</Badge>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-gray-600">Cache</span>
                                <Badge variant="outline">Redis</Badge>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
}