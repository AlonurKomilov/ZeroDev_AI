import hashlib
import json
from collections import defaultdict
from pathlib import Path

from sqlmodel import Session, select

from backend.core.database import get_session
from backend.models.analytics_model import PromptFeedback, SecurityViolationPattern


class FeedbackAnalysisAgent:
    """
    Processes log files to identify patterns and stores structured insights
    in a dedicated analytics database. This agent is designed to be run as a
    scheduled periodic task.
    """

    # Correct paths assuming the CWD is the 'backend' directory
    FEEDBACK_LOG_PATH = Path("security_engine/feedback_log.json")
    AUDIT_LOG_PATH = Path("security_log.json")

    def run_analysis(self):
        """
        The main method for the agent to run its analysis. It processes
        both feedback and audit logs.
        """
        print("Starting feedback and audit log analysis...")
        # Using a context manager for the session ensures it's properly closed.
        with get_session() as session:
            self._analyze_feedback_log(session)
            self._analyze_audit_log(session)
        print("Feedback and audit log analysis complete.")

    def _analyze_feedback_log(self, session: Session):
        """
        Analyzes the user feedback log and updates the database with aggregated data.
        """
        print("Analyzing feedback log...")
        if not self.FEEDBACK_LOG_PATH.exists():
            print(f"Feedback log not found at {self.FEEDBACK_LOG_PATH}")
            return

        try:
            with self.FEEDBACK_LOG_PATH.open("r", encoding="utf-8") as f:
                feedback_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Could not read or parse feedback log: {e}")
            return

        # Aggregate feedback using a dictionary
        aggregated_feedback = defaultdict(lambda: {"upvotes": 0, "downvotes": 0})
        for entry in feedback_data:
            original_prompt = entry.get("original_prompt")
            suggested_prompt = entry.get("suggested_prompt")
            feedback = entry.get("feedback")

            if not all([original_prompt, suggested_prompt, feedback]):
                continue

            prompt_hash = hashlib.sha256(original_prompt.encode("utf-8")).hexdigest()
            key = (prompt_hash, suggested_prompt)

            if feedback == "up":
                aggregated_feedback[key]["upvotes"] += 1
            elif feedback == "down":
                aggregated_feedback[key]["downvotes"] += 1

        # Upsert (Update or Insert) the aggregated data into the database
        for (prompt_hash, suggested_prompt), votes in aggregated_feedback.items():
            statement = select(PromptFeedback).where(
                PromptFeedback.original_prompt_hash == prompt_hash,
                PromptFeedback.suggested_prompt == suggested_prompt,
            )
            db_entry = session.exec(statement).first()

            if db_entry:
                # We are overwriting the counts here, not incrementing.
                # This assumes the log is processed fresh each time.
                # A more robust system might archive processed logs.
                db_entry.upvotes = votes["upvotes"]
                db_entry.downvotes = votes["downvotes"]
            else:
                db_entry = PromptFeedback(
                    original_prompt_hash=prompt_hash,
                    suggested_prompt=suggested_prompt,
                    upvotes=votes["upvotes"],
                    downvotes=votes["downvotes"],
                )
            session.add(db_entry)

        session.commit()
        print(
            f"Upserted {len(aggregated_feedback)} feedback entries into the database."
        )

    def _analyze_audit_log(self, session: Session):
        """
        Analyzes the security audit log and updates the database with violation counts.
        """
        print("Analyzing audit log...")
        if not self.AUDIT_LOG_PATH.exists():
            print(f"Audit log not found at {self.AUDIT_LOG_PATH}")
            return

        try:
            with self.AUDIT_LOG_PATH.open("r", encoding="utf-8") as f:
                audit_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Could not read or parse audit log: {e}")
            return

        violation_counts = defaultdict(int)
        for entry in audit_data:
            for violation in entry.get("violations", []):
                violation_counts[violation] += 1

        # Upsert violation counts
        for violation_type, count in violation_counts.items():
            statement = select(SecurityViolationPattern).where(
                SecurityViolationPattern.violation_type == violation_type
            )
            db_entry = session.exec(statement).first()

            if db_entry:
                db_entry.count = count  # Overwrite with the latest total count
            else:
                db_entry = SecurityViolationPattern(
                    violation_type=violation_type, count=count
                )

            session.add(db_entry)

        session.commit()
        print(
            f"Upserted {len(violation_counts)} security violation types into the database."
        )


# Singleton instance of the agent
feedback_analysis_agent = FeedbackAnalysisAgent()
