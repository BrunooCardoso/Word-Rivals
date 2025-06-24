
def calc_ranking(word_vectors,palavra_do_dia: str) -> dict:
    """
    Calcula o ranking de similaridade de todas as palavras em relação à `palavra_do_dia`
    e retorna um dicionário {palavra: posição}, onde a posição começa em 1 (mais similar).

    Args:
        palavra_do_dia (str): Palavra de referência para o cálculo do ranking.

    Returns:
        dict: Dicionário no formato {palavra: posição_ranking}.
    """
    # Calcula a similaridade de todas as palavras com a palavra_do_dia
    palavras_ordenadas = word_vectors.most_similar(palavra_do_dia, topn=len(word_vectors))
    
    # Cria um dicionário {palavra: posição} (posição inicia em 2,1 para a palavra do dia)
    ranking_posicoes = {palavra[0]: pos +2 for pos, palavra in enumerate(palavras_ordenadas) }
    return ranking_posicoes
