def calculate_cost(chat_completion):
    model = chat_completion.model.strip()
    prompt_tokens = chat_completion.usage.prompt_tokens
    completion_tokens = chat_completion.usage.completion_tokens

    # Calculate cost based on the model and input tokens
    if model == "gpt-3.5-turbo-0125":
        prompt_cost_per_million = 0.05
        completion_cost_per_million = 1.50
    else:
        raise ValueError(f"Model not supported: {model}")

    prompt_cost = prompt_tokens * prompt_cost_per_million / 1_000_000
    completion_cost = completion_tokens * completion_cost_per_million / 1_000_000

    return prompt_cost + completion_cost
