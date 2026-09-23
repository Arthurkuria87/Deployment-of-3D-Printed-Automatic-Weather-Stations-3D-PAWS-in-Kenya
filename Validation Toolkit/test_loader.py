from modules.chords_loader import CHORDSLoader


file = "data/raw/April 2026 kenya-kisumu-intl-airport-met.csv"


loader = CHORDSLoader(file)


metadata, data = loader.load()


print("\nMETADATA")
print("----------------")

for k,v in metadata.items():

    print(k,":",v)



print("\nCOLUMNS")
print("----------------")

for c in data.columns:

    print(c)



print("\nROWS")
print(data.head())