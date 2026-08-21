import { DubbingJob, INITIAL_STAGES, PipelineStageInfo, StageStatus } from './mock-data';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function createJob(url: string, targetLanguage: string = 'en') {
  const res = await fetch(`${API_BASE_URL}/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ youtube_url: url, target_language: targetLanguage }),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Failed to create job');
  }
  return res.json();
}

export async function listJobs(limit = 50, offset = 0) {
  const res = await fetch(`${API_BASE_URL}/jobs?limit=${limit}&offset=${offset}`);
  if (!res.ok) throw new Error('Failed to fetch jobs');
  const data = await res.json();
  return data.jobs.map((job: any) => mapToDubbingJob(job));
}

export async function getJobStatus(jobId: string): Promise<DubbingJob> {
  const res = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
  if (!res.ok) throw new Error('Failed to fetch job status');
  const data = await res.json();
  return mapToDubbingJob(data);
}

export async function deleteJob(jobId: string) {
  const res = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete job');
}

function mapToDubbingJob(backendJob: any): DubbingJob {
  const p = backendJob.progress_percent || 0;
  
  let currentStageId: 'fetch' | 'transcribe' | 'translate' | 'synthesize' | 'remux' = 'fetch';
  if (p >= 100) currentStageId = 'remux';
  else if (p >= 80) currentStageId = 'remux';
  else if (p >= 60) currentStageId = 'synthesize';
  else if (p >= 40) currentStageId = 'translate';
  else if (p >= 20) currentStageId = 'transcribe';
  
  const stages: PipelineStageInfo[] = INITIAL_STAGES.map((stage, idx) => {
    const stageThreshold = idx * 20;
    const nextStageThreshold = (idx + 1) * 20;
    
    let status: StageStatus = 'pending';
    let progressPercent = 0;
    
    if (backendJob.status === 'failed' && currentStageId === stage.id) {
        status = 'failed';
        progressPercent = Math.min(100, Math.max(0, (p - stageThreshold) * 5));
    } else if (p >= nextStageThreshold) {
      status = 'completed';
      progressPercent = 100;
    } else if (p >= stageThreshold) {
      status = 'in_progress';
      progressPercent = Math.min(100, Math.max(0, (p - stageThreshold) * 5));
    }

    return {
      ...stage,
      status: backendJob.status === 'completed' ? 'completed' : status,
      progressPercent: backendJob.status === 'completed' ? 100 : progressPercent,
      message: (status === 'in_progress' || status === 'failed') 
        ? (backendJob.current_stage_message || stage.description)
        : (status === 'completed' ? 'Done' : 'Queued'),
    };
  });

  return {
    id: backendJob.job_id,
    title: 'Dubbed Video — ' + (backendJob.youtube_url?.split('v=')[1]?.slice(0,8) || backendJob.job_id.slice(0,8)),
    youtubeUrl: backendJob.youtube_url,
    targetLanguage: backendJob.target_language || 'en',
    targetLanguageLabel: backendJob.target_language === 'en' ? 'English (US)' : 'Other',
    status: backendJob.status,
    currentStageId: backendJob.status === 'completed' ? 'remux' : currentStageId,
    progressPercent: p,
    createdAt: backendJob.created_at,
    completedAt: backendJob.completed_at,
    stages,
    videoDuration: backendJob.video_duration_sec 
      ? `${Math.floor(backendJob.video_duration_sec / 60)}:${Math.floor(backendJob.video_duration_sec % 60).toString().padStart(2, '0')}` 
      : undefined,
    sourceLanguage: backendJob.source_language || 'Unknown',
    downloadUrl: backendJob.status === 'completed' ? `${API_BASE_URL}/jobs/${backendJob.job_id}/download` : undefined,
    error: backendJob.error_message || backendJob.error,
  };
}
