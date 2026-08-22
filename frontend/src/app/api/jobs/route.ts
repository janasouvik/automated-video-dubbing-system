import { NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { mapToDubbingJob } from '@/lib/api';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const session = await auth();
    if (!session?.user?.email) {
      return NextResponse.json({ jobs: [] }, { status: 200 });
    }

    const email = session.user.email;
    const res = await fetch(
      `${BACKEND_URL}/api/v1/jobs?user_email=${encodeURIComponent(email)}&limit=100`,
      { cache: 'no-store' }
    );

    if (!res.ok) {
      console.error('FastAPI returned error fetching jobs:', res.status);
      return NextResponse.json({ jobs: [] }, { status: 200 });
    }

    const data = await res.json();
    const rawJobs = Array.isArray(data?.jobs) ? data.jobs : [];
    const jobs = rawJobs.map((j: any) => mapToDubbingJob(j));

    return NextResponse.json({ jobs });
  } catch (error) {
    console.error('Failed to fetch user jobs from PostgreSQL backend:', error);
    return NextResponse.json({ error: 'Failed to fetch jobs', jobs: [] }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const session = await auth();
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    const youtubeUrl = body?.youtubeUrl || body?.youtube_url;
    const targetLanguage = body?.targetLanguage || body?.target_language || 'en';

    if (!youtubeUrl) {
      return NextResponse.json({ error: 'Missing youtubeUrl' }, { status: 400 });
    }

    const res = await fetch(`${BACKEND_URL}/api/v1/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        youtube_url: youtubeUrl,
        target_language: targetLanguage,
        user_email: session.user.email,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      return NextResponse.json({ error: err.detail || 'Failed to create job' }, { status: res.status });
    }

    const created = await res.json();
    return NextResponse.json({ success: true, job_id: created.job_id }, { status: 201 });
  } catch (error) {
    console.error('Failed to create job in PostgreSQL backend:', error);
    return NextResponse.json({ error: 'Failed to save job' }, { status: 500 });
  }
}
