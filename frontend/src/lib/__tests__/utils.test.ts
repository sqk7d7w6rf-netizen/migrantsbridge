import { cn } from "../utils";

describe("cn (className merger)", () => {
  it("returns a single class unchanged", () => {
    expect(cn("foo")).toBe("foo");
  });

  it("merges multiple classes", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("deduplicates conflicting tailwind utilities", () => {
    // tailwind-merge collapses conflicting padding utilities
    expect(cn("p-2", "p-4")).toBe("p-4");
  });

  it("removes conflicting text colours", () => {
    expect(cn("text-red-500", "text-blue-500")).toBe("text-blue-500");
  });

  it("ignores falsy values", () => {
    expect(cn("foo", false, null, undefined, "bar")).toBe("foo bar");
  });

  it("handles conditional objects from clsx", () => {
    expect(cn({ "font-bold": true, "italic": false })).toBe("font-bold");
  });

  it("handles array inputs", () => {
    expect(cn(["px-2", "py-1"])).toBe("px-2 py-1");
  });

  it("returns empty string when all values are falsy", () => {
    expect(cn(false, null, undefined)).toBe("");
  });
});
