export const queryKeys = {
  clients: {
    all: ["clients"] as const,
    list: (params: Record<string, unknown>) => ["clients", "list", params] as const,
    detail: (id: string) => ["clients", "detail", id] as const,
  },
  cases: {
    all: ["cases"] as const,
    list: (params: Record<string, unknown>) => ["cases", "list", params] as const,
    detail: (id: string) => ["cases", "detail", id] as const,
  },
  documents: {
    all: ["documents"] as const,
    list: (params: Record<string, unknown>) => ["documents", "list", params] as const,
    detail: (id: string) => ["documents", "detail", id] as const,
  },
  appointments: {
    all: ["appointments"] as const,
    list: (params: Record<string, unknown>) => ["appointments", "list", params] as const,
    detail: (id: string) => ["appointments", "detail", id] as const,
  },
  communications: {
    all: ["communications"] as const,
    list: (params: Record<string, unknown>) => ["communications", "list", params] as const,
    detail: (id: string) => ["communications", "detail", id] as const,
  },
  invoices: {
    all: ["invoices"] as const,
    list: (params: Record<string, unknown>) => ["invoices", "list", params] as const,
    detail: (id: string) => ["invoices", "detail", id] as const,
  },
  tasks: {
    all: ["tasks"] as const,
    list: (params: Record<string, unknown>) => ["tasks", "list", params] as const,
    detail: (id: string) => ["tasks", "detail", id] as const,
  },
  workflows: {
    all: ["workflows"] as const,
    list: (params: Record<string, unknown>) => ["workflows", "list", params] as const,
    detail: (id: string) => ["workflows", "detail", id] as const,
  },
  dashboard: {
    all: ["dashboard"] as const,
    kpis: () => ["dashboard", "kpis"] as const,
    recentActivity: () => ["dashboard", "activity"] as const,
  },
  reports: {
    all: ["reports"] as const,
    clients: () => ["reports", "clients"] as const,
    cases: () => ["reports", "cases"] as const,
    financial: () => ["reports", "financial"] as const,
  },
  wealth: {
    all: ["wealth"] as const,
    dashboard: () => ["wealth", "dashboard"] as const,
    goals: () => ["wealth", "goals"] as const,
    goal: (id: string) => ["wealth", "goals", id] as const,
    savings: () => ["wealth", "savings"] as const,
    investments: () => ["wealth", "investments"] as const,
    assets: () => ["wealth", "assets"] as const,
  },
} as const;
