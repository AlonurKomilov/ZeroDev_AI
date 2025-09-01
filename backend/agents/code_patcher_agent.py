from backend.core.ai_router import get_llm_adapter


class CodePatcherAgent:
    """
    Takes a user's modification prompt and rich context from the Context Engine,
    and its primary output is a standard diff/patch file representing the
    proposed code changes.
    """

    async def generate_patch(
        self, prompt: str, context: dict, model_name: str = "gpt-4o-mini"
    ) -> str:
        """
        Generates a diff patch in the standard unified format.

        :param prompt: The user's natural language prompt for the modification.
        :param context: A dictionary where keys are file paths and values are file contents.
        :param model_name: The name of the language model to use.
        :return: A string containing the diff patch.
        """
        print(f"Generating patch for prompt: '{prompt[:50]}...'")

        # 1. Construct a detailed prompt for the AI model.
        system_prompt = """You are an expert software engineer. Your sole task is to generate a code modification based on a user's request and the provided file context.
Your output MUST be a diff file in the standard unified format.
Do NOT provide any explanation, commentary, or any text other than the diff itself.
The diff must be complete and well-formed so it can be applied directly using a tool like `patch`.
It should start with `--- a/path/to/file.ext` and `+++ b/path/to/file.ext` for each modified file."""

        # Format the context for the prompt
        context_str = ""
        if not context or not isinstance(context, dict):
            return "Error: Invalid or empty context provided."

        for file_path, file_content in context.items():
            context_str += f"--- {file_path} ---\n{file_content}\n\n"

        user_prompt = f"""User Request:
{prompt}

Project File Context:
{context_str}

Based on the user request and the provided files, generate the required diff file."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # 2. Get an LLM adapter and call the chat_completion method.
        try:
            adapter = get_llm_adapter(model_name)
            # The chat_completion method is async, so we need to await it.
            response = await adapter.chat_completion(
                messages=messages, model=model_name
            )

            # 3. Extract the diff from the model's response.
            if response and response.get("choices"):
                patch = response["choices"][0]["message"]["content"]

                # Clean the patch to remove markdown code blocks if the model adds them.
                if patch.startswith("```diff"):
                    patch = patch[len("```diff\n") :]
                if patch.endswith("```"):
                    patch = patch[: -len("```")]

                print("Successfully generated patch.")
                return patch.strip()
            else:
                error_msg = "Error: Received an empty or invalid response from the language model."
                print(error_msg)
                return error_msg

        except Exception as e:
            error_msg = f"Error: An exception occurred while communicating with the language model: {e}"
            print(error_msg)
            return error_msg


# Singleton instance of the agent
code_patcher_agent = CodePatcherAgent()
