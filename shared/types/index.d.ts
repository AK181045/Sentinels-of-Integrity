// =============================================================================
// SENTINELS OF INTEGRITY — Shared TypeScript Type Definitions
// Used by the browser extension and any Node.js-based tooling.
// =============================================================================

/** Supported platforms for media detection. */
export type Platform = "youtube" | "twitter" | "tiktok";

/** Supported media types. */
export type MediaType = "video" | "image" | "audio";

/** Trust verdict levels. */
export type Verdict = "authentic" | "suspicious" | "synthetic";

// ---------------------------------------------------------------------------
// Media Analysis Request (Extension → API)
// ---------------------------------------------------------------------------

export interface MediaAnalysisRequest {
  request_id: string;
  media_hash: string;
  media_url: string;
  platform: Platform;
  media_type: MediaType;
  options?: AnalysisOptions;
  submitted_at: string;
  extension_version: string;
}

export interface AnalysisOptions {
  skip_blockchain?: boolean;
  detailed_report?: boolean;
  max_frames?: number;
  confidence_threshold?: number;
}

export interface MediaAnalysisAck {
  request_id: string;
  status: "accepted" | "rejected" | "rate_limited";
  estimated_completion_ms: number;
  message: string;
}

// ---------------------------------------------------------------------------
// Trust Report (API → Extension)
// ---------------------------------------------------------------------------

export interface TrustReport {
  report_id: string;
  media_hash: string;
  media_url: string;
  platform: Platform;
  sentinels_score: number;
  verdict: Verdict;
  ml_result: MLResult;
  blockchain_result: BlockchainResult;
  analyzed_at: string;
  latency_ms: number;
}

export interface MLResult {
  is_synthetic: boolean;
  confidence: number;
  artifacts: string[];
  model_version: string;
  spatial: SpatialAnalysis;
  temporal: TemporalAnalysis;
  frequency: FrequencyAnalysis;
}

export interface SpatialAnalysis {
  face_consistency_score: number;
  edge_artifact_score: number;
  faces_detected: number;
}

export interface TemporalAnalysis {
  temporal_consistency: number;
  frames_analyzed: number;
  anomaly_frames: number[];
}

export interface FrequencyAnalysis {
  spectral_anomaly_score: number;
  ghosting_detected: boolean;
}

export interface BlockchainResult {
  is_registered: boolean;
  author: string;
  registration_tx: string;
  edit_history: EditRecord[];
  zk_verified: boolean;
}

export interface EditRecord {
  editor: string;
  edit_hash: string;
  timestamp: string;
  description: string;
}

// ---------------------------------------------------------------------------
// Blockchain Events
// ---------------------------------------------------------------------------

export interface ContentRegisteredEvent {
  tx_hash: string;
  content_hash: string;
  creator_address: string;
  metadata_uri: string;
  block_number: string;
  timestamp: string;
}

export interface WatermarkVerification {
  content_hash: string;
  watermark_found: boolean;
  embedded_hash: string;
  matches_original: boolean;
  extraction_confidence: number;
}

// ---------------------------------------------------------------------------
// Extension Settings
// ---------------------------------------------------------------------------

export interface ExtensionSettings {
  auto_scan: boolean;
  show_overlay: boolean;
  confidence_threshold: number;
  enabled_platforms: Platform[];
  detailed_reports: boolean;
  notification_enabled: boolean;
}

export const DEFAULT_SETTINGS: ExtensionSettings = {
  auto_scan: true,
  show_overlay: true,
  confidence_threshold: 0.7,
  enabled_platforms: ["youtube", "twitter", "tiktok"],
  detailed_reports: false,
  notification_enabled: true,
};
