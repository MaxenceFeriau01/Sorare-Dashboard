// Utilitaires divers pour le frontend

import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';

/**
 * Combine les classes CSS avec Tailwind
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Formate une date en format français
 */
export function formatDate(date: string | null | undefined, formatStr: string = 'dd/MM/yyyy'): string {
  if (!date) return '-';
  try {
    return format(parseISO(date), formatStr, { locale: fr });
  } catch {
    return '-';
  }
}

/**
 * Formate une date en "il y a X temps"
 */
export function formatRelativeTime(date: string | null | undefined): string {
  if (!date) return '-';
  try {
    return formatDistanceToNow(parseISO(date), { addSuffix: true, locale: fr });
  } catch {
    return '-';
  }
}

/**
 * Formate un score avec 2 décimales
 */
export function formatScore(score: number | null | undefined): string {
  if (score === null || score === undefined) return '-';
  return score.toFixed(2);
}

/**
 * Retourne la couleur pour un score
 */
export function getScoreColor(score: number): string {
  if (score >= 60) return 'text-green-600';
  if (score >= 45) return 'text-blue-600';
  if (score >= 30) return 'text-yellow-600';
  return 'text-red-600';
}

/**
 * Retourne le badge de couleur pour une position
 */
export function getPositionBadge(position: string | null): string {
  if (!position) return 'bg-gray-100 text-gray-800';

  const pos = position.toLowerCase();

  if (pos.includes('goalkeeper') || pos.includes('gardien')) {
    return 'bg-yellow-100 text-yellow-800';
  }
  if (pos.includes('defender') || pos.includes('défense')) {
    return 'bg-blue-100 text-blue-800';
  }
  if (pos.includes('midfielder') || pos.includes('milieu')) {
    return 'bg-green-100 text-green-800';
  }
  if (pos.includes('forward') || pos.includes('attaquant')) {
    return 'bg-red-100 text-red-800';
  }

  return 'bg-gray-100 text-gray-800';
}

/**
 * Traduit une position en français
 */
export function translatePosition(position: string | null): string {
  if (!position) return '-';

  const translations: Record<string, string> = {
    'Goalkeeper': 'Gardien',
    'Defender': 'Défenseur',
    'Midfielder': 'Milieu',
    'Forward': 'Attaquant',
  };

  return translations[position] || position;
}

/**
 * Retourne la couleur pour la sévérité d'une blessure
 */
export function getSeverityColor(severity: string | null): string {
  if (!severity) return 'bg-gray-100 text-gray-800';

  const sev = severity.toLowerCase();

  if (sev === 'minor' || sev === 'légère') {
    return 'bg-yellow-100 text-yellow-800';
  }
  if (sev === 'moderate' || sev === 'modérée') {
    return 'bg-orange-100 text-orange-800';
  }
  if (sev === 'severe' || sev === 'grave') {
    return 'bg-red-100 text-red-800';
  }

  return 'bg-gray-100 text-gray-800';
}

/**
 * Traduit la sévérité en français
 */
export function translateSeverity(severity: string | null): string {
  if (!severity) return '-';

  const translations: Record<string, string> = {
    'Minor': 'Légère',
    'Moderate': 'Modérée',
    'Severe': 'Grave',
  };

  return translations[severity] || severity;
}

/**
 * Tronque un texte à une longueur donnée
 */
export function truncate(text: string | null | undefined, length: number = 50): string {
  if (!text) return '-';
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
}

/**
 * Génère des initiales à partir d'un nom
 */
export function getInitials(name: string | null | undefined): string {
  if (!name) return '?';

  const parts = name.split(' ');
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();

  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/**
 * Retourne un emoji de drapeau pour un code pays
 */
export function getFlagEmoji(countryCode: string | null): string {
  if (!countryCode || countryCode.length !== 2) return '🏴';

  const codePoints = countryCode
    .toUpperCase()
    .split('')
    .map(char => 127397 + char.charCodeAt(0));

  return String.fromCodePoint(...codePoints);
}

/**
 * Formate un nombre avec des espaces (ex: 1000 -> 1 000)
 */
export function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return '-';
  return num.toLocaleString('fr-FR');
}

/**
 * Retourne l'URL de l'avatar par défaut si pas d'image
 */
export function getPlayerAvatar(imageUrl: string | null, name: string | null): string {
  if (imageUrl) return imageUrl;

  // Utiliser UI Avatars comme fallback
  const initials = getInitials(name);
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(initials)}&background=random&size=200`;
}