def f(x):
    return x**(0.5)
a=0
b=1
N=100
dx = (b-a)/N
s=0
for i in range(N+1):
    x = a+i*dxs=s+f(x)
print(round(s/N+1),2)