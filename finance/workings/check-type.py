shares = ["abc","23", "21av", "1.24", "-3", ""]

for i in range(len(shares)):
    print("[i = " + str(i) + "]")
    if shares[i].isalnum() == True:
        print(shares[i] + " - is alpha OR numeric")

    if shares[i].isnumeric() == True:
        print(shares[i] + " - is numeric only")

    if shares[i].isalpha() == True:
        print(shares[i] + " - is alpha only")
    print()


# alphabet only
# str.isalpha()

# alphabet or numeric
# str.isalnum()

# numeric only
# str.isnumeric()

# Return True if the float instance is finite with integral value, and False otherwise
# float.is_integer()