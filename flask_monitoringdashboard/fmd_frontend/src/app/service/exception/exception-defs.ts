export interface ExceptionGroup {
  type: string;
  message: string;
  endpoint: string;
  endpoint_id: number;
  latest_timestamp: string;
  first_timestamp: string;
  count: number;
}

export interface StackTraceLine {
  position: number;
  full_file_path: string;
  file_path: string;
  function_definition_id: number;
  function_name: string;
  function_start_line_number: number;
  line_number: number;
}

export interface ExceptionDetails {
  type: string;
  message: string;
  stack_trace_snapshot_id: number;
  stack_trace_snapshot: StackTraceLine[];
  latest_timestamp: string;
  first_timestamp: string;
  count: number;
}
