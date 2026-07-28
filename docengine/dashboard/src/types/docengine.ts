export interface ClaimItem { files_modified: string[]; adrs_touched: string[]; prs: { number: number }[]; }
export interface VerificationDetail { files: { file: string; status: 'VERIFICADO' | 'NO_ENCONTRADO' }[]; adrs: { adr: string; status: 'VERIFICADO' | 'NO_ENCONTRADO' }[]; prs: { number: number; status: 'VERIFICADO' | 'NO_ENCONTRADO' }[]; }
export interface AgentSession { schema_version: string; session_id: string; agent_id: string; repo: string; branch: string; task_ref: string; started_at: string; ended_at: string; summary: string; outcome: 'COMPLETADO' | 'BLOQUEADO' | 'PARCIAL'; claims: ClaimItem; verification: { status: 'VERIFICADO' | 'NO_ENCONTRADO' | 'DISCREPANCIA'; checked_at: string; details: VerificationDetail; } | null; }
export interface InvalidSession { file_name: string; error: string; }
export interface ADRItem { id: string; number: string; title: string; declared_status: string; auto_status: string; evidence_commits: { sha: string; message: string; url: string }[]; warning: string | null; }
export interface GitCommit { sha: string; message: string; author: string; date: string; url: string; files: string[]; }
export interface GitPR { number: number; title: string; state: string; user: string; created_at: string; merged_at: string | null; url: string; }
export interface GitBranch { name: string; sha: string; }
export interface DocItem { path: string; title: string; last_commit_date: string; days_old: number | string; is_stale: boolean; }
