import { describe, expect, it } from "vitest";

import { clientFormSchema } from "@/lib/validations/client";

const valid = {
  first_name: "Ada",
  last_name: "Lovelace",
  email: "ada@example.com",
};

describe("clientFormSchema", () => {
  it("accepts a minimal valid client and applies array defaults", () => {
    const parsed = clientFormSchema.parse(valid);
    expect(parsed.phone_numbers).toEqual([]);
    expect(parsed.languages).toEqual([]);
    expect(parsed.tags).toEqual([]);
  });

  it("rejects a missing first name", () => {
    const result = clientFormSchema.safeParse({ ...valid, first_name: "" });
    expect(result.success).toBe(false);
  });

  it("rejects an invalid email", () => {
    const result = clientFormSchema.safeParse({ ...valid, email: "nope" });
    expect(result.success).toBe(false);
  });

  it("allows empty-string optional fields", () => {
    const result = clientFormSchema.safeParse({
      ...valid,
      date_of_birth: "",
      nationality: "",
    });
    expect(result.success).toBe(true);
  });
});
