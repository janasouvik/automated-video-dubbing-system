'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Sidebar } from '@/components/dashboard/Sidebar';
import { TopBar } from '@/components/dashboard/TopBar';
import { NewJobView } from '@/components/dashboard/NewJobView';
import { JobDetailView } from '@/components/dashboard/JobDetailView';
import { DubbingJob } from '@/lib/mock-data';

function DashboardContent() {
  const searchParams = useSearchParams();
  const initialUrl = searchParams.get('url') || '';

  // Initial state starts strictly at [] for new users
  const [jobs, setJobs] = useState<DubbingJob[]>([]);
  const [selectedJob, setSelectedJob] = useState<DubbingJob | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);

  // Fetch only this authenticated user's isolated jobs from the server
  useEffect(() => {
    let isMounted = true;

    async function loadUserJobs() {
      try {
        const res = await fetch('/api/jobs', { cache: 'no-store' });
        if (res.ok) {
          const data = await res.json();
          if (isMounted && Array.isArray(data?.jobs)) {
            setJobs(data.jobs);
          }
        }
      } catch (err) {
        console.error('Error fetching user jobs:', err);
      } finally {
        if (isMounted) setIsLoadingJobs(false);
      }
    }

    loadUserJobs();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleJobCreated = (newJob: DubbingJob) => {
    setJobs((prev) => [newJob, ...prev.filter((j) => j.id !== newJob.id)]);
  };

  const handleToggleSidebar = () => {
    if (typeof window !== 'undefined' && window.innerWidth < 768) {
      setSidebarOpen((prev) => !prev);
    } else {
      setSidebarCollapsed((prev) => !prev);
    }
  };

  return (
    <div className="flex min-h-screen bg-transparent">
      {/* Collapsible Left Sidebar */}
      <Sidebar
        jobs={jobs}
        activeJobId={selectedJob?.id || null}
        onSelectJob={(job) => {
          setSelectedJob(job);
        }}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed((prev) => !prev)}
      />

      {/* Main Panel Content Area */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          sidebarCollapsed ? 'md:pl-0' : 'md:pl-72'
        }`}
      >
        <TopBar
          onToggleSidebar={handleToggleSidebar}
          isSidebarCollapsed={sidebarCollapsed}
          activeTitle={selectedJob ? selectedJob.title : 'New Dubbing Job'}
        />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
          {selectedJob ? (
            <JobDetailView
              job={selectedJob}
              onNewJob={() => setSelectedJob(null)}
            />
          ) : (
            <NewJobView
              initialUrl={initialUrl}
              onJobCreated={handleJobCreated}
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-transparent flex items-center justify-center text-sm text-[var(--color-text-muted)]">
          Loading VanniDub Workspace...
        </div>
      }
    >
      <DashboardContent />
    </Suspense>
  );
}
