import { NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { getJobsForUser, saveJobForUser } from '@/lib/jobStore';

export async function GET() {
  try {
    const session = await auth();
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const jobs = getJobsForUser(session.user.email);
    return NextResponse.json({ jobs });
  } catch (error) {
    console.error('Failed to fetch user jobs:', error);
    return NextResponse.json({ error: 'Failed to fetch jobs' }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const session = await auth();
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    if (!body?.id || !body?.youtubeUrl) {
      return NextResponse.json({ error: 'Invalid job data' }, { status: 400 });
    }

    const savedJob = saveJobForUser(session.user.email, body);
    return NextResponse.json({ success: true, job: savedJob }, { status: 201 });
  } catch (error) {
    console.error('Failed to save user job:', error);
    return NextResponse.json({ error: 'Failed to save job' }, { status: 500 });
  }
}
