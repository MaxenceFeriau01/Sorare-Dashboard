// Exemples de composants UI de base
// Ces fichiers seront remplacés par les composants shadcn/ui

// Si shadcn n'est pas encore installé, tu peux utiliser ces composants basiques

import * as React from "react"
import { cn } from "@/lib/utils"

// ===========================================
// BUTTON
// ===========================================
export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'default' | 'destructive' | 'outline' | 'ghost'
    size?: 'default' | 'sm' | 'lg' | 'icon'
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'default', size = 'default', ...props }, ref) => {
        return (
            <button
                className={cn(
                    "inline-flex items-center justify-center rounded-md font-medium transition-colors",
                    "focus-visible:outline-none focus-visible:ring-2 disabled:opacity-50 disabled:pointer-events-none",
                    {
                        'bg-blue-600 text-white hover:bg-blue-700': variant === 'default',
                        'bg-red-600 text-white hover:bg-red-700': variant === 'destructive',
                        'border border-gray-300 bg-white hover:bg-gray-50': variant === 'outline',
                        'hover:bg-gray-100': variant === 'ghost',
                        'h-10 py-2 px-4': size === 'default',
                        'h-9 px-3 text-sm': size === 'sm',
                        'h-11 px-8': size === 'lg',
                        'h-10 w-10': size === 'icon',
                    },
                    className
                )}
                ref={ref}
                {...props}
            />
        )
    }
)
Button.displayName = "Button"

// ===========================================
// CARD
// ===========================================
const Card = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={cn(
            "rounded-lg border bg-white shadow-sm",
            className
        )}
        {...props}
    />
))
Card.displayName = "Card"

// ===========================================
// BADGE
// ===========================================
export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'outline' | 'destructive'
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
    ({ className, variant = 'default', ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
                    {
                        'bg-blue-100 text-blue-800': variant === 'default',
                        'border border-gray-200': variant === 'outline',
                        'bg-red-100 text-red-800': variant === 'destructive',
                    },
                    className
                )}
                {...props}
            />
        )
    }
)
Badge.displayName = "Badge"

// ===========================================
// SKELETON
// ===========================================
const Skeleton = ({
    className,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) => {
    return (
        <div
            className={cn("animate-pulse rounded-md bg-gray-200", className)}
            {...props}
        />
    )
}

// ===========================================
// ALERT
// ===========================================
const Alert = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement> & { variant?: 'default' | 'destructive' }
>(({ className, variant = 'default', ...props }, ref) => (
    <div
        ref={ref}
        className={cn(
            "relative w-full rounded-lg border p-4",
            {
                'bg-white': variant === 'default',
                'bg-red-50 border-red-200': variant === 'destructive',
            },
            className
        )}
        {...props}
    />
))
Alert.displayName = "Alert"

const AlertDescription = React.forwardRef<
    HTMLParagraphElement,
    React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={cn("text-sm [&_p]:leading-relaxed", className)}
        {...props}
    />
))
AlertDescription.displayName = "AlertDescription"

// ===========================================
// AVATAR
// ===========================================
const Avatar = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={cn(
            "relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full",
            className
        )}
        {...props}
    />
))
Avatar.displayName = "Avatar"

const AvatarFallback = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={cn(
            "flex h-full w-full items-center justify-center rounded-full bg-gray-100",
            className
        )}
        {...props}
    />
))
AvatarFallback.displayName = "AvatarFallback"

// Export all components
export {
    Button,
    Card,
    Badge,
    Skeleton,
    Alert,
    AlertDescription,
    Avatar,
    AvatarFallback,
}