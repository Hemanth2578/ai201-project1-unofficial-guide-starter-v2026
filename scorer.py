import os, sys

def judge(question, expects, answer, results) -> bool:
    '''
    Evaluate whether expected answer is in results.

    Should ask these questions after the scoring:
    1. Did you retrive the right thing? If not, fix top_k, chunking
    2. Did the model use what you retrived? If not, fix the prompts etc

    '''
    if not expects:
        return False
    return expects.strip().lower() in (answer or "").lower()
