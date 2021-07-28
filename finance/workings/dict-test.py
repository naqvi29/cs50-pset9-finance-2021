def main():
    portfolio = [ 
    {'symbol': 'AAPL', 'totalshares': 3},  
    {'symbol': 'AMZN', 'totalshares': 2},  
    {'symbol': 'FB', 'totalshares': 2},  
    {'symbol': 'TSLA', 'totalshares': 2} 
    ] 
     
    
    # #BEFORE
    hline()
    print("BEFORE")
    hsline()
    print("PORTFOLIO")
    print(portfolio)

    # # number of items in list
    # print("number of items in list")
    # print(len(portfolio))

    # # access portfolio symbol
    # print("access portfolio symbol")
    # print(portfolio[2]["symbol"])

    # # AFTER
    hline()
    print("AFTER")
    hsline()
    print("PORTFOLIO")
    
    totals_list = []

    # loop mechanics
    for i in range(len(portfolio)):
        # update portfolio dict with info from lookup()
        portfolio[i].update(lookup(portfolio[i]["symbol"]))
        
        # TODO - TOTAL = totalshares * price, add to dictionary
        totals = portfolio[i]["totalshares"] * portfolio[i]["price"]
        totals_list.append(totals)

        portfolio[i].update(totals = totals)

    print(portfolio)
    hline()

    print(totals_list)
    print(sum(totals_list))

    
def hline():
    num = 70
    for i in range(num):
        print("=",end="")
    print()
    return 


def hsline():
    num = 6
    for i in range(num):
        print("=",end="")
    print()
    return 


def lookup(symbol):
    if (symbol == "FB"):
        symbol = { 'name': 'Facebook Inc - Class A','price': 366.365, 'symbol': 'FB'}
    elif (symbol == "AAPL"):
        symbol = { 'name': 'Apple Inc','price': 146.77, 'symbol': 'AAPL'}
    elif (symbol == "AMZN"):
        symbol = { 'name': 'Amazon.com Inc.','price': 3626.39, 'symbol': 'AMZN'}
    elif (symbol == "TSLA"):
        symbol = { 'name': 'Tesla Inc','price': 644.78, 'symbol': 'TSLA'}
    else:
        print("try again!")
    return symbol


main()

# # sample lookup response
# lookup = { 
# 'name': 'Facebook Inc - Class A',  
# 'price': 366.365,  
# 'symbol': 'FB' 
# }


# # adds lookup result to FB
# portfolio[2].update(lookup)
# print(portfolio)
# hline()


# # success fully append/update FB key value pair
# https://www.geeksforgeeks.org/add-a-keyvalue-pair-to-dictionary-in-python/
# result of update and targetting
# [{'symbol': 'AAPL', 'totalshares': 3}, 
# {'symbol': 'AMZN', 'totalshares': 2}, 
# {'symbol': 'FB', 'totalshares': 2, 'name': 'Facebook Inc - Class A', 'price': 366.365}, 
# {'symbol': 'TSLA', 'totalshares': 2}]


# # success result of loop mechanics
# [{'symbol': 'AAPL', 'totalshares': 3, 'name': 'Apple Inc', 'price': 146.77}, 
# {'symbol': 'FB', 'totalshares': 2, 'name': 'Amazon.com Inc.', 'price': 3626.39}, 
# {'symbol': 'FB', 'totalshares': 2, 'name': 'Facebook Inc - Class A', 'price': 366.365}, 
# {'symbol': 'TSLA', 'totalshares': 2, 'name': 'Tesla Inc', 'price': 644.78}]


# # success after totalshare * price added to dict in loop
# [{'symbol': 'AAPL', 'totalshares': 3, 'name': 'Apple Inc', 'price': 146.77, 'totals': 440.31000000000006}, 
# {'symbol': 'AMZN', 'totalshares': 2, 'name': 'Amazon.com Inc.', 'price': 3626.39, 'totals': 7252.78}, 
# {'symbol': 'FB', 'totalshares': 2, 'name': 'Facebook Inc - Class A', 'price': 366.365, 'totals': 732.73}, 
# {'symbol': 'TSLA', 'totalshares': 2, 'name': 'Tesla Inc', 'price': 644.78, 'totals': 1289.56}]