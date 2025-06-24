from gensim.models import KeyedVectors
from preprocess import preprocess_embeddings

preprocess_embeddings('glove_s300.txt', 'glove_s300.filtered.txt')

word_vectors = KeyedVectors.load_word2vec_format('glove_s300.filtered.txt', binary=False, no_header=True)
word_vectors.save('vectors.kv')
