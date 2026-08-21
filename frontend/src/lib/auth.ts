import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import { verifyUser } from '@/lib/userStore';

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Credentials({
      id: 'credentials',
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      authorize: async (credentials) => {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        const email = String(credentials.email).trim().toLowerCase();
        const password = String(credentials.password);

        // Verify credentials against the registered users store
        const verifiedUser = verifyUser(email, password);
        if (!verifiedUser) {
          // Account does not exist or password mismatch
          return null;
        }

        return {
          id: verifiedUser.id,
          name: verifiedUser.name,
          email: verifiedUser.email,
        };
      },
    }),
  ],
  pages: {
    signIn: '/login',
    newUser: '/signup',
  },
  session: {
    strategy: 'jwt',
  },
  callbacks: {
    jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.name = user.name;
        token.email = user.email;
      }
      return token;
    },
    session({ session, token }) {
      if (session.user) {
        if (token.id) session.user.id = token.id as string;
        if (token.name) session.user.name = token.name as string;
        if (token.email) session.user.email = token.email as string;
      }
      return session;
    },
  },
  secret: process.env.AUTH_SECRET || 'vannidub_secret_key_development_3499fd_2026',
});
