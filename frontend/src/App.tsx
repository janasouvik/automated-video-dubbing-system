import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Video, 
  Languages, 
  Play, 
  Loader2, 
  CheckCircle2, 
  Download, 
  AlertCircle 
} from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

interface JobResponse {
  job_id: string;
  youtube_url: string;
  status: string;
}

interface JobStatus {
  job_id: string;
  status: 'pending' | 'downloading' | 'transcribing' | 'translating' | 'synthesizing' | 'remixing' | 'completed' | 'failed';
  progress_percent: number;
  current_stage_message: string | null;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export default function App() {
  const [url, setUrl] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('en');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Poll for job status
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;

    if (currentJobId && (!jobStatus || !['completed', 'failed'].includes(jobStatus.status))) {
      interval = setInterval(async () => {
        try {
          const res = await axios.get(`${API_BASE_URL}/jobs/${currentJobId}`);
          setJobStatus(res.data);
          
          if (['completed', 'failed'].includes(res.data.status)) {
            clearInterval(interval);
          }
        } catch (err) {
          console.error("Failed to poll status", err);
        }
      }, 2000);
    }

    return () => clearInterval(interval);
  }, [currentJobId, jobStatus?.status]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setIsSubmitting(true);
    setError(null);
    setJobStatus(null);
    
    try {
      const res = await axios.post<JobResponse>(`${API_BASE_URL}/jobs`, {
        youtube_url: url,
        target_language: targetLanguage,
      });
      setCurrentJobId(res.data.job_id);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to submit job. Make sure the backend is running.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDownload = () => {
    if (!currentJobId) return;
    window.location.href = `${API_BASE_URL}/jobs/${currentJobId}/download`;
  };

  return (
    <div className="min-h-screen flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="max-w-3xl w-full space-y-8 text-center mb-12">
        <div className="flex justify-center">
          <div className="p-4 bg-blue-500/10 rounded-full border border-blue-500/20 backdrop-blur-sm">
            <Video className="w-12 h-12 text-blue-400" />
          </div>
        </div>
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
            Automated Video Dubbing
          </h1>
          <p className="mt-4 text-lg text-slate-400">
            Translate and dub YouTube videos using AI seamlessly.
          </p>
        </div>
      </div>

      <div className="w-full max-w-xl">
        {/* Form Card */}
        <div className="bg-slate-800/50 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-slate-700/50">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-slate-300">
                YouTube URL
              </label>
              <div className="mt-2">
                <input
                  id="url"
                  name="url"
                  type="url"
                  required
                  placeholder="https://www.youtube.com/watch?v=..."
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="block w-full rounded-lg border-0 py-3 px-4 bg-slate-900 text-white shadow-inner ring-1 ring-inset ring-slate-700 focus:ring-2 focus:ring-inset focus:ring-blue-500 sm:text-sm sm:leading-6 placeholder:text-slate-500"
                />
              </div>
            </div>

            <div>
              <label htmlFor="language" className="block text-sm font-medium text-slate-300">
                Target Language
              </label>
              <div className="mt-2 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Languages className="h-5 w-5 text-slate-400" />
                </div>
                <select
                  id="language"
                  name="language"
                  value={targetLanguage}
                  onChange={(e) => setTargetLanguage(e.target.value)}
                  className="block w-full rounded-lg border-0 py-3 pl-10 pr-4 bg-slate-900 text-white shadow-inner ring-1 ring-inset ring-slate-700 focus:ring-2 focus:ring-inset focus:ring-blue-500 sm:text-sm sm:leading-6 appearance-none"
                >
                  <option value="en">English (US)</option>
                  <option value="es" disabled>Spanish (Coming Soon)</option>
                  <option value="fr" disabled>French (Coming Soon)</option>
                </select>
              </div>
            </div>

            {error && (
              <div className="rounded-md bg-red-500/10 p-4 border border-red-500/20">
                <div className="flex">
                  <AlertCircle className="h-5 w-5 text-red-400" />
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-400">{error}</h3>
                  </div>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting || !!(jobStatus && !['completed', 'failed'].includes(jobStatus.status))}
              className="flex w-full justify-center items-center rounded-lg bg-blue-600 px-3 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-lg hover:shadow-blue-500/30"
            >
              {isSubmitting ? (
                <Loader2 className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" />
              ) : (
                <Play className="-ml-1 mr-2 h-5 w-5 text-white" />
              )}
              {isSubmitting ? 'Starting Job...' : 'Start Dubbing'}
            </button>
          </form>
        </div>

        {/* Progress Card */}
        {jobStatus && (
          <div className="mt-8 bg-slate-800/50 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-slate-700/50 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h3 className="text-lg font-medium text-white mb-6 flex items-center">
              Job Status
              {jobStatus.status === 'completed' && <CheckCircle2 className="ml-2 w-5 h-5 text-emerald-400" />}
            </h3>
            
            <div className="space-y-4">
              <div className="flex justify-between text-sm font-medium">
                <span className="text-slate-300 capitalize">{jobStatus.status}</span>
                <span className="text-blue-400">{jobStatus.progress_percent}%</span>
              </div>
              
              <div className="w-full bg-slate-900 rounded-full h-3 ring-1 ring-inset ring-slate-700 overflow-hidden">
                <div 
                  className={`h-3 rounded-full transition-all duration-500 ${
                    jobStatus.status === 'failed' ? 'bg-red-500' : 
                    jobStatus.status === 'completed' ? 'bg-emerald-500' : 'bg-blue-500'
                  }`}
                  style={{ width: `${jobStatus.progress_percent}%` }}
                ></div>
              </div>

              <p className="text-sm text-slate-400">
                {jobStatus.current_stage_message || 'Initializing...'}
              </p>

              {jobStatus.status === 'failed' && (
                <div className="mt-4 rounded-md bg-red-500/10 p-4 border border-red-500/20">
                  <p className="text-sm text-red-400">{jobStatus.error_message}</p>
                </div>
              )}

              {jobStatus.status === 'completed' && (
                <button
                  onClick={handleDownload}
                  className="mt-6 flex w-full justify-center items-center rounded-lg bg-emerald-600 px-3 py-3 text-sm font-semibold text-white shadow-sm hover:bg-emerald-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-600 transition-all duration-200"
                >
                  <Download className="-ml-1 mr-2 h-5 w-5 text-white" />
                  Download Dubbed Video
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
