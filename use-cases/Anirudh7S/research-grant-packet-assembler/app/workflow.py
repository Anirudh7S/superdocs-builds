from pathlib import Path
from typing import Any, Dict

from app.pipeline import run_grant_assembly
from app.superdocs import SuperDocsClient


def run_superdocs_workflow(
    grant_directory: str | Path,
) -> Dict[str, Any]:
    """Run the complete local grant + SuperDocs workflow."""

    grant_directory = Path(grant_directory)

    # 1. Build and validate the grant package.
    assembly = run_grant_assembly(
        grant_directory
    )

    validation = assembly["validation"]

    # Never send an invalid grant package to SuperDocs.
    if not validation["valid"]:
        return {
            "status": "validation_failed",
            "validation": validation,
            "grant_package": assembly["grant_package"],
            "output_path": assembly["output_path"],
        }

    # 2. Create SuperDocs client.
    client = SuperDocsClient()

    # 3. Create a new session.
    session = client.init_session()

    session_id = session["session_id"]

    # 4. Upload the research narrative.
    research_narrative_path = (
        grant_directory / "research_narrative.txt"
    )

    upload = client.upload_document(
        str(research_narrative_path),
        session_id,
    )

    # 5. Ask SuperDocs to improve the narrative.
    chat_result = client.chat(
        session_id,
        (
            "Improve the research narrative for clarity and concision "
            "while preserving the project title, investigators, all "
            "three specific aims, research approach, expected outcomes, "
            "and significance. Do not introduce new facts."
        ),
    )

    return {
        "status": "completed",
        "validation": validation,
        "grant_package": assembly["grant_package"],
        "output_path": assembly["output_path"],
        "session_id": session_id,
        "document_id": upload.get("document_id"),
        "upload": upload,
        "chat": chat_result,
    }