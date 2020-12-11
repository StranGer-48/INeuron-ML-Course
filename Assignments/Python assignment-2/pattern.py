def pattern(n):
    for i in range(0,n):
        for j in range(0,i):
            print("* ",end="")
        print("\r")
    for i in range(n,2*n):
        for k in range(0,2*n-i):
            print("* ",end="")
        print("\r")

n = 5
pattern(n)
