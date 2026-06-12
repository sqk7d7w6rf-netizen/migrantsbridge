import { z } from "zod";

export const clientFormSchema = z.object({
  first_name: z.string().min(1, "First name is required").max(150),
  last_name: z.string().min(1, "Last name is required").max(150),
  email: z.string().email("Enter a valid email address"),
  phone_numbers: z.array(z.string()).default([]),
  languages: z.array(z.string()).default([]),
  tags: z.array(z.string()).default([]),
  date_of_birth: z.string().optional().or(z.literal("")),
  nationality: z.string().optional().or(z.literal("")),
  immigration_status: z.string().optional().or(z.literal("")),
  address: z
    .object({
      street: z.string().optional().or(z.literal("")),
      city: z.string().optional().or(z.literal("")),
      state: z.string().optional().or(z.literal("")),
      zip_code: z.string().optional().or(z.literal("")),
      country: z.string().optional().or(z.literal("")),
    })
    .optional(),
  notes: z.string().optional().or(z.literal("")),
});

export type ClientFormInput = z.infer<typeof clientFormSchema>;
