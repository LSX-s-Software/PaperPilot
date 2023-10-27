import jieba


def limit_str(input_str, max_bytes=30):
    encoded_str = input_str.encode("utf-8")

    if len(encoded_str) <= max_bytes:
        return input_str

    tokens = list(jieba.cut(input_str))
    total_bytes = 0
    tokenized_text = []

    for token in tokens:
        token_bytes = token.encode("utf-8")
        if total_bytes + len(token_bytes) <= max_bytes:
            tokenized_text.append(token)
            total_bytes += len(token_bytes)
        else:
            break

    return "".join(tokenized_text)
