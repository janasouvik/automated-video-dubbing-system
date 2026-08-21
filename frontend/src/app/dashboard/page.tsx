'use client';

import React, { useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Sidebar } from '@/components/dashboard/Sidebar';
import { TopBar } from '@/components/dashboard/TopBar';
import { NewJobView } from '@/components/dashboard/NewJobView';
import { JobDetailView } from '@/components/dashboard/JobDetailView';
import { MOCK_HISTORY_JOBS, DubbingJob } from '@/lib/mock-data';

function DashboardContent() {
  const searchParams = useSearchParams();
  const initialUrl = searchParams.get('url') || '';

  const [jobs, setJobs] = useState<DubbingJob[]>(MOCK_HISTORY_JOBS);
  const [selectedJob, setSelectedJob] = useState<DubbingJob | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleJobCreated = (newJob: DubbingJob) => {
    setJobs((prev) => [newJob, ...prev.filter((j) => j.id !== newJob.id)]);
  };

  const handleToggleSidebar = () => {
    // If mobile, toggle open drawer; if desktop, toggle collapse
    if (typeof window !== 'undefined' && window.innerWidth < 768) {
      setSidebarOpen((prev) => !prev);
    } else {
      setSidebarCollapsed((prev) => !prev);
    }
  };

  return (
    <div className="flex min-h-screen bg-transparent">
      {/* Claude.ai-style Collapsible Left Sidebar */}
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
