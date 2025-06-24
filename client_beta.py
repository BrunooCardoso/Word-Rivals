import socket
import threading
import tkinter as tk
from tkinter import messagebox


class ContextoClient:
    def __init__(self, master):
        self.master = master
        self.tempo_restante = 600  # Tempo inicial de 10 minutos
        
        master.title("Jogo Contexto - Cliente")

        self.words_ranked = []  # lista de (palavra, rank)
        self.word_set = set()  # Para evitar palavras duplicadas
        self.running = True
        self.game_started = False
        
        # Frame principal
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(pady=10)

        # Frame do timer
        self.timer_frame = tk.Frame(self.main_frame)
        self.timer_frame.pack(side=tk.TOP, pady=5)
        self.timer_label = tk.Label(self.timer_frame, text="Aguardando início...", font=('Arial', 12))
        self.timer_label.pack()

        # Frame de entrada
        self.entry_frame = tk.Frame(self.main_frame)
        self.entry_frame.pack(pady=5)
        
        self.label_info = tk.Label(self.entry_frame, text="Digite sua palavra:")
        self.label_info.pack(side=tk.LEFT)

        self.entry = tk.Entry(self.entry_frame,state=tk.DISABLED)
        self.entry.pack(side=tk.LEFT, padx=5)

        self.send_button = tk.Button(self.entry_frame, text="Enviar", command=self.send_word, state=tk.DISABLED)
        self.send_button.pack(side=tk.LEFT)

        # Lista de resultados
        self.result_frame = tk.Frame(self.main_frame)
        self.result_frame.pack(pady=10)
        
        self.result_list = tk.Listbox(self.result_frame, height=15, width=40)
        self.result_list.pack()

        # Conexão
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect(('172.20.21.49', 12345))
           
        except:
            messagebox.showerror("Erro", "Não foi possível conectar ao servidor.")
            master.destroy()
            return
        self.master.bind("<Return>", lambda event: self.send_word())
        # Thread para escutar o servidor
        threading.Thread(target=self.receive_messages, daemon=True).start()
        
    def update_timer(self):
        if not self.game_started:
            return

        minutos = self.tempo_restante / 60
        segundos = self.tempo_restante % 60
        self.timer_label.config(text=f"Tempo restante: {minutos:02d}:{segundos:02d}")

        if self.tempo_restante > 0:
            self.tempo_restante -= 1
            self.master.after(1000, self.update_timer)  # Agenda próxima atualização em 1s
        else:
            self.running = False

    def send_word(self):
        word = self.entry.get().strip().lower()
        if word:
            try:
                self.socket.send(word.encode('utf-8'))
                self.entry.delete(0, tk.END)
            except:
                messagebox.showerror("Erro", "Conexão perdida com o servidor.")
                self.master.destroy()

    def receive_messages(self):
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break

                buffer += data

                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.process_message(line.strip())

            except:
                break

        self.socket.close()

    def process_message(self, data):
        if data == "GAME_START":
            self.game_started = True
            self.entry.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
            self.timer_label.config(text="Tempo restante: 10:00")
            self.update_timer()  # Inicia o timer
        
        
        
        
        if data.startswith("WORD:"):
            _, palavra, rank = data.split(":")
            try:
                rank = int(rank)

                if palavra in self.word_set:
                    messagebox.showerror("Palavra repetida", f"Você já digitou a palavra: '{palavra}'")
                else:
                    self.words_ranked.append((palavra, rank))
                    self.word_set.add(palavra)
                    self.update_word_list()
            except:
                pass

        elif data == "UNKNOW":
            messagebox.showinfo("Palavra inválida", "Não conheço essa palavra ou ela é muito comum.")

        elif data == "WIN":
            messagebox.showinfo("Vitória!", "Parabéns! Você descobriu a palavra.")
            self.running = False

        elif data == "LOSS":
            messagebox.showinfo("Derrota", "Seu oponente descobriu a palavra.")
            self.running = False

        elif data == "TIME_OUT_WIN":
            messagebox.showinfo("Vitória por aproximação!", "Você venceu com o rank mais próximo.")
            self.running = False

        elif data == "TIME_OUT_LOSS":
            messagebox.showinfo("Derrota por tempo", "Seu adversário teve uma tentativa mais próxima.")
            self.running = False

        elif data == "TIME_OUT_DRAW":
            messagebox.showinfo("Empate!", "Ninguém venceu a partida.")
            self.running = False

    def update_word_list(self):
        self.result_list.delete(0, tk.END)
        for palavra, rank in sorted(self.words_ranked, key=lambda x: x[1]):
            self.result_list.insert(tk.END, f"{palavra}: {rank}")

    def close(self):
        self.running = False
        try:
            self.socket.close()
        except:
            pass
        self.master.destroy()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        client = ContextoClient(root)
        
        try:
            if root.winfo_exists():
                root.protocol("WM_DELETE_WINDOW", client.close)
                root.mainloop()
        except tk.TclError:
            print("Não foi possível conectar ao servidor. Verifique se o servidor está rodando.")
            pass  
    except Exception as e:
        print("Erro ao iniciar o cliente:", e)