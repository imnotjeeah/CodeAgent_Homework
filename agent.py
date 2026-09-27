import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件里的配置
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")


class CodeAgent:
    """
    代码助手 Agent
    支持两种功能：
    1. explain：解释代码逻辑并加注释
    2. review：审查代码，找出潜在 Bug 和改进建议
    """

    def __init__(self, api_key, base_url, model_name):
        """初始化 Agent，创建大模型客户端"""
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model_name

        # 两种功能的 System Prompt
        self.prompts = {
            "explain": (
                "你是一个专业的代码解释助手。用户会给你一段代码，"
                "请你用通俗易懂的中文解释这段代码的功能、逻辑和关键步骤，"
                "并在代码中添加适当的中文注释。"
            ),
            "review": (
                "你是一个资深的代码审查专家。用户会给你一段代码，"
                "请你找出代码中潜在的 Bug、性能问题、代码坏味道，"
                "并给出具体的改进建议。请用中文回答。"
            ),
        }

    def _call_llm(self, mode, code_snippet):
        """
        内部方法：调用大模型
        :param mode: "explain" 或 "review"
        :param code_snippet: 用户输入的代码
        :return: 大模型返回的文本
        """
        try:
            messages = [
                {"role": "system", "content": self.prompts[mode]},
                {"role": "user", "content": f"请处理以下代码：\n\n{code_snippet}"},
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"调用大模型时出错：{str(e)}"

    def explain(self, code_snippet):
        """解释代码"""
        return self._call_llm("explain", code_snippet)

    def review(self, code_snippet):
        """审查代码"""
        return self._call_llm("review", code_snippet)

    def explain_file(self, file_path):
        """读取本地文件并解释"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            return self.explain(code)
        except FileNotFoundError:
            return f"找不到文件：{file_path}"
        except Exception as e:
            return f"读取文件出错：{str(e)}"


# ================= 命令行交互 =================
if __name__ == "__main__":
    agent = CodeAgent(API_KEY, BASE_URL, MODEL_NAME)

    print("=" * 40)
    print("  代码助手 Agent 已启动")
    print("  功能：explain（解释） / review（审查）")
    print("  输入 exit 退出")
    print("=" * 40)

    while True:
        print("\n请选择功能：")
        print("  1. explain - 解释代码")
        print("  2. review  - 审查代码")
        print("  3. file    - 解释本地文件")
        print("  exit       - 退出")

        choice = input(">>> ").strip().lower()

        if choice == "exit":
            print("再见！")
            break

        if choice == "1" or choice == "explain":
            code = input("请粘贴你的代码（输入 END 结束）：\n")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            code = "\n".join(lines)
            print("\n正在请求大模型，请稍候...\n")
            print(agent.explain(code))

        elif choice == "2" or choice == "review":
            code = input("请粘贴代码（输入 END 结束）：\n")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            code = "\n".join(lines)
            print("\n正在请求大模型，请稍候...\n")
            print(agent.review(code))

        elif choice == "3" or choice == "file":
            path = input("请输入文件路径：").strip()
            print("\n正在请求大模型，请稍候...\n")
            print(agent.explain_file(path))

        else:
            print("无效输入，请重新选择。")