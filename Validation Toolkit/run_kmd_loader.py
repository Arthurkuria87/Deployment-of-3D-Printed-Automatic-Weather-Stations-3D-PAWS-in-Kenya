from modules.kmd_loader import KMDLoader



file = "data/reference/fivestndata.xlsx"



loader = KMDLoader(file)



kmd = loader.load()



print("\n\nTEMPERATURE / RAIN DATA")
print("=" * 80)

print(
    kmd["temperature_rain"].head()
)



print("\n\nPRESSURE / RH DATA")
print("=" * 80)

print(
    kmd["pressure_humidity"].head()
)