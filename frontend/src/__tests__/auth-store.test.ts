/**
 * Tests for src/stores/use-auth-store.ts
 *
 * localStorage and window.location are provided by jsdom.
 * axios / apiClient calls are mocked via vi.mock.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

// ── Mock apiClient before importing the store ─────────────────────────────────
vi.mock("@/lib/api-client", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

import apiClient from "@/lib/api-client";
import { useAuthStore } from "@/stores/use-auth-store";

// Helper: reset Zustand store between tests
function resetStore() {
  useAuthStore.setState({ user: null, loading: true });
}

beforeEach(() => {
  resetStore();
  localStorage.clear();
  vi.clearAllMocks();
});

// ── Initial state ─────────────────────────────────────────────────────────────

describe("initial state", () => {
  it("starts with user null and loading true", () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.loading).toBe(true);
  });
});

// ── setUser ───────────────────────────────────────────────────────────────────

describe("setUser", () => {
  it("sets a user object", () => {
    const user = {
      id: "abc-123",
      email: "test@example.com",
      first_name: "Jane",
      last_name: "Doe",
      phone: null,
      role_name: "caseworker",
      is_active: true,
    };
    useAuthStore.getState().setUser(user);
    expect(useAuthStore.getState().user).toEqual(user);
  });

  it("clears user when called with null", () => {
    useAuthStore.setState({ user: { id: "x", email: "x@x.com", first_name: "X", last_name: "X", phone: null, role_name: null, is_active: true } });
    useAuthStore.getState().setUser(null);
    expect(useAuthStore.getState().user).toBeNull();
  });
});

// ── logout ────────────────────────────────────────────────────────────────────

describe("logout", () => {
  it("clears tokens from localStorage", () => {
    localStorage.setItem("access_token", "at");
    localStorage.setItem("refresh_token", "rt");

    // Prevent actual navigation
    const originalHref = Object.getOwnPropertyDescriptor(window.location, "href");
    Object.defineProperty(window.location, "href", { writable: true, value: "/" });

    useAuthStore.getState().logout();

    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();

    if (originalHref) {
      Object.defineProperty(window.location, "href", originalHref);
    }
  });

  it("sets user to null", () => {
    useAuthStore.setState({
      user: { id: "u1", email: "u@u.com", first_name: "U", last_name: "1", phone: null, role_name: null, is_active: true },
    });

    Object.defineProperty(window.location, "href", { writable: true, value: "/" });
    useAuthStore.getState().logout();

    expect(useAuthStore.getState().user).toBeNull();
  });

  it("sets loading to false", () => {
    Object.defineProperty(window.location, "href", { writable: true, value: "/" });
    useAuthStore.getState().logout();
    expect(useAuthStore.getState().loading).toBe(false);
  });
});

// ── fetchUser ─────────────────────────────────────────────────────────────────

describe("fetchUser", () => {
  it("sets user from API when token is present", async () => {
    const mockUser = {
      id: "u1",
      email: "u@example.com",
      first_name: "Jane",
      last_name: "Doe",
      phone: null,
      role_name: "caseworker",
      is_active: true,
    };
    localStorage.setItem("access_token", "valid-token");
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockUser });

    await useAuthStore.getState().fetchUser();

    expect(useAuthStore.getState().user).toEqual(mockUser);
    expect(useAuthStore.getState().loading).toBe(false);
  });

  it("clears user and sets loading false when no token", async () => {
    await useAuthStore.getState().fetchUser();

    expect(useAuthStore.getState().user).toBeNull();
    expect(useAuthStore.getState().loading).toBe(false);
    expect(apiClient.get).not.toHaveBeenCalled();
  });

  it("clears tokens and user on API error", async () => {
    localStorage.setItem("access_token", "expired-token");
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error("Unauthorized"));

    await useAuthStore.getState().fetchUser();

    expect(useAuthStore.getState().user).toBeNull();
    expect(useAuthStore.getState().loading).toBe(false);
    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
  });
});

// ── login ─────────────────────────────────────────────────────────────────────

describe("login", () => {
  it("stores tokens and sets user on success", async () => {
    const tokens = { access_token: "at-value", refresh_token: "rt-value" };
    const mockUser = {
      id: "u2",
      email: "u@example.com",
      first_name: "Carlos",
      last_name: "Rivera",
      phone: null,
      role_name: "admin",
      is_active: true,
    };

    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: tokens });
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockUser });

    await useAuthStore.getState().login("u@example.com", "Password1!");

    expect(localStorage.getItem("access_token")).toBe("at-value");
    expect(localStorage.getItem("refresh_token")).toBe("rt-value");
    expect(useAuthStore.getState().user).toEqual(mockUser);
    expect(useAuthStore.getState().loading).toBe(false);
  });

  it("propagates API errors without storing tokens", async () => {
    vi.mocked(apiClient.post).mockRejectedValueOnce(new Error("Invalid credentials"));

    await expect(
      useAuthStore.getState().login("bad@example.com", "WrongPass1!")
    ).rejects.toThrow("Invalid credentials");

    expect(localStorage.getItem("access_token")).toBeNull();
    expect(useAuthStore.getState().user).toBeNull();
  });
});
