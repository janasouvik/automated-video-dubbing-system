import fs from 'fs';
import path from 'path';
import { DubbingJob } from './mock-data';

const DATA_DIR = path.join(process.cwd(), 'data');
const JOBS_FILE = path.join(DATA_DIR, 'user_jobs.json');

interface UserJobsStore {
  [userEmail: string]: DubbingJob[];
}

function ensureJobsFileExists(): void {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }

  if (!fs.existsSync(JOBS_FILE)) {
    fs.writeFileSync(JOBS_FILE, JSON.stringify({}, null, 2), 'utf-8');
  }
}

export function getAllUserJobs(): UserJobsStore {
  try {
    ensureJobsFileExists();
    const data = fs.readFileSync(JOBS_FILE, 'utf-8');
    return JSON.parse(data) as UserJobsStore;
  } catch (error) {
    console.error('Error reading user_jobs.json:', error);
    return {};
  }
}

export function getJobsForUser(userEmail: string): DubbingJob[] {
  if (!userEmail) return [];
  const normalized = userEmail.trim().toLowerCase();
  const allStores = getAllUserJobs();
  return allStores[normalized] || [];
}

export function saveJobForUser(userEmail: string, job: DubbingJob): DubbingJob {
  if (!userEmail) throw new Error('User email is required to save job');
  ensureJobsFileExists();
  const normalized = userEmail.trim().toLowerCase();
  const allStores = getAllUserJobs();

  const userJobs = allStores[normalized] || [];
  const existingIdx = userJobs.findIndex((j) => j.id === job.id);

  if (existingIdx >= 0) {
    userJobs[existingIdx] = job;
  } else {
    userJobs.unshift(job);
  }

  allStores[normalized] = userJobs;
  fs.writeFileSync(JOBS_FILE, JSON.stringify(allStores, null, 2), 'utf-8');
  return job;
}

export function deleteJobForUser(userEmail: string, jobId: string): boolean {
  if (!userEmail) return false;
  ensureJobsFileExists();
  const normalized = userEmail.trim().toLowerCase();
  const allStores = getAllUserJobs();

  if (!allStores[normalized]) return false;

  allStores[normalized] = allStores[normalized].filter((j) => j.id !== jobId);
  fs.writeFileSync(JOBS_FILE, JSON.stringify(allStores, null, 2), 'utf-8');
  return true;
}
