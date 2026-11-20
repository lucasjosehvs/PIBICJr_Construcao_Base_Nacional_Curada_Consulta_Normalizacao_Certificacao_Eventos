caminho = r''
with open(caminho, "r", encoding="utf-8") as arquivo:
  for i in range(10000):
    linha = arquivo.readline()
    if not linha:
      break
    print(linha.strip())