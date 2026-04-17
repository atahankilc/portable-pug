export const theme = {
  colors: {
    primary: "#4F46E5",
    primaryLight: "#6366F1",
    background: "#F9FAFB",
    surface: "#FFFFFF",
    text: "#111827",
    textSecondary: "#6B7280",
    border: "#E5E7EB",
    error: "#EF4444",
    success: "#10B981",
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 16,
    full: 9999,
  },
  typography: {
    h1: { fontSize: 32, fontWeight: "700" as const },
    h2: { fontSize: 24, fontWeight: "600" as const },
    h3: { fontSize: 20, fontWeight: "600" as const },
    body: { fontSize: 16, fontWeight: "400" as const },
    caption: { fontSize: 12, fontWeight: "400" as const },
  },
};

export type Theme = typeof theme;
