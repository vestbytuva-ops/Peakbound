class Mangekant:
    def __init__(self,antall_sider):
        self.antall_sider = antall_sider
        self.sidelengder = []
    def registrer_sidelengder(self):
        self.sidelengder = []
        for i in range(self.antall_sider):
            lengde = float(input(f"Lengde på side {i + 1}: "))
            self.sidelenger.append(lengde)
    def beregn_omkrets(self):
        return sum(self.sidelengder)
    def visInfo(self):
        print(f"Antall sider: {self.antall_sider}")
        print(f"Sidelenger: {self.sidelengder}")
        print(f"Omkrets: {self_omkrets():g}")
mangekanter = []

for i in range(4):
    print(f"\nRegisterer mangekant {i + 1}")
    antall = int(input("Hvor mange sider har mangekanten?"))
    mangekant.registrer_sidelenger()
    mangekanter.append(mangekant)

for i, mangekant in enumerate(mangekanter, start = 1):
    print(f"\nMangekant {i}")
    mangekant.visInfo()
