/** Design tokens mirrored from Tailwind @theme for JS usage (charts, motion, etc.). */
export const theme = {
  colors: {
    ink: '#0f1c18',
    inkMuted: '#3d5249',
    surface: '#f4f7f5',
    surfaceElevated: '#ffffff',
    border: '#d5e0db',
    accent: '#1a6b4a',
    accentHover: '#14553a',
    accentSoft: '#e4f2eb',
    danger: '#b42318',
    warning: '#b54708',
  },
  fonts: {
    sans: '"DM Sans", ui-sans-serif, system-ui, sans-serif',
    display: '"Fraunces", ui-serif, Georgia, serif',
  },
  motion: {
    page: { duration: 0.35, ease: [0.22, 1, 0.36, 1] },
    fade: { duration: 0.25, ease: 'easeOut' },
  },
}
