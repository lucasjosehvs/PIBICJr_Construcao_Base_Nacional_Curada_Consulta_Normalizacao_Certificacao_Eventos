import csv
import pandas as pd

caminhoEntrada = r'E:\Magela\ordenadoNC.csv'
caminhoSaida   = r'E:\Magela\ordenadoNCexemplo.csv'

df = pd.read_csv(caminhoEntrada, sep=';', nrows=5000, on_bad_lines='skip')
df.to_csv(caminhoSaida, sep=';', index=False)

