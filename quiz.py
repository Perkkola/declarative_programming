def eval(a,b,c):
    return (not a or not b) and (not b or c) and (not c or a)

arr = [[False, False, False],
       [False, False, True],
       [False, True, False],
       [False, True, True],
       [True, False, False],
       [True, False, True],
       [True, True, False],
       [True, True, True]]

for x in arr:
    print(eval(x[0], x[1], x[2]))