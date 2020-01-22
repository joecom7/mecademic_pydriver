

def message2codepayload(message):
    """
    Convert a message in a (code,payload) tuple
    message must be:
    [code][payload]
    """

    if not message.startswith("["):
        raise ValueError("message2codepayload : invalid start char : {}".format(message))
    if not message.endswith("]"):
        raise ValueError("message2codepayload : invalid end char : {}".format(message))

    end_code_index = message.find("][")
    if end_code_index == -1:
        raise ValueError("message2codepayload : invalid message : {}".format(message))

    start_payload_index = end_code_index + 2

    code = message[1:end_code_index]
    payload = message[start_payload_index:-1]

    return (code,payload)

def messages2codepayload(messages):
    """
    Convert a list of messages in a list of tuple (code, payload)
    """
    out = []
    for message in messages:
        out.append( message2codepayload(message) )
    return out

def extract_payload_from_messages(code, messages):
    """
    Extract the payload corresponding to a specific code from message list [message1, message2, ...]
    Returns the first occurence of the corresponding payload or None 
    """
    payload = None
    for message in messages:
        this_code, this_payload = message2codepayload(message)
        if this_code == code:
            payload = this_payload
    return payload

def payload2tuple(payload, output_type = float):
    """
    Extract a tuple from a payload message
    usefull for messages that returns an array [a,b,c,d,....]
    payload: str
        the payload to be parsed
    output_type: a type
        the type to use to parse the payload (Default float)
    """
    splitted_payload = payload.split(',')
    return tuple((output_type(x) for x in splitted_payload))
    