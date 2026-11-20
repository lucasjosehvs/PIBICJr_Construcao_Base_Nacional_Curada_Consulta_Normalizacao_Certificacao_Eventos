##f
# top10Genericos.py
# Gera os top10 de eventos GENERICOS e NAO GENERICOS de um conjunto por vez.
#
# Uso: python top10Genericos.py N|NA|NPA|NCA
#
# Entradas (delimitador |, ordenadas por ocorrencia decrescente):
#   N    NOME-DO-EVENTO | OCORRENCIAS-EVENTO
#   NA   NOME-DO-EVENTO | ANO-DO-EVENTO | OCORRENCIAS-EVENTO-ANO
#   NPA  NOME-DO-EVENTO | PAIS-DO-EVENTO | ANO-DO-EVENTO | OCORRENCIAS-EVENTO-PAIS-ANO
#   NCA  NOME-DO-EVENTO | CIDADE-DO-EVENTO | ANO-DO-EVENTO | OCORRENCIAS-EVENTO-CIDADE-ANO
#
# Saidas (em DIR_SAIDA, delimitador ;):
#   top10_{conjunto}_genericas.csv       OCORRENCIAS;{colunas da chave}
#   top10_{conjunto}_nao_genericas.csv   OCORRENCIAS;{colunas da chave}
#
# Definicao de evento generico: nome formado apenas por tipo de evento + tema de
# atividade academica ampla (iniciacao cientifica, extensao, ensino, pesquisa,
# ciencia e tecnologia, semana academica), sem sigla, instituicao ou nome proprio.
# Ex.: "congresso iniciacao cientifica", "semana academica".
# Nao generico: "reuniao anual sbpc", "congresso iniciacao cientifica unesp".

import csv
import os
import re
import sys

# --- caminhos (preencher) ----------------------------------------------------
ARQUIVOS = {
    'N':   r'D:\BACKUP\Magela\conjuntoN_ordenado.csv',
    'NA':  r'D:\BACKUP\Magela\conjuntoNA_ordenado.csv',
    'NPA': r'D:\BACKUP\Magela\conjuntoNPA_ordenado.csv',
    'NCA': r'D:\BACKUP\Magela\conjuntoNCA_ordenado.csv',
}
DIR_SAIDA = r'D:\BACKUP\Magela\resultados'

# --- parametros --------------------------------------------------------------
DELIMITADOR_ENTRADA = '|'
DELIMITADOR_SAIDA = ';'
TAMANHO_TOP = 10

# --- classificacao -----------------------------------------------------------
TIPOS = {
    'congresso', 'seminario', 'encontro', 'jornada', 'semana', 'simposio',
    'forum', 'coloquio', 'workshop', 'mostra', 'feira', 'ciclo', 'curso',
    'palestra', 'conferencia', 'mesa', 'oficina', 'atividade', 'evento',
    'reuniao', 'debate', 'painel', 'roda', 'campanha', 'olimpiada',
    'maratona', 'festival', 'bienal', 'exposicao', 'salao',
}
QUALIFICADORES = {
    'nacional', 'internacional', 'regional', 'estadual', 'municipal', 'local',
    'brasileiro', 'brasileira', 'latino', 'latinoamericano', 'americano',
    'iberoamericano', 'mundial', 'anual', 'cientifico', 'cientifica',
    'academico', 'academica', 'universitario', 'universitaria', 'integrado',
    'integrada', 'online', 'virtual', 'presencial', 'remoto', 'hibrido',
    'gratuito', 'aberto', 'aberta', 'publico', 'publica', 'digital',
    'estudantil', 'discente', 'docente',
}
LIGACOES = {'de', 'da', 'do', 'das', 'dos', 'e', 'em', 'a', 'o', 'as', 'os',
            'para', 'com', 'sobre', 'no', 'na', 'nos', 'nas', 'ao', 'aos'}
TEMAS = {
    'iniciacao', 'cientifica', 'ciencia', 'ciencias', 'tecnologia',
    'tecnologias', 'pesquisa', 'extensao', 'ensino', 'graduacao', 'pos',
    'inovacao', 'empreendedorismo', 'divulgacao', 'popularizacao',
    'conhecimento',
}
TEMAS_FORTES = [
    'iniciacao cientifica', 'semana academica', 'semana universitaria',
    'semana cientifica', 'mostra cientifica', 'feira de ciencias',
    'feira de ciencia', 'divulgacao cientifica', 'popularizacao da ciencia',
    'ciencia e tecnologia', 'ciencia tecnologia', 'ciencia e inovacao',
    'extensao', 'ensino', 'pesquisa',
]
VOCABULARIO = TIPOS | QUALIFICADORES | TEMAS | LIGACOES


def classificar(nome: str) -> bool:
    """True se o nome do evento for generico."""
    nome = re.sub(r'\s+', ' ', nome.strip())
    if not nome or not any(t in nome for t in TEMAS_FORTES):
        return False
    return all(token in VOCABULARIO for token in nome.split())


def gravar(conjunto: str, rotulo: str, cabecalho: list, linhas: list) -> None:
    os.makedirs(DIR_SAIDA, exist_ok=True)
    caminho = os.path.join(DIR_SAIDA, f'top10_{conjunto}_{rotulo}.csv')
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f, delimiter=DELIMITADOR_SAIDA)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)
    print(f'  salvo: {caminho} ({len(linhas)} linhas)')


def top10(conjunto: str) -> None:
    arquivo = ARQUIVOS[conjunto]
    chaves = {
        'N':   [0],
        'NA':  [0, 1],
        'NPA': [0, 1, 2],
        'NCA': [0, 1, 2],
    }[conjunto]
    nomes_colunas = ['NOME-DO-EVENTO']
    if conjunto == 'NA':
        nomes_colunas.append('ANO-DO-EVENTO')
    elif conjunto == 'NPA':
        nomes_colunas += ['PAIS-DO-EVENTO', 'ANO-DO-EVENTO']
    elif conjunto == 'NCA':
        nomes_colunas += ['CIDADE-DO-EVENTO', 'ANO-DO-EVENTO']
    indice_occ = len(chaves)

    genericas, nao_genericas = [], []

    def inserir(lista, occ, linha):
        lista.append((occ, linha))
        lista.sort(key=lambda item: -item[0])
        del lista[TAMANHO_TOP:]

    with open(arquivo, encoding='utf-8') as f:
        cabecalho = next(f).rstrip('\n').split(DELIMITADOR_ENTRADA)
        if len(cabecalho) != indice_occ + 1:
            raise ValueError(f'cabecalho inesperado em {arquivo}: {cabecalho}')
        for linha in f:
            partes = linha.rstrip('\n').split(DELIMITADOR_ENTRADA)
            if len(partes) != indice_occ + 1:
                continue
            nome = partes[0]
            if not nome:
                continue
            try:
                occ = int(partes[indice_occ])
            except ValueError:
                continue
            valores = [partes[i] for i in chaves]
            chave = tuple(valores)
            if classificar(nome):
                if chave not in {item[1][0] for item in genericas}:
                    inserir(genericas, occ, (chave, occ))
            else:
                if chave not in {item[1][0] for item in nao_genericas}:
                    inserir(nao_genericas, occ, (chave, occ))
            # arquivo ordenado por ocorrencia: parar quando nada mais entra
            if len(genericas) == TAMANHO_TOP and len(nao_genericas) == TAMANHO_TOP:
                if occ < min(min(v for v, _ in genericas),
                             min(v for v, _ in nao_genericas)):
                    break

    cabecalho_saida = ['OCORRENCIAS'] + nomes_colunas

    def linhas(lista):
        return [[occ] + list(chave) for occ, (chave, _) in lista]

    gravar(conjunto, 'genericas', cabecalho_saida, linhas(genericas))
    gravar(conjunto, 'nao_genericas', cabecalho_saida, linhas(nao_genericas))


def main():
    conjunto = sys.argv[1].upper() if len(sys.argv) > 1 else ''
    if conjunto not in ARQUIVOS:
        sys.exit('uso: python top10Genericos.py N|NA|NPA|NCA')
    print(f'=== top10 genericas / nao genericas: {conjunto} ===')
    top10(conjunto)


if __name__ == '__main__':
    main()
