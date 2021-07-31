def main():
    # just testing functions
    print(lookup("AMZN"))

    a = 2
    b = 2.5

    print(a * b)


def lookup(symbol):
    # lookup test
    if symbol == "FB":
        # get FB
        symbol = {'name': 'Facebook Inc - Class A', 'price': 366.365, 'symbol': 'FB'}
    elif symbol == "AAPL":
        # get sample AAPLE
        symbol = {'name': 'Apple Inc', 'price': 146.77, 'symbol': 'AAPL'}
    elif symbol == "AMZN":
        # get sample AMZN
        symbol = {'name': 'Amazon.com Inc.', 'price': 3626.39, 'symbol': 'FB'}
    elif symbol == "TSLA":
        symbol = {'name': 'Tesla Inc', 'price': 644.78, 'symbol': 'TSLA'}
    else:
        print("try again!")
    return symbol


main()
