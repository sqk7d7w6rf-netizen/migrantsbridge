export const queryKeys = {
  dashboard: {
    all: ["dashboard"] as const,
    kpis: (params?: object) => ["dashboard", "kpis", params] as const,
    recentActivity: (params?: object) => ["dashboard", "recent-activity", params] as const,
  },
  clients: {
    all: ["clients"] as const,
    list: (params?: object) => ["clients", "list", params] as const,
    detail: (id: string) => ["clients", id] as const,
  },
  cases: {
    all: ["cases"] as const,
    list: (params?: object) => ["cases", "list", params] as const,
    detail: (id: string) => ["cases", id] as const,
  },
  documents: {
    all: ["documents"] as const,
    list: (params?: object) => ["documents", "list", params] as const,
    detail: (id: string) => ["documents", id] as const,
  },
  appointments: {
    all: ["appointments"] as const,
    list: (params?: object) => ["appointments", "list", params] as const,
    detail: (id: string) => ["appointments", id] as const,
  },
  communications: {
    all: ["communications"] as const,
    list: (params?: object) => ["communications", "list", params] as const,
    detail: (id: string) => ["communications", id] as const,
  },
  tasks: {
    all: ["tasks"] as const,
    list: (params?: object) => ["tasks", "list", params] as const,
    detail: (id: string) => ["tasks", id] as const,
  },
  invoices: {
    all: ["invoices"] as const,
    list: (params?: object) => ["invoices", "list", params] as const,
    detail: (id: string) => ["invoices", id] as const,
  },
  workflows: {
    all: ["workflows"] as const,
    list: (params?: object) => ["workflows", "list", params] as const,
    detail: (id: string) => ["workflows", id] as const,
  },
  wealth: {
    all: ["wealth"] as const,
    goals: (params?: object) => ["wealth", "goals", params] as const,
    goal: (id: string) => ["wealth", "goals", id] as const,
    savings: (params?: object) => ["wealth", "savings", params] as const,
    investments: (params?: object) => ["wealth", "investments", params] as const,
  },
  reports: {
    clients: (params?: object) => ["reports", "clients", params] as const,
    cases: (params?: object) => ["reports", "cases", params] as const,
    financial: (params?: object) => ["reports", "financial", params] as const,
  },
};
