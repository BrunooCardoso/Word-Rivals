from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def distance(p1:str, p2:str):
    
    vet1 = p1.split(" ")
    vet2 = p2.split(" ")
    
    vet1 = [float(x) for x in vet1]
    vet2 = [float(x) for x in vet2]
    
    vet1 = np.array(vet1)
    vet2 = np.array(vet2)
    
    
    
    sim = cosine_similarity(vet1.reshape(1,-1),vet2.reshape(1,-1))
    
    print(sim.shape)
    return sim[0][0]


with open("glove_s300.txt","r",encoding = "utf-8") as file:
    var = file.readlines()
    vec = {}
    
    for palavra in var[1:]:
        for p, i in zip(palavra, range(len(palavra))):
            if p == " ":
                vec[palavra[:i]] = palavra[i+1:]
                
                break
            
#palavra_chave = "camisa"        
while(True):
    palavra1 = input("Digite uma palavra: ") 
    palavra2=  input("Digite uma palavra: ") 
    try:
       
        palavra1 = palavra1.lower()
        palavra2 = palavra2.lower()
        
        dist = distance(vec[palavra1],vec[palavra2])
        print(dist)
    except KeyError:
        print("não tem filho")
        
        
        
