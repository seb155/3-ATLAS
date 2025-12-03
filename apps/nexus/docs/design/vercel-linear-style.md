# Vercel/Linear Design System

> **Visual polish strategy for Nexus Phase 1.5**
> **Status:** Planning Complete | **Priority:** High
> **Timeline:** 3-4 hours implementation

---

## Overview

Transform Nexus from a functional dark-mode application into a visually impressive, polished product with **Vercel/Linear-inspired aesthetics**. Focus on Dashboard first with reusable components and smooth theme switching.

## Design Principles

### 1. Subtle, Not Flashy
- Animations: 200-300ms duration, smooth easing
- Purposeful motion that enhances UX
- No unnecessary flourishes

### 2. Depth Through Shadows
- Multi-layer shadows for visual hierarchy
- Elegant shadow system (elegant, elegant-lg, glow)
- Context-appropriate depth

### 3. Gradients Sparingly
- Accent use only, never overwhelming
- Subtle background gradients (5-10% opacity)
- Animated mesh gradients for hero sections

### 4. Typography Hierarchy
- Clear size and weight differences
- Gradient text for primary headings
- Consistent font scale

### 5. Consistent Spacing
- 4px/8px grid system
- Predictable spacing patterns
- Tailwind's default scale

### 6. Hover Feedback
- All interactive elements respond to hover
- Scale, lift, or glow effects
- Consistent transition timing

### 7. Loading States
- Skeleton loaders, never blank screens
- Shimmer animations
- Progressive content loading

### 8. Color with Purpose
- Colors indicate meaning (success, warning, error)
- Semantic color system
- High contrast for accessibility

---

## Color System

### Theme Variables

Using Tailwind CSS 4's `light-dark()` function:

```css
@theme {
  /* Core Colors - Dynamic based on theme */
  --color-background: light-dark(#ffffff, #0a0a0a);
  --color-foreground: light-dark(#171717, #ededed);
  --color-card: light-dark(#fafafa, #111111);
  --color-border: light-dark(#e5e5e5, #262626);
  --color-muted: light-dark(#f5f5f5, #171717);
  --color-muted-foreground: light-dark(#737373, #a3a3a3);

  /* Accent - Vercel Blue */
  --color-primary: #0070f3;
  --color-primary-foreground: #ffffff;

  /* Semantic Colors */
  --color-success: #0070f3;
  --color-warning: #f5a623;
  --color-error: #e00;

  /* Glass/Blur effects */
  --glass-bg: light-dark(rgba(255,255,255,0.8), rgba(17,17,17,0.8));
}
```

### Light Theme Palette
- Background: `#ffffff` (White)
- Foreground: `#171717` (Almost Black)
- Card: `#fafafa` (Off White)
- Border: `#e5e5e5` (Light Gray)
- Muted: `#f5f5f5` (Lighter Gray)

### Dark Theme Palette
- Background: `#0a0a0a` (Near Black)
- Foreground: `#ededed` (Off White)
- Card: `#111111` (Dark Gray)
- Border: `#262626` (Medium Gray)
- Muted: `#171717` (Darker Gray)

---

## Component Variants

### Card Component

**Variants:**
- `default`: Standard border with solid background
- `glass`: Backdrop blur with semi-transparent background
- `gradient`: Subtle gradient from card to muted colors
- `elevated`: Multi-layer shadows for depth

**Props:**
```typescript
interface CardProps {
  variant?: 'default' | 'glass' | 'gradient' | 'elevated'
  hover?: boolean  // Lift effect on hover
  glow?: boolean   // Primary color glow on hover
}
```

**Example Usage:**
```tsx
<Card variant="glass" hover glow>
  {/* Content */}
</Card>
```

### Button Component

**Enhanced Features:**
- `loading` state with spinner
- Icon support (left/right positioning)
- `gradient` variant: Primary to blue-600 gradient
- Scale animation: `active:scale-95`

**Props:**
```typescript
interface ButtonProps {
  loading?: boolean
  icon?: ReactNode
  iconPosition?: 'left' | 'right'
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'gradient'
}
```

### StatCard Component

**Purpose:** Display metrics with visual flair

**Features:**
- Icon with gradient background circle
- Trend indicator (arrow + color)
- Change percentage display
- Smooth number transitions
- Hover lift effect

**Props:**
```typescript
interface StatCardProps {
  title: string
  value: string | number
  change?: number      // +12.5 or -3.2
  trend?: 'up' | 'down' | 'neutral'
  icon?: ReactNode
  iconColor?: string
}
```

### Skeleton Component

**Purpose:** Loading state placeholder

**Features:**
- Shimmer animation (2s loop)
- Gradient sweep effect
- Configurable dimensions

---

## Animations

### Blob Animation

For hero sections with animated mesh gradients:

```css
@keyframes blob {
  0%, 100% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}
```

### Shimmer Animation

For skeleton loaders:

```css
@keyframes shimmer {
  100% { transform: translateX(100%); }
}

.animate-shimmer {
  animation: shimmer 2s infinite;
}
```

### Page Transitions

Fade-in and slide-up for route changes:

```tsx
<div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
  <Routes>{/* routes */}</Routes>
</div>
```

---

## Utility Classes

### Hover Effects

```css
.hover-lift {
  @apply transition-transform hover:-translate-y-1;
}

.hover-glow {
  @apply transition-shadow hover:shadow-lg hover:shadow-primary/20;
}

.hover-scale {
  @apply transition-transform hover:scale-[1.02];
}
```

### Shadows

```css
.shadow-elegant {
  box-shadow:
    0 1px 2px 0 rgb(0 0 0 / 0.05),
    0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.shadow-elegant-lg {
  box-shadow:
    0 4px 6px -1px rgb(0 0 0 / 0.1),
    0 10px 15px -3px rgb(0 0 0 / 0.1),
    0 20px 25px -5px rgb(0 0 0 / 0.1);
}

.shadow-glow {
  box-shadow: 0 0 20px -5px var(--color-primary);
}
```

### Gradient Text

```css
.text-gradient {
  @apply bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent;
}
```

### Glass Effect

```css
.glass {
  @apply bg-card/80 backdrop-blur-md border border-border/50;
}
```

---

## Dashboard Design

### Hero Section

Animated mesh gradient with blob animations:

```tsx
<div className="relative overflow-hidden rounded-2xl p-8 mb-8">
  {/* Gradient Background */}
  <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-purple-500/5 dark:from-primary/20 dark:to-purple-500/10" />

  {/* Animated Mesh Gradient */}
  <div className="absolute inset-0 opacity-30 dark:opacity-20">
    <div className="absolute top-0 -left-4 w-72 h-72 bg-primary rounded-full mix-blend-multiply filter blur-xl animate-blob" />
    <div className="absolute top-0 -right-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000" />
  </div>

  {/* Content */}
  <div className="relative z-10">
    <h1 className="text-4xl md:text-5xl font-bold text-gradient">
      Dashboard
    </h1>
    <p className="text-muted-foreground mt-2">Your Knowledge Graph Portal</p>
  </div>
</div>
```

### Stats Grid

Using StatCard components:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <StatCard
    title="Notes"
    value={0}
    change={12.5}
    trend="up"
    icon={<FileText />}
    iconColor="text-blue-500"
  />
  {/* More stats */}
</div>
```

### Activity Timeline

Vertical timeline with glass card:

```tsx
<Card variant="glass">
  <CardHeader>
    <div className="flex items-center gap-2">
      <Calendar className="h-5 w-5 text-primary" />
      <CardTitle>Recent Activity</CardTitle>
    </div>
  </CardHeader>
  <CardContent>
    <div className="relative">
      {/* Vertical line */}
      <div className="absolute left-2 top-0 bottom-0 w-px bg-border" />

      {/* Activity items */}
      {activities.map((activity, idx) => (
        <div key={idx} className="relative flex gap-4 pl-6">
          <div className="absolute left-0 top-1 w-4 h-4 rounded-full border-2 border-primary bg-background" />
          {/* Content */}
        </div>
      ))}
    </div>
  </CardContent>
</Card>
```

---

## Implementation Phases

### Phase 1: Enhanced Theme System (30 min)
- Update color system in `index.css`
- Enhance theme toggle with localStorage
- Add smooth transitions

### Phase 2: Enhanced Component Library (45 min)
- Card variants (glass, gradient, elevated)
- Button enhancements (loading, icons, gradient)
- Create StatCard component
- Create Skeleton component

### Phase 3: Dashboard Visual Overhaul (60 min)
- Hero section with animated gradients
- Stats grid with StatCard
- Activity timeline
- Feature cards with glass effect

### Phase 4: Animations & Micro-interactions (30 min)
- Page transitions
- Loading skeletons
- Hover utilities

### Phase 5: Visual Polish (30 min)
- Enhanced shadow system
- Gradient text utilities
- Glass container classes

---

## Success Criteria

### Visual Impact
- ✅ Dashboard looks polished and professional
- ✅ Smooth animations throughout (no jank)
- ✅ Clear visual hierarchy
- ✅ Premium feel with shadows/gradients/glass

### Functionality
- ✅ Theme toggle works smoothly (light/dark)
- ✅ All components are reusable
- ✅ No performance issues (<16ms frame time)
- ✅ Responsive on all screen sizes

### User Experience
- ✅ Fast and responsive interactions
- ✅ Clear feedback on all actions
- ✅ Consistent design language
- ✅ Accessible (keyboard navigation, focus states)

---

## Inspiration References

- **Vercel**: https://vercel.com
- **Linear**: https://linear.app
- **Tailwind UI**: https://tailwindui.com
- **Shadcn/ui**: https://ui.shadcn.com

---

**Document Version:** 1.0
**Created:** 2025-11-27
**Status:** Ready for implementation
