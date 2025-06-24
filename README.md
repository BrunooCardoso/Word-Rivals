# X1Contexto
Projeto apresentado na disciplina de Programação em Tempo Real, do curso de Engenharia de Sistemas, Unimontes.
O projeto consiste na implementação de um sistema cliente-servidor com um jogo de encontrar a palavra escolhida, inspirado no jogo Contexto.
A ideia é dois clientes se enfrentarem e quem descobrir a palavra primeiro ou chegar mais próximo vence. 

# 🚀 Guia de Execução do Projeto

```bash
# Sequência de execução (rode na ordem):
1. python downloader.py       # Baixa modelos/datasets
2. python preprocess.py       # Pré-processa os dados
3. python load_model.py       # Carrega o modelo
4. python server.py           # Inicia o servidor (terminal 1)
5. python client.py           # Roda o cliente (terminal 2 e 3 para jogar) 
