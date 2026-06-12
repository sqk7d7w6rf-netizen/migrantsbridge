import { queryKeys } from "../query-keys";

describe("queryKeys", () => {
  describe("dashboard", () => {
    it("all key is stable", () => {
      expect(queryKeys.dashboard.all).toEqual(["dashboard"]);
    });

    it("kpis key includes params", () => {
      const key = queryKeys.dashboard.kpis({ page: 1 });
      expect(key[0]).toBe("dashboard");
      expect(key[1]).toBe("kpis");
      expect(key[2]).toEqual({ page: 1 });
    });

    it("recentActivity key includes params", () => {
      const key = queryKeys.dashboard.recentActivity({ limit: 5 });
      expect(key).toContain("recent-activity");
    });
  });

  describe("clients", () => {
    it("all key", () => {
      expect(queryKeys.clients.all).toEqual(["clients"]);
    });

    it("list key with params", () => {
      const key = queryKeys.clients.list({ page: 2 });
      expect(key[0]).toBe("clients");
      expect(key[1]).toBe("list");
    });

    it("detail key contains id", () => {
      const key = queryKeys.clients.detail("abc-123");
      expect(key).toContain("abc-123");
    });
  });

  describe("cases", () => {
    it("detail key is unique per id", () => {
      const k1 = queryKeys.cases.detail("id-1");
      const k2 = queryKeys.cases.detail("id-2");
      expect(k1).not.toEqual(k2);
    });
  });

  describe("wealth", () => {
    it("goal key contains id", () => {
      const key = queryKeys.wealth.goal("goal-99");
      expect(key).toContain("goal-99");
    });

    it("goals and goal are distinct", () => {
      const goals = queryKeys.wealth.goals();
      const goal = queryKeys.wealth.goal("x");
      expect(goals).not.toEqual(goal);
    });
  });

  describe("reports", () => {
    it("different report types are distinct", () => {
      const clients = queryKeys.reports.clients();
      const cases = queryKeys.reports.cases();
      const financial = queryKeys.reports.financial();
      const allKeys = [clients[1], cases[1], financial[1]];
      expect(new Set(allKeys).size).toBe(3);
    });
  });

  describe("key uniqueness across namespaces", () => {
    it("no two namespace .all keys are equal", () => {
      const allKeys = [
        queryKeys.clients.all,
        queryKeys.cases.all,
        queryKeys.documents.all,
        queryKeys.appointments.all,
        queryKeys.tasks.all,
        queryKeys.invoices.all,
        queryKeys.workflows.all,
        queryKeys.wealth.all,
        queryKeys.communications.all,
      ];
      const serialised = allKeys.map(k => JSON.stringify(k));
      expect(new Set(serialised).size).toBe(allKeys.length);
    });
  });
});
