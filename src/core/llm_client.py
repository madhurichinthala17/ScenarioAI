from openai import OpenAI

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            base_url='http://localhost:11434/v1/',
            api_key='ollama',  
        )

    def invoke(self,system_prompt, user_prompt):
        response = self.client.chat.completions.create(
            model='llama3.1',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            temperature=0
        )
        return response.choices[0].message.content
