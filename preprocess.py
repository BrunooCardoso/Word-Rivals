import re
import unicodedata
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from tqdm import tqdm  # para barra de progresso (opcional)
import nltk
nltk.download('stopwords')
nltk.download('punkt')


# Configurações de filtro

ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzáéíóúâêîôûãõç")
BANNED_SUBSTRINGS = {'http', 'www', '.com', '.br'}
PORTUGUESE_STOPWORDS = set(stopwords.words('portuguese'))

# Baixa stopwords do NLTK (executar uma vez)


# Carrega stopwords do português


def is_valid_word(word):
    """Verifica se a palavra atende todos os critérios de filtro"""
    
    # Normaliza a palavra para apenas caracteres minúsculos
    normalized = word.lower()
    
    if len(normalized) == 1:
        return False
    
    # Verifica caracteres permitidos
    if not all(c in ALLOWED_CHARS for c in normalized):
        return False
    
    # Verifica substrings proibidas
    if any(sub in normalized for sub in BANNED_SUBSTRINGS):
        return False
    
    # Verifica padrões inválidos (muitas repetições)
    if re.search(r'(.)\1{2,}', normalized):
        return False
    
    # Verifica se não é stopword
    if normalized in PORTUGUESE_STOPWORDS:
        return False
    
    return True

def preprocess_embeddings(input_file, output_file):
    """
    Processa um arquivo de embeddings e salva uma versão filtrada
    
    Args:
        input_file (str): Caminho do arquivo de embeddings original
        output_file (str): Caminho para salvar o arquivo processado
    """
    embeddings_processed = 0
    skipped_words = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
        open(output_file, 'w', encoding='utf-8') as outfile:
        
        # Usa tqdm para mostrar progresso (opcional)
        for line in tqdm(infile, desc='Processando embeddings'):
            parts = line.split()
            if not parts:
                continue
                
            word = parts[0]
            
            if is_valid_word(word):
                try:
                    # Verifica a dimensão do embedding (assume 300D)
                    vector = [float(x.replace(',', '.')) for x in parts[1:]]
                    if len(vector) == 300:
                        # Escreve a linha processada no novo arquivo
                        outfile.write(f"{word} {' '.join(parts[1:])}\n")
                        embeddings_processed += 1
                    else:
                        skipped_words += 1
                except (ValueError, IndexError):
                    skipped_words += 1
            else:
                skipped_words += 1
    
    print(f"\nPré-processamento concluído!")
    print(f"Embeddings válidos salvos: {embeddings_processed}")
    print(f"Palavras ignoradas: {skipped_words}")




