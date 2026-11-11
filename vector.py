xA = float(input("x-koordinaten til A: "))
yA = float(input("y-koordinaten til A: "))

xB = float(input("x-koordinaten til B: "))
yB = float(input("y-koordinaten til B: "))

xC = float(input("x-koordinaten til C: "))
yC = float(input("y-koordinaten til C: "))

xT = (xA + xB + xC) / 3
yT = (yA + yB + yC) / 3

print(f"Tyngdepunktet er T = ({xT}, {yT})")