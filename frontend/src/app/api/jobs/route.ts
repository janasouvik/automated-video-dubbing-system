import { NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { getJobsForUser, saveJobForUser, deleteJobForUser } from '@/lib/jobStore';

export async function GET() {
  try {
    const session = await auth();
    if (!session?.user?.email) {
      return NextResponse.json({ jobs: [] }, { status: 200 });
    }

    const jobs = getJobsForUser(session.user.email);
    return NextResponse.json({ jobs: jobs || [] });
  } catch (error) {
    console.error('Failed to fetch user jobs:', error);
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

export async function DELETE(request: Request) {
  try {
    const session = await auth();
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const jobId = searchParams.get('id');
    if (!jobId) {
      return NextResponse.json({ error: 'Missing job id' }, { status: 400 });
    }

    const success = deleteJobForUser(session.user.email, jobId);
    return NextResponse.json({ success });
  } catch (error) {
    console.error('Failed to delete job:', error);
    return NextResponse.json({ error: 'Failed to delete job' }, { status: 500 });
  }
}
