import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";

// Primary auth is JWT-based via the backend (/auth/login) and stored in
// localStorage by the auth store. This NextAuth setup backs the
// /api/auth/[...nextauth] route with a Credentials provider that delegates
// to the same backend endpoint, so session-cookie auth also works.
export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Credentials({
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const backendUrl =
          process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";
        try {
          const res = await fetch(`${backendUrl}/api/v1/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials?.email,
              password: credentials?.password,
            }),
          });
          if (!res.ok) return null;
          const data = await res.json();
          if (!data?.access_token) return null;

          const meRes = await fetch(`${backendUrl}/api/v1/auth/me`, {
            headers: { Authorization: `Bearer ${data.access_token}` },
          });
          if (!meRes.ok) return null;
          const user = await meRes.json();
          return {
            id: user.id,
            email: user.email,
            name: `${user.first_name} ${user.last_name}`.trim(),
          };
        } catch {
          return null;
        }
      },
    }),
  ],
  session: { strategy: "jwt" },
  pages: { signIn: "/login" },
});
