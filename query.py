from Stack import Stack


def precedence(token):
    """ Precedence of supported operators """
    __precedence = {"&": 2, "|": 1, "~": 3}
    try:
        return __precedence[token]
    except KeyError:
        return -1


def is_left_bracket(token):
    """ Returns true if left bracket """
    return token == "("


def is_right_bracket(token):
    return token == ")"


def is_operator(token):
    return token in {"&", "|", "~"}


def infix_to_postfix(tokens):
    stack = Stack()
    postfix = list()

    for token in tokens:

        if is_left_bracket(token):
            # Left bracket "("
            stack.push(token)

        elif is_right_bracket(token):
            # Right bracket ")"
            while (not stack.is_empty()) and stack.peek() != "(":
                key = stack.pop()
                postfix.append(key)
            if not stack.is_empty() and stack.peek() != "(":
                raise ValueError("Query isn't well formatted")
            else:
                stack.pop()

        elif is_operator(token):
            # Operator
            while (
                not stack.is_empty()
                and stack.peek() != "("
                and precedence(token) <= precedence(stack.peek())
            ):
                postfix.append(stack.pop())
            stack.push(token)

        else:
            # Operand
            postfix.append(token)

    # Pop all the operator from the stack
    while not stack.is_empty():
        postfix.append(stack.pop())

    return postfix
