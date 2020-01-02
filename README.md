# argument_randomiser


```python
from argument_randomiser import randargs, IntRandomiser

@randargs()
def func(a, b):
    return a + b

i = IntRandomiser(0, 5)
j = IntRandomiser(5, 10)

print(func(a=i, b=j))
print(func(a=i, b=j))
print(func(a=i, b=j))
```
```
11
13
7
```

---

```python
func.call_history
```
```
>> [{a: 3, b: 8}, {a: 4, b: 9}, {a: 1, b: 6}]
```