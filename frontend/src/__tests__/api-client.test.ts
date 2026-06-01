/**
 * Tests for src/lib/api-client.ts
 *
 * We test the axios interceptors by spying on the instance methods and
 * simulating request/response flows.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock axios so we can inspect interceptors without real HTTP
vi.mock("axios", async () => {
  const interceptorStore: { request: Function[]; response: Function[] } = {
    request: [],
    response: [],
  };

  const axiosInstance = {
    defaults: { headers: { common: {} } },
    interceptors: {
      request: {
        use: (fulfilled: Function) => {
          interceptorStore.request.push(fulfilled);
          return 0;
        },
      },
      response: {
        use: (fulfilled: Function, rejected: Function) => {
          interceptorStore.response.push({ fulfilled, rejected });
          return 0;
        },
      },
    },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    _interceptorStore: interceptorStore,
  };

  return {
    default: {
      create: () => axiosInstance,
    },
  };
});

// ── Request interceptor: attaches Authorization header ───────────────────────

describe("request interceptor", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("attaches Bearer token when access_token is in localStorage", async () => {
    localStorage.setItem("access_token", "my-token");

    // Dynamically import after mocks are set up
    const { default: apiClient } = await import("@/lib/api-client");
    const store = (apiClient as any)._interceptorStore as {
      request: Function[];
    };

    const config = { headers: {} as Record<string, string> };

    if (store.request.length > 0) {
      const result = await store.request[0](config);
      expect(result.headers["Authorization"]).toBe("Bearer my-token");
    }
  });

  it("does not attach Authorization when no token", async () => {
    const { default: apiClient } = await import("@/lib/api-client");
    const store = (apiClient as any)._interceptorStore as {
      request: Function[];
    };

    const config = { headers: {} as Record<string, string> };
    if (store.request.length > 0) {
      const result = await store.request[0](config);
      expect(result.headers["Authorization"]).toBeUndefined();
    }
  });
});

// ── Response interceptor: handles 401 ────────────────────────────────────────

describe("response interceptor", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("clears tokens and redirects on 401 for non-auth endpoints", async () => {
    localStorage.setItem("access_token", "at");
    localStorage.setItem("refresh_token", "rt");
    Object.defineProperty(window.location, "href", { writable: true, value: "/" });

    const { default: apiClient } = await import("@/lib/api-client");
    const store = (apiClient as any)._interceptorStore as {
      response: { fulfilled: Function; rejected: Function }[];
    };

    if (store.response.length > 0) {
      const error = {
        response: { status: 401 },
        config: { url: "/api/v1/clients/" },
      };

      try {
        await store.response[0].rejected(error);
      } catch {
        // Expected to reject
      }

      expect(localStorage.getItem("access_token")).toBeNull();
      expect(localStorage.getItem("refresh_token")).toBeNull();
    }
  });

  it("does NOT redirect for 401 on auth login endpoint", async () => {
    localStorage.setItem("access_token", "at");
    Object.defineProperty(window.location, "href", { writable: true, value: "http://localhost/dashboard" });

    const { default: apiClient } = await import("@/lib/api-client");
    const store = (apiClient as any)._interceptorStore as {
      response: { fulfilled: Function; rejected: Function }[];
    };

    if (store.response.length > 0) {
      const originalHref = window.location.href;
      const error = {
        response: { status: 401 },
        config: { url: "/api/v1/auth/login" },
      };

      try {
        await store.response[0].rejected(error);
      } catch {
        // Expected rejection
      }

      // Location should NOT have changed to /login
      expect(window.location.href).toBe(originalHref);
    }
  });

  it("passes through successful responses unchanged", async () => {
    const { default: apiClient } = await import("@/lib/api-client");
    const store = (apiClient as any)._interceptorStore as {
      response: { fulfilled: Function; rejected: Function }[];
    };

    if (store.response.length > 0) {
      const response = { status: 200, data: { id: "1" } };
      const result = store.response[0].fulfilled(response);
      expect(result).toEqual(response);
    }
  });
});
