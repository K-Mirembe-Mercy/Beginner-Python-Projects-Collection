multiples = list(range(3, 31, 3))
for i in multiples:
    print(multiples)
#exercise4,4
cubes = []
for i in range(1,11):
    cube = i**3
    cubes.append(cube)
print(cubes)
#exercise4,5(This is called list comprehension.)
cubes = [i**3 for i in range(1,11)]
print(cubes)