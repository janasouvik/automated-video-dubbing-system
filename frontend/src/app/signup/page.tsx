import { Suspense } from 'react';
import { AuthLayout } from '@/components/auth/AuthLayout';
import { SignupForm } from '@/components/auth/SignupForm';

export const metadata = {
  title: 'Sign Up — VanniDub AI',
  description: 'Create a free VanniDub AI account to start automating video dubbing.',
};

export default function SignupPage() {
  return (
    <AuthLayout
      title="Create your account"
      subtitle="Start dubbing videos with AI in minutes"
    >
      <Suspense fallback={<div className="h-64 flex items-center justify-center text-xs text-[var(--color-text-muted)]">Loading signup...</div>}>
        <SignupForm />
      </Suspense>
    </AuthLayout>
  );
}
