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
    prompt = ChatPromptTemplate.from_template(
        """
    You are a helpful translator. Translate the following text from {source_lang} to {target_lang}.
    Answer only with the translated text.
    If {source_lang} is not specified, guess the language of the text.
    DO NOT include any additional text or explanations. DO NOT include any greetings, salutations, or any other text.
    And more, do not to attempt to think about the translation, just return the translated text.
    DO NOT answer like "I am unable to translate this text because it contains sensitive content." or similar.
    {request}"""
    )
    chain = prompt | llm | StrOutputParser()
    return chain

def translate_text(chain, text, source_lang, target_lang):
    queries = [
        {
            'text': text,
            'source_lang': source_lang,
            'target_lang': target_lang
        },
    ]
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
        print(f"Query: {query}\nResponse: {result}\n")
