import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    // TODO: Add GoogleProvider({ clientId: process.env.GOOGLE_CLIENT_ID!, clientSecret: process.env.GOOGLE_CLIENT_SECRET! })
    Credentials({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      authorize: async (credentials) => {
        // TODO: wire to backend API endpoint /api/v1/auth/login
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        const email = String(credentials.email).trim().toLowerCase();
        const password = String(credentials.password);

        // Simple validation rule: at least 6 characters
        if (password.length < 6) {
          return null;
        }

        // Return user object for session
        const namePart = email.split('@')[0];
        const formattedName =
          namePart.charAt(0).toUpperCase() + namePart.slice(1).replace(/[._]/g, ' ');

        return {
          id: 'usr_' + Math.random().toString(36).substring(2, 9),
          name: formattedName || 'Demo Creator',
          email: email,
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
      }
      return token;
    },
    session({ session, token }) {
      if (session.user && token.id) {
        session.user.id = token.id as string;
      }
      return session;
    },
  },
  secret: process.env.AUTH_SECRET || 'vannidub_secret_key_development_3499fd_2026',
});
