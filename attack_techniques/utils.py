############################ Miscellaneous functions ########################

def generate_from_payloads(payloads):
    if len(payloads) == 1:
        return payloads[0]
    if len(payloads) == 2:
        ret = []
        for i in range(0, len(payloads[0])):
            for j in range(0, len(payloads[1])):
                delim = " "
                if payloads[0][i] == "" or payloads[1][j] == "":
                    delim = ""
                ret += [payloads[0][i] + delim + payloads[1][j]]
        return ret
    else:
        ret = generate_from_payloads([payloads[len(payloads)-2], payloads[len(payloads)-1]])
        for i in reversed(range(0, len(payloads)-2)):
            ret = generate_from_payloads([payloads[i], ret])
        return ret

def get_substring_score(str_source, str_substr):
    score = 0.0
    source = " ".join(str_source.split())
    words = str_substr.split()
    patterns = []
    for i in range(1, len(words) - 1):
        patterns += [words[i-1] + " " + words[i] + " " + words[i+1]]

    score_delta = 1/len(patterns)
    for i in range(0, len(patterns)):
        if source.find(patterns[i]) != -1:
            score += score_delta
    return round(score,4)
