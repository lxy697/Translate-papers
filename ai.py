from openai import OpenAI
import time

class AI_API:
    def __init__(self, api_key, base_url, model, max_tokens):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.max_tokens = max_tokens

    def chatmore(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens
            )
            messages.append({"role": "assistant", "content": "{response.choices[0].message.content}}"})
            return messages, response.choices[0].message.content
        except Exception as e:
            print(f"Error: {e}")
            messages.append({"role": "assistant", "content": "API失效"})
            return messages, "API失效"

    def long_chat(self, query, max_retries):
        messages = [{"role": "user", "content": query}]
        print("开始对话")
        messages, txt = self.chatmore(messages)
        if txt == "API失效":
            return "API失效"
        retries = 0
        while retries < max_retries:
            time.sleep(10)####################################################
            print("续写一次")
            messages.append({"role": "user", "content": "请继续生成剩余部分，直到文本完整输出为止。如果上一段对话没有被截断，请回复“<<done>>”表示任务完成。"})
            messages, content = self.chatmore(messages)
            if content == "API失效":
                return "API失效"
            txt += content
            if content == "<<done>>":
                break
            retries += 1
        return txt
    
    def chatonce(self, query):
        time.sleep(10)###########################################################
        try:
            messages = [{"role": "user", "content": query}]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens
            )
        except Exception as e:
            print(f"Error: {e}")
            return "API失效"
        content = response.choices[0].message.content
        return content



