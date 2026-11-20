import csv
import pandas as pd # type: ignore

caminhoEntrada = r'E:\Magela\conjuntoNPA_ordenado.csv'
caminhoSaida   = r'E:\Magela\exemplos_conjuntoNPA_ordenado.csv'

df = pd.read_csv(caminhoEntrada, sep=';', nrows=5000, on_bad_lines='skip')
df.to_csv(caminhoSaida, sep=';', index=False)

