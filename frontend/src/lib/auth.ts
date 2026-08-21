import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import Google from 'next-auth/providers/google';

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    ...(process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET
      ? [
          Google({
            clientId: process.env.GOOGLE_CLIENT_ID,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET,
          }),
        ]
      : []),
    Credentials({
      id: 'credentials',
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
        name: { label: 'Name', type: 'text' },
      },
      authorize: async (credentials) => {
        if (!credentials?.email) {
          return null;
        }

        const email = String(credentials.email).trim().toLowerCase();
        const password = String(credentials.password || '');
        const providedName = credentials.name ? String(credentials.name).trim() : '';

        // Validate password unless it's a simulated OAuth sign-in
        if (password && password.length < 6 && !email.includes('google')) {
          return null;
        }

        const namePart = email.split('@')[0];
        const formattedName =
          providedName ||
          namePart.charAt(0).toUpperCase() + namePart.slice(1).replace(/[._]/g, ' ');

        return {
          id: 'usr_' + Math.random().toString(36).substring(2, 9),
          name: formattedName || 'Creator',
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
