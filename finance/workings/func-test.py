def main():
    print(lookup("AMZN"))

    a = 2
    b = 2.5

    print(a * b)


def lookup(symbol):
    if symbol == "FB":
        symbol = { 'name': 'Facebook Inc - Class A','price': 366.365, 'symbol': 'FB'}
    elif symbol == "AAPL":
        symbol = { 'name': 'Apple Inc','price': 146.77, 'symbol': 'AAPL'}
    elif symbol == "AMZN":
        symbol = { 'name': 'Amazon.com Inc.','price': 3626.39, 'symbol': 'FB'}
    elif symbol == "TSLA":
        symbol = { 'name': 'Tesla Inc','price': 644.78, 'symbol': 'TSLA'}
    else:
        print("try again!")
    return symbol


main()
