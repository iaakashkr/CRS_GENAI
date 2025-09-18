# from dataclasses import dataclass, field
# from typing import List, Optional, Dict, Any
# from datetime import datetime

# @dataclass
# class PipelineDTO:
#     """
#     Production-grade Data Transfer Object for the full SQL conversational pipeline.
#     """

#     # -------------------------
#     # 1️⃣ User Input & Preprocessing
#     # -------------------------
#     input_question: str
#     rephrased_question: Optional[str] = None
#     detected_locations: List[Dict[str, str]] = field(default_factory=list)

#     # -------------------------
#     # 2️⃣ LLM Intent & Selected Metrics
#     # -------------------------
#     selected_metric: List[Any] = field(default_factory=list)
#     intent_result: Optional[Dict[str, Any]] = None
#     intent_text: Optional[str] = None
#     intent_usage: Optional[Dict[str, Any]] = None

#     # -------------------------
#     # 3️⃣ Table & Column Mapping
#     # -------------------------
#     tables: List[str] = field(default_factory=list)
#     columns: List[str] = field(default_factory=list)
#     joinings: List[Dict[str, Any]] = field(default_factory=list)

#     # -------------------------
#     # 4️⃣ SQL Generation
#     # -------------------------
#     sql_query: Optional[str] = None
#     sql_usage: Optional[Dict[str, Any]] = None
#     few_shots: List[Dict[str, str]] = field(default_factory=list)

#     # -------------------------
#     # 5️⃣ SQL Execution & Response
#     # -------------------------
#     response: List[Dict[str, Any]] = field(default_factory=list)
#     query_in_cache: bool = False
#     chart_data: Optional[Dict[str, Any]] = None

#     # -------------------------
#     # 6️⃣ Extras / Downstream
#     # -------------------------
#     extras: Optional[Dict[str, Any]] = None
#     conv_chain_hist: List[Dict[str, Any]] = field(default_factory=list)

#     # -------------------------
#     # 7️⃣ Token & Audit Info
#     # -------------------------
#     token_summary: Optional[Dict[str, Any]] = None
#     steps_usage: List[Dict[str, Any]] = field(default_factory=list)
#     total_tokens: Optional[int] = None

#     # -------------------------
#     # 8️⃣ Timing
#     # -------------------------
#     start_time: float = field(default_factory=lambda: datetime.now().timestamp())
#     end_time: float = field(default_factory=lambda: datetime.now().timestamp())
#     time_taken_in_seconds: Optional[float] = None

#     # -------------------------
#     # 9️⃣ Errors & Suggestions
#     # -------------------------
#     errors: List[str] = field(default_factory=list)
#     suggestions: List[str] = field(default_factory=list)

#     # -------------------------
#     # Utility Methods
#     # -------------------------
#     def compute_total_tokens(self) -> int:
#         """Compute total tokens from steps_usage if total_tokens not provided."""
#         if self.total_tokens is not None:
#             return self.total_tokens
#         return sum(
#             step.get("prompt_tokens", 0) + step.get("completion_tokens", 0)
#             for step in self.steps_usage
#         )

#     def finalize_timing(self):
#         """Compute time taken automatically."""
#         self.time_taken_in_seconds = self.end_time - self.start_time

#     def to_dict(self) -> Dict[str, Any]:
#         """Serialize DTO for audit, logging, or API response."""
#         return {
#             "input_question": self.input_question,
#             "rephrased_question": self.rephrased_question,
#             "selected_metric": self.selected_metric,
#             "intent_result": self.intent_result,
#             # "intent_text": self.intent_text,
#             "intent_usage": self.intent_usage,
#             "tables": self.tables,
#             "columns": self.columns,
#             "joinings": self.joinings,
#             "sql_query": self.sql_query,
#             "sql_usage": self.sql_usage,
#             # "few_shots": self.few_shots,
#             "response": self.response,
#             # "query_in_cache": self.query_in_cache,
#             # "chart_data": self.chart_data,
#             "extras": self.extras,
#             # "conv_chain_hist": self.conv_chain_hist,
#             # "token_summary": self.token_summary,
#             "steps_usage": self.steps_usage,
#             "total_tokens": self.compute_total_tokens(),
#             "start_time": self.start_time,
#             "end_time": self.end_time,
#             "time_taken_in_seconds": self.time_taken_in_seconds,
#             "errors": self.errors,
#             # "suggestions": self.suggestions,
#         }


from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class PipelineDTO:
    """
    Production-grade Data Transfer Object for the full SQL conversational pipeline.
    """

    # -------------------------
    # 1️⃣ User Input & Preprocessing
    # -------------------------
    input_question: str
    rephrased_question: Optional[str] = None
    detected_locations: List[Dict[str, str]] = field(default_factory=list)

    # -------------------------
    # 2️⃣ LLM Intent & Selected Metrics
    # -------------------------
    selected_metric: Dict[str, Any] = field(default_factory=dict)
    intent_result: Optional[Dict[str, Any]] = None
    intent_text: Optional[str] = None
    intent_usage: Optional[Dict[str, Any]] = None

    # -------------------------
    # 3️⃣ Table & Column Mapping
    # -------------------------
    tables: List[str] = field(default_factory=list)
    columns: Dict[str, List[str]] = field(default_factory=dict)
    joinings: List[Dict[str, Any]] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    # -------------------------
    # 4️⃣ SQL Generation
    # -------------------------
    sql_query: Optional[str] = None
    sql_usage: Optional[Dict[str, Any]] = None
    few_shots: List[Dict[str, str]] = field(default_factory=list)
    few_shot_matched_indices: List[int] = field(default_factory=list)


    # -------------------------
    # 5️⃣ SQL Execution & Response
    # -------------------------
    response: List[Dict[str, Any]] = field(default_factory=list)
    query_in_cache: bool = False
    chart_data: Optional[Dict[str, Any]] = None

    # -------------------------
    # 6️⃣ Extras / Downstream
    # -------------------------
    extras: Optional[Dict[str, Any]] = None
    conv_chain_hist: List[Dict[str, Any]] = field(default_factory=list)

    # -------------------------
    # 7️⃣ Token & Audit Info
    # -------------------------
    token_summary: Optional[Dict[str, Any]] = None
    steps_usage: List[Dict[str, Any]] = field(default_factory=list)
    total_tokens: Optional[int] = None

    # -------------------------
    # 8️⃣ Timing
    # -------------------------
    start_time: float = field(default_factory=lambda: datetime.now().timestamp())
    end_time: float = field(default_factory=lambda: datetime.now().timestamp())
    time_taken_in_seconds: Optional[float] = None

    # -------------------------
    # 9️⃣ Errors & Suggestions
    # -------------------------
    errors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    # -------------------------
    # Utility Methods
    # -------------------------
    def compute_total_tokens(self) -> int:
        """Compute total tokens from steps_usage if total_tokens not provided."""
        if self.total_tokens is not None:
            return self.total_tokens
        return sum(
            step.get("prompt_tokens", 0) + step.get("completion_tokens", 0)
            for step in self.steps_usage
        )

    def finalize_timing(self):
        """Compute time taken automatically."""
        self.time_taken_in_seconds = self.end_time - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        """Serialize DTO for audit, logging, or API response."""
        return {
            "input_question": self.input_question,
            "rephrased_question": self.rephrased_question,
            "selected_metric": self.selected_metric,
            # "intent_result": self.intent_result,
            # "intent_text": self.intent_text,
            # "intent_usage": self.intent_usage,
            "tables": self.tables,
            "columns": self.columns,
            "joinings": self.joinings,
            "sql_query": self.sql_query,
            "sql_usage": self.sql_usage,
            # "few_shots": self.few_shots,
            "response": self.response,
            # "query_in_cache": self.query_in_cache,
            # "chart_data": self.chart_data,
            "extras": self.extras,
            # "conv_chain_hist": self.conv_chain_hist,
            # "token_summary": self.token_summary,
            "steps_usage": self.steps_usage,
            "total_tokens": self.compute_total_tokens(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "time_taken_in_seconds": self.time_taken_in_seconds,
            "errors": self.errors,
            # "suggestions": self.suggestions,
        }
