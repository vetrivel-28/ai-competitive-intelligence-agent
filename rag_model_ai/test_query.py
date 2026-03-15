import builtins

queries = ["best gaming laptop with good performance", "quit"]
call_count = 0

def mock_input(prompt=""):
    global call_count
    print(prompt, end="", flush=True)
    val = queries[call_count]
    print(val)
    call_count += 1
    return val

builtins.input = mock_input

import rag_model
rag_model.main()
