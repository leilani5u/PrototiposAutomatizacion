class OpenAIService:

    def __init__(self, client, deployment):
        self.client = client
        self.deployment = deployment

    def ask(self, system_prompt, user_prompt):

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=4000
        )

        return response.choices[0].message.content