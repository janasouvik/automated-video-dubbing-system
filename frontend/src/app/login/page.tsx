import { Suspense } from 'react';
import { AuthLayout } from '@/components/auth/AuthLayout';
import { LoginForm } from '@/components/auth/LoginForm';

export const metadata = {
  title: 'Log In — VanniDub AI',
  description: 'Sign in to access your VanniDub AI dashboard and video dubbing projects.',
};

export default function LoginPage() {
  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to your VanniDub AI workspace"
    >
      <Suspense fallback={<div className="h-64 flex items-center justify-center text-xs text-[var(--color-text-muted)]">Loading login...</div>}>
        <LoginForm />
      </Suspense>
    </AuthLayout>
  );
}
