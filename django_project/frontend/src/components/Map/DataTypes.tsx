/**
 * All data types that being used on Map
 */

export interface AnalysisDataPeriod {
  year?: number;
  quarter?: number;
}

export interface AnalysisData {
  landscape?: string;
  analysisType?: string;
  temporalResolution?: string;
  variable?: string;
  period?: AnalysisDataPeriod;
  comparisonPeriod?: AnalysisDataPeriod;
}

export const GroupName = {
  BaselineGroup: 'baseline',
  NearRealtimeGroup: 'near-real-time',
  UserDefinedGroup: 'user-defined'
}
