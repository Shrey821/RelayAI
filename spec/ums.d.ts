/**
 * Universal Memory Schema (UMS) - v1.0.0
 * Open Specification for Cross-LLM Memory Migration and Context Portability.
 */

export interface UMSPayload {
  version: "1.0.0";
  metadata: UMSMetadata;
  tier1_identity: UMSTier1Identity;
  tier2_active_context: UMSTier2ActiveContext;
  tier3_conversation_transcript?: UMSTier3Transcript;
}

export interface UMSMetadata {
  id: string;
  name?: string;
  created_at: string;
  updated_at?: string;
  source_provider: "chatgpt" | "claude" | "gemini" | "cursor" | "manual" | "generic";
  tags?: string[];
}

export interface UMSTier1Identity {
  profile: {
    name?: string;
    role?: string;
    bio?: string;
    core_principles: string[];
  };
  tech_stack: {
    primary_languages: string[];
    frameworks: string[];
    databases: string[];
    toolchains: string[];
    operating_system?: string;
  };
  communication_style: {
    tone: string;
    verbosity: "minimalist" | "concise" | "balanced" | "thorough" | "verbose";
    code_preference?: string;
    prohibitions: string[];
  };
  conventions: {
    coding_standards: string[];
    architecture_patterns: string[];
    testing_requirements: string[];
  };
  personal_trivia?: Array<{
    topic: string;
    value: string;
    is_work_related: boolean;
  }>;
}

export interface UMSTier2ActiveContext {
  current_objective: string;
  active_projects: Array<{
    name: string;
    status: string;
    current_phase?: string;
    decisions_made_today: string[];
    active_blockers: string[];
    next_steps: string[];
  }>;
  ephemeral_constraints: string[];
}

export interface UMSTier3Transcript {
  included: boolean;
  summary?: string;
  message_count?: number;
  messages: Array<{
    role: "user" | "assistant" | "system";
    content: string;
    timestamp?: string;
  }>;
}

export interface VerificationResult {
  timestamp: string;
  source_provider: string;
  target_provider: string;
  retention_score: number; // 0 to 100
  items_total: number;
  items_learned: number;
  items_adapted: number;
  items_filtered: number;
  diff_entries: DiffEntry[];
  suggestions: string[];
}

export interface DiffEntry {
  category: "tier1" | "tier2" | "tier3";
  field: string;
  item: string;
  status: "learned" | "adapted" | "filtered";
  reason?: string;
  confidence: number; // 0.0 to 1.0
}
