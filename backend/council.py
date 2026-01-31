"""3-stage LLM Council orchestration."""

from typing import List, Dict, Any, Tuple
from .openrouter import query_models_parallel, query_model
from .config import COUNCIL_MODELS, CHAIRMAN_MODEL

#add system prompt
from .system_prompt import CHAIRMAN_SYSTEM_PROMPT, PHILOSOPHIERS_SYSTEM_PROMPT

# region agent log helper
# def _agent_debug_log(hypothesis_id: str, location: str, message: str, data: Dict[str, Any], run_id: str = "initial") -> None:
#     """
#     Lightweight debug logger writing NDJSON lines for this debug session.
#     """
#     try:
#         import json
#         import time

#         payload = {
#             "sessionId": "debug-session",
#             "runId": run_id,
#             "hypothesisId": hypothesis_id,
#             "location": location,
#             "message": message,
#             "data": data,
#             "timestamp": int(time.time() * 1000),
#         }
#         with open("/media/hungmtp/DATA1/Git_clone/phylosophy-llm-council/.cursor/debug.log", "a", encoding="utf-8") as f:
#             f.write(json.dumps(payload, ensure_ascii=False) + "\n")
#     except Exception:
#         # Debug logging must never break main logic
#         pass
# endregion


async def stage1_collect_responses(user_query: str) -> List[Dict[str, Any]]:
    """
    Stage 1: Collect individual responses from all council models.

    Args:
        user_query: The user's question

    Returns:
        List of dicts with 'model' and 'response' keys
    """
    # Build per-model messages with philosopher-specific system prompts
    messages: List[List[Dict[str, str]]] = []
    for _, philosophier_system_prompt in PHILOSOPHIERS_SYSTEM_PROMPT.items():
        messages.append([
            {"role": "system", "content": philosophier_system_prompt + "\nIMPORTANT: Answer ONLY in Vietnamese."},
            {"role": "user", "content": user_query},
        ])

    # region agent log
    # if messages:
    #     _agent_debug_log(
    #         hypothesis_id="H1",
    #         location="council.stage1_collect_responses",
    #         message="Stage 1 messages built",
    #         data={
    #             "messages_count": len(messages),
    #             "first_message_roles": [m["role"] for m in messages[0]],
    #         },
    #     )
    # endregion

    # Query all models in parallel (one message list per philosopher)
    philosopher_names = list(PHILOSOPHIERS_SYSTEM_PROMPT.keys())
    responses = await query_models_parallel(COUNCIL_MODELS, messages)

    # Format results: philosophier = key from PHILOSOPHIERS_SYSTEM_PROMPT (order preserved)
    stage1_results = []
    for i in range(min(len(philosopher_names), len(responses))):
        response = responses[i]
        if response is not None:
            stage1_results.append({
                "philosophier": philosopher_names[i],
                "response": response.get('content', '')
            })

    return stage1_results


async def stage2_cross_debate(
    user_query: str,
    stage1_results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Stage 2: Cross-Debate — each philosopher critiques the others (identified, direct attack).

    Args:
        user_query: The original user query
        stage1_results: Results from Stage 1 (philosophier, response)

    Returns:
        List of dicts with philosophier and critique
    """
    philosopher_names = list(PHILOSOPHIERS_SYSTEM_PROMPT.keys())
    DEBATE_PROMPT_TEMPLATE = """
    You are {current_philosopher_name}.
    Your Core Philosophy:
    You are currently in a "Round Table" debate with other philosophers. You have all just answered a user's question. Now, you must read the responses of your peers and critique them.

    ### CONTEXT
    User Question: "{user_query}"

    Here are the responses from the other philosophers:
    {responses_text}

    ### YOUR TASK
    Do NOT answer the user's question again. Instead, launch a philosophical attack on the other responses based on your specific worldview.

    1.  **Identify the Enemy:** Pick 1 or 2 philosophers whose answers are most offensive to your beliefs (e.g., if you are Nietzsche, attack Confucius for being weak/submissive; if you are Descartes, attack Plato for being mystical/illogical).
    2.  **Critique & Mock:** Tear apart their logic. Be in character. Use your specific terminology (e.g., "Forms," "Slave Morality," "Cogito," "Ritual").
    3.  **Direct Address:** Speak directly to them (e.g., "Plato, you are lost in shadows...", "Confucius, your rules suffocate the spirit...").
    4.  **Keep it Short:** limit your response to 2-3 sharp sentences. This is a verbal spar.

    ### TONE GUIDELINES
    - Be provocative and confident.
    - Do not be polite; this is a clash of ideologies.
    - Show, don't just tell, why your philosophy is superior.

    ### OUTPUT FORMAT
    Just output your spoken critique with whom you speak to in the format "<philosopher_name>, <critique>". Do not add headers like "My Critique:" or "Response:"."""

    messages: List[List[Dict[str, str]]] = []
    for i, current_name in enumerate(philosopher_names):
        # Build "other" responses (exclude self)
        others_text = "\n\n".join([
            f"{result['philosophier']}:\n{result['response']}"
            for result in stage1_results
            if result['philosophier'] != current_name
        ])

        debate_prompt = DEBATE_PROMPT_TEMPLATE.format(
            current_philosopher_name=current_name,
            user_query=user_query,
            responses_text=others_text,
        )

        # System = philosopher's core identity (from PHILOSOPHIERS_SYSTEM_PROMPT)
        system_content = (
            PHILOSOPHIERS_SYSTEM_PROMPT.get(current_name, "")
            + "\nIMPORTANT: Answer in Vietnamese. Output only your spoken critique, no headers."
        )
        messages.append([
            {"role": "system", "content": system_content},
            {"role": "user", "content": debate_prompt},
        ])

    # One model per philosopher (same order as stage1)
    responses = await query_models_parallel(COUNCIL_MODELS, messages)

    stage2_results = []
    for i in range(min(len(philosopher_names), len(responses))):
        response = responses[i]
        if response is not None:
            stage2_results.append({
                "philosophier": philosopher_names[i],
                "critique": response.get('content', ''),
            })

    return stage2_results


async def stage3_synthesize_final(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Stage 3: Chairman synthesizes final response.

    Args:
        user_query: The original user query
        stage1_results: Individual philosopher responses from Stage 1 (philosophier, response)
        stage2_results: Debate critiques from Stage 2 (philosophier, critique)

    Returns:
        Dict with 'model' and 'response' keys
    """
    # Build comprehensive context for chairman
    stage1_text = "\n\n".join([
        f"Philosopher: {result['philosophier']}\nResponse: {result['response']}"
        for result in stage1_results
    ])

    stage2_text = "\n\n".join([
        f"Philosopher: {result['philosophier']}\nCritique: {result['critique']}"
        for result in stage2_results
    ])

    chairman_prompt = f"""You are the Chairman of a Philosopher Council. Multiple Philosophers have provided responses to a user's question, then engaged in a Round Table cross-debate—attacking each other's positions by name.

Original Question: {user_query}

STAGE 1 - Individual Responses:
{stage1_text}

STAGE 2 - Cross-Debate Critiques (each philosopher attacking others):
{stage2_text}

Your task as Chairman is to synthesize all of this into a single, comprehensive, accurate answer to the user's original question. Consider:
- The individual responses and their insights
- The debate critiques and what they reveal about strengths and weaknesses of each position
- Any patterns of agreement or ideological clash

Provide a clear, well-reasoned final answer that represents the council's collective wisdom after the debate.
IMPORTANT: Answer ONLY in Vietnamese. DO NOT USE MARKDOWN FORMAT. Just output the answer directly."""

    messages = [
        {"role": "system", "content": CHAIRMAN_SYSTEM_PROMPT},
        {"role": "user", "content": chairman_prompt},
    ]

    # region agent log
    # _agent_debug_log(
    #     hypothesis_id="H3",
    #     location="council.stage3_synthesize_final",
    #     message="Stage 3 chairman messages built",
    #     data={
    #         "messages_roles": [m["role"] for m in messages],
    #     },
    # )
    # endregion

    # Query the chairman model
    response = await query_model(CHAIRMAN_MODEL, messages)

    if response is None:
        # Fallback if chairman fails
        return {
            "model": CHAIRMAN_MODEL,
            "response": "Error: Unable to generate final synthesis."
        }

    return {
        "model": CHAIRMAN_MODEL,
        "response": response.get('content', '')
    }


async def generate_conversation_title(user_query: str) -> str:
    """
    Generate a short title for a conversation based on the first user message.

    Args:
        user_query: The first user message

    Returns:
        A short title (3-5 words)
    """
    title_prompt = f"""Generate a very short title (3-5 words maximum) that summarizes the following question.
The title should be concise and descriptive. Do not use quotes or punctuation in the title.

Question: {user_query}

Title:"""

    messages = [{"role": "user", "content": title_prompt}]

    # Use gemini-3-4b for title generation (fast and cheap)
    response = await query_model("google/gemma-3-4b-it:free", messages, timeout=30.0)

    if response is None:
        # Fallback to a generic title
        return "New Conversation"

    title = response.get('content', 'New Conversation').strip()

    # Clean up the title - remove quotes, limit length
    title = title.strip('"\'')

    # Truncate if too long
    if len(title) > 50:
        title = title[:47] + "..."

    return title


async def run_full_council(user_query: str) -> Tuple[List, List, Dict, Dict]:
    """
    Run the complete 3-stage council process.

    Args:
        user_query: The user's question

    Returns:
        Tuple of (stage1_results, stage2_results, stage3_result, metadata)
    """
    # Stage 1: Collect individual responses
    stage1_results = await stage1_collect_responses(user_query)

    # If no models responded successfully, return error
    if not stage1_results:
        return [], [], {
            "model": "error",
            "response": "All models failed to respond. Please try again."
        }, {}

    # Stage 2: Cross-debate (each philosopher critiques others)
    stage2_results = await stage2_cross_debate(user_query, stage1_results)

    # Stage 3: Synthesize final answer
    stage3_result = await stage3_synthesize_final(
        user_query,
        stage1_results,
        stage2_results
    )

    # No ranking metadata; stage2 is debate critiques only
    metadata = {}

    return stage1_results, stage2_results, stage3_result, metadata
