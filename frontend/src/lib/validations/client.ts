import { z } from "zod";

export const clientFormSchema = z.object({
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  email: z.string().email("Invalid email address").optional().or(z.literal("")),
  phone_numbers: z.array(z.string()).default([]),
  date_of_birth: z.string().optional(),
  nationality: z.string().optional(),
  immigration_status: z.string().optional(),
  languages: z.array(z.string()).default([]),
  address: z.object({
    street: z.string().optional(),
    city: z.string().optional(),
    state: z.string().optional(),
    zip_code: z.string().optional(),
    country: z.string().optional(),
  }).optional(),
  notes: z.string().optional(),
  tags: z.array(z.string()).default([]),
});

export type ClientFormInput = z.infer<typeof clientFormSchema>;
