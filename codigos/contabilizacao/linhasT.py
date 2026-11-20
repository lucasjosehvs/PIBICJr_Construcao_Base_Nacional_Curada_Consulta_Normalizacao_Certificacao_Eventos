with open(r'D:\BACKUP\Magela\csvs\conjuntoNPA_ordenado\conjuntoNPA_ordenado.csv', encoding='utf-8') as f:
    total_linhas = sum(1 for linha in f)

print(f"O arquivo tem {total_linhas} linhas.")
