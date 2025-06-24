import socket
import threading
import tkinter as tk
from tkinter import messagebox
from gensim.models import KeyedVectors
from ranking import calc_ranking


class ServerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Servidor Contexto")

        self.label = tk.Label(master, text="Escreva a palavra da partida:")
        self.label.pack()

        self.word_entry = tk.Entry(master)
        self.word_entry.bind("<Return>", lambda event: self.start_server())
        self.word_entry.pack()

        self.start_button = tk.Button(master, text="Ligar Servidor", command=self.start_server)
        self.start_button.pack()

        self.status_label = tk.Label(master, text="Aguardando início...")
        self.status_label.pack()

        # Timer display
        self.timer_frame = tk.Frame(master)
        self.timer_frame.pack(pady=10)
        self.timer_label = tk.Label(self.timer_frame, text="Tempo restante: 10:00", font=('Arial', 14))
        self.timer_label.pack()

        # Configuração de socket
        self.host = '172.20.21.49'
        self.port = 12345
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []

        self.word_vectors = KeyedVectors.load('vectors.kv')
        self.word_vectors.fill_norms()
        self.ranking_cache = {}

        self.running = False
        self.tempo_restante = 600  # 10 minutos em segundos
        self.game_started = False
        
        
        
        self.event_TIME_OUT = threading.Event()
        self.event_WINNER = threading.Event()
    def start_server(self):
        self.palavra_partida = self.word_entry.get().strip().lower()

        if not self.palavra_partida:
            messagebox.showerror("Erro", "Digite uma palavra!")
            return

        try:
            _ = self.word_vectors[self.palavra_partida]
        except KeyError:
            messagebox.showerror("Erro", f"Escolha uma palavra válida.")
            return

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        self.ranking_cache = calc_ranking(self.word_vectors, self.palavra_partida)

        self.start_button.config(state='disabled')
        self.word_entry.config(state='disabled')
        self.status_label.config(text="Servidor iniciado. Aguardando 2 jogadores...")

        self.running = True
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while len(self.clients) < 2 and self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                self.clients.append(client_socket)
                self.update_status(f"Jogador {len(self.clients)} conectado: {addr}")
            except:
                break

        if len(self.clients) == 2:
            self.update_status("Dois jogadores conectados. Jogo iniciado.")
            self.game_started = True
            
            for client_socket in self.clients:
                client_socket.send(f"GAME_START\n".encode('utf-8'))
            
            self.update_timer()  # Inicia a contagem regressiva
            
            self.best_guess = {}  # (palavra, ranking)
            
            for client_socket in self.clients:
                self.best_guess[client_socket] = ("", float('inf')) # nicializa o melhor palpite de cada cliente
                
            for client_socket in self.clients:
                threading.Thread(target=self.handle_clients_game, args=(client_socket,), daemon=True).start()

    def update_timer(self):
        if not self.game_started:
            return

        minutos = self.tempo_restante // 60
        segundos = self.tempo_restante % 60
        self.timer_label.config(text=f"Tempo restante: {minutos:02d}:{segundos:02d}")

        if self.tempo_restante > 0:
            self.tempo_restante -= 1
            self.master.after(1000, self.update_timer)
        else:
            self.event_TIME_OUT.set()

    def handle_clients_game(self, client_socket):
        
        
        while not self.event_TIME_OUT.is_set() and not self.event_WINNER.is_set():
            try:
                client_socket.settimeout(0.5)
                message = client_socket.recv(1024).decode('utf-8').strip().lower()

                if not message:
                    continue

                if message == self.palavra_partida:
                    self.event_WINNER.set()
                    continue

                try:
                    _ = self.word_vectors[message]
                except KeyError:
                    client_socket.send("UNKNOW\n".encode('utf-8'))
                    continue

                rank = self.ranking_cache.get(message)
                client_socket.send(f"WORD:{message}:{rank}\n".encode('utf-8'))
                
                if rank < self.best_guess[client_socket][1]:
                    self.best_guess[client_socket] = (message, rank)
                    
                
                    

            except socket.timeout:
                continue
            except:
                break


        # Verifica se algum cliente ganhou
        if self.event_WINNER.is_set():
            self.handle_winner(client_socket)
            return
        # Se o tempo acabou, verifica o melhor palpite
        if self.event_TIME_OUT.is_set():
            self.handle_timeout_results()
            return
        
    def handle_winner(self, winner_socket):
        for client in self.clients:
            if client == winner_socket:
                client.send("WIN\n".encode('utf-8'))
            else:
                client.send("LOSS\n".encode('utf-8'))
        self.close_connections()
        self.update_status("Jogo encerrado. Um jogador venceu.")
        

    def handle_timeout_results(self):

        if self.best_guess:
            winner = min(self.best_guess.items(), key=lambda x: x[1][1])[0] # cliente com menor ranking
            
            for client_socket in self.clients:
                if client_socket == winner:
                    client_socket.send("TIME_OUT_WIN\n".encode('utf-8'))
                else:
                    client_socket.send("TIME_OUT_LOSS\n".encode('utf-8'))
        else:
            for client_socket in self.clients:
                client_socket.send("TIME_OUT_DRAW\n".encode('utf-8'))
        
        self.close_connections()

    def close_connections(self):
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.clients.clear()
        try:
            self.server_socket.close()
        except:
            pass
        self.running = False

    def update_status(self, text):
        self.status_label.config(text=text)

if __name__ == "__main__":
    root = tk.Tk()
    gui = ServerGUI(root)
    root.mainloop()