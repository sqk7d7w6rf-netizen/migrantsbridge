import { describe, expect, it } from "vitest";

import { queryKeys } from "@/lib/query-keys";

describe("queryKeys", () => {
  it("builds stable list keys including params", () => {
    expect(queryKeys.clients.list({ page: 1 })).toEqual(["clients", "list", { page: 1 }]);
  });

  it("builds detail keys scoped by id", () => {
    expect(queryKeys.cases.detail("abc")).toEqual(["cases", "detail", "abc"]);
  });

  it("exposes an all key per resource", () => {
    expect(queryKeys.documents.all).toEqual(["documents"]);
  });
});
