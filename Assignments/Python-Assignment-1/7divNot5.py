start = 2000
end = 3200
numbers = []

for i in range(start,end+1):
    if i % 5 == 0:
        continue
    elif i % 7 == 0:
        numbers.append(i)
    
for i in numbers:
    print(i, end=',')
        