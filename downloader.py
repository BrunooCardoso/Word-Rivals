import requests
from tqdm import tqdm

url = "http://143.107.183.175:22980/download.php?file=embeddings/glove/glove_s300.zip"
caminho_local =  "glove_s300.zip"

response = requests.get(url, stream=True)
total_size = int(response.headers.get('content-length', 0))

with open(caminho_local, 'wb') as arquivo, tqdm(
    desc=caminho_local,
    total=total_size,
    unit='iB',
    unit_scale=True,
    unit_divisor=1024,
) as barra:
    for dados in response.iter_content(chunk_size=1024):
        tamanho = arquivo.write(dados)
        barra.update(tamanho)