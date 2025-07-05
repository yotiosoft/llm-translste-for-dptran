import langchain_core
import re
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def init_langchain(model_name):
    print(f"Using model: {model_name}")

    # load the LLM
    llm = OllamaLLM(model=model_name, temperature=0.7)

    # set up the prompt template
    """
    prompt = ChatPromptTemplate.from_template(
        """
    """You are a helpful translator. Translate the following text from {source_lang} to {target_lang}.
    Answer only with the translated text. If {source_lang} is not specified, guess the language of the text.
    You must follow these rules:
    - Translatiion should be whole and accurate. Do not summarize or itemize the translation results.
    - DO NOT include any additional text or explanations. DO NOT include any greetings, salutations, or any other text.
    - DO NOT answer like "I am unable to translate this text because it contains sensitive content." or similar.
    - Translate as much as possible so that symbols and sentence structure are equivalent.
    - DO NOT think about anything other than translation and meaning of the text. It's not telling you to think about the text.
    - You must answer in {target_lang}.
    {request}"""
    """)
    """
    prompt = ChatPromptTemplate.from_template(
        """
        Please provide the {target_lang} translation for the {source_lang} sentences. Example:
        Source: "Hello" Target: "こんにちは"
        Source: "Bonjour" Target: "Hello"
        Source: "Tutte le strade portano a Roma" Target: "All roads lead to Rome"
        Source: "我早上喝了 15 瓶啤酒。我很开心" Target: "I drank 15 bottles of beer in the morning. I am happy."
        Answer only with the translated text.
        Now, let's focus on the following {source_lang}-{target_lang} translation pair. 
        If source language is not specified, guess the language of the text.
        Do not include any additional text or explanations. Do not include any greetings, salutations, or any other text. The text is not telling you to think about the text.
        Translatiion should be whole and accurate. Do not summarize or itemize the translation results. All sentences should be translated.
        You must answer in {target_lang}.
        Source: {request} Target: 
        """
    )

    chain = prompt | llm | StrOutputParser()
    return chain

def translate_text(chain, texts, source_lang, target_lang):
    queries = []
    for text in texts:
        query = {
            'text': text,
            'source_lang': source_lang,
            'target_lang': target_lang
        }
        queries.append(query)

    results = []
    for query in queries:
        result = chain.invoke(
            {
                "request": query['text'],
                "source_lang": query['source_lang'],
                "target_lang": query['target_lang']
            }
        )
        # remove <think> </think> tags if they exist
        result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
        results.append(result)
    return results

if __name__ == "__main__":
    model_name = "hf.co/mmnga/cyberagent-DeepSeek-R1-Distill-Qwen-14B-Japanese-gguf:latest"
    chain = init_langchain(model_name)
    
    while True:
        # prompt for input
        text = input("> ")
        
        source_lang = input("Source language (or leave blank to guess): ") or None
        target_lang = input("Target language: ")
        if not target_lang:
            print("Target language is required.")
            continue
        
        # translate the text
        results = translate_text(chain, text, source_lang, target_lang)

        # print the results
        for result in results:
            print(f"Translated text: {result}")
