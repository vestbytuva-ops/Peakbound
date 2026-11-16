def f(x):
    return x**2+3*x+1
h = 0.000000001

def dfx(x):
    return (f(x+h)-f(x))/h
a = 1
b = 3
N=100
dx = (b-a)/N
verdi = (f(b)-f(a))/(b-a)

for i in range(N):
    x = a + dx
    nyverdi = dfx(x)
    if abs(nyverdi-verdi) < 0.000001:
        print(round(x,2))
        break
