from app.schemas.content import Conversation
from app.schemas.conversation_production import (
    ConversationProductionSubmission,
)


def validate_conversation_production_submission(
    submission: ConversationProductionSubmission,
    conversation: Conversation,
) -> None:
    """Validate captured productions against conversation prompts.

    Valida las producciones capturadas contra los prompts conversacionales.
    """
    if submission.conversation_id != conversation.id:
        raise ValueError(
            "Submission conversation ID does not match conversation"
        )

    prompts_by_id = {
        turn.production_prompt.id: (
            turn.id,
            turn.production_prompt,
        )
        for turn in conversation.turns
        if turn.production_prompt is not None
    }

    submitted_prompt_ids: set[str] = set()

    for production in submission.productions:
        prompt_context = prompts_by_id.get(production.prompt_id)

        if prompt_context is None:
            raise ValueError(
                "Submission references unknown production prompt: "
                + production.prompt_id
            )

        expected_turn_id, prompt = prompt_context

        if production.turn_id != expected_turn_id:
            raise ValueError(
                "Production turn ID does not match production prompt: "
                + production.prompt_id
            )

        if production.modality not in prompt.accepted_modalities:
            raise ValueError(
                "Production modality is not accepted by prompt: "
                + production.prompt_id
            )

        submitted_prompt_ids.add(production.prompt_id)

    required_prompt_ids = {
        prompt_id
        for prompt_id, (_, prompt) in prompts_by_id.items()
        if prompt.required
    }
    missing_prompt_ids = sorted(
        required_prompt_ids - submitted_prompt_ids
    )

    if missing_prompt_ids:
        raise ValueError(
            "Submission is missing required production: "
            + ", ".join(missing_prompt_ids)
        )
