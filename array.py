a = float(input("Skriv a sin x"))
b = float(input("Skriv a sin y"))
c = float(input("Skriv b sin x"))
d = float(input("Skriv b sin y"))
e = float(input("Skriv c sin x"))
f = float(input("Skriv c sin y"))

AB = ((d-b)**2+(c-a**2))**0.5
AC = ((f-b)**2+(e-a**2))**0.5
BC = ((f-d)**2+(e-a**2))**0.5

if AC**2==(AB**2+BC**2) or AB**2==(AC**2+BC**2) or BC**2==(AB**2+AC**2):
    print("Det er rettvinklet")
else:
    print("Nei")