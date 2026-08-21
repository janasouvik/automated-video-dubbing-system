import React from 'react';

export const metadata = {
  title: 'Dashboard — VanniDub AI',
  description: 'Manage automated video dubbing pipelines and view project results.',
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-transparent flex flex-col">
      {children}
    </div>
  );
}
