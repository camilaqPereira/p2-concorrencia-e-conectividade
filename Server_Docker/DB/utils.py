from enum import Enum
from json import load, dump
import os
import numpy as np
import networkx as nx
from threading import Lock

## 
#   @brief: Classe utilizada para o gerenciamento dos arquivos utilizados no armazenamento de dados do servidor
#   @note: Extende a classe Enum
##
class FilePathsManagement(Enum):
    PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    USERS_FILE_PATH = PARENT_DIR+'\\DB\\users.json'
    TICKETS_FILE_PATH = PARENT_DIR+'\\DB\\tickets.json'
    GRAPH_FILE_PATH = PARENT_DIR+'\\DB\\graph.json'


## 
#   @brief: Classe utilizada para o gerenciamento do grafo de trechos e dos dados dos voos
##
class ServerData:

    graph_lock = Lock() #mutex para o acesso ao grafo

    def __init__(self):
        self.path_locks:dict = {}
        self.graph:nx.DiGraph = self.__init_graph()
        self.destinations:list[str] = list(self.graph)
        self.__init_database()

    ##
    #   @brief: Método utilizado inicializar os arquivos de users e tickets. Cria um novo arquivo e o inicializa com um JSON vazio
    #   caso o arquivo não exista
    #   @note Gera uma excessão do tipo OSError caso não consiga criar os arquivos
    ##
    def __init_database(self):
        try:
            if not os.path.exists(FilePathsManagement.USERS_FILE_PATH.value):
                with open(FilePathsManagement.USERS_FILE_PATH.value, 'x') as file: #criando arquivo de usuários
                    dump({}, file)
            
            if not os.path.exists(FilePathsManagement.TICKETS_FILE_PATH.value):
                with open(FilePathsManagement.TICKETS_FILE_PATH.value, 'x') as file: #criando arquivo de tickets
                    dump({}, file)
        
        except OSError as e:
            print(f'[SERVER] Could not init properly the users and tickets files. {e}')
            raise


##
#   @brief: Método utilizado inicializar o grafo de rotas
#   @return new_grah - DiGraph carregado do arquivo de grafos do servidor.
#   Caso contrário, retorna um DiGraph vazio
##
    def __init_graph(self):
        try:
            with open(FilePathsManagement.GRAPH_FILE_PATH.value, 'r') as file:
                adjacency_dict:dict = load(file)

            new_graph = nx.DiGraph()
            for node, edges in adjacency_dict.items():
                for neighbor, attrs in edges.items():
                    self.path_locks[(node, neighbor)] = Lock()
                    new_graph.add_edge(node, neighbor, **attrs)

        except FileNotFoundError:
            new_graph =  nx.DiGraph()
        finally:
            #TODO: solicitar grafos dos nós vizinhos e dar o merge
            pass
        return new_graph
            


##
#   @brief: Método utilizado atualizar o valor de uma aresta no grafo
#   @param: origin - nó origem
#   @param: destination - nó destino
#   @param: new_weiht - novo valor da aresta
#   @return True o peso da aresta foi atualizado. Caso contrário, retorna falso
## 
    def __set_graph_edge_weight(self, origin:str, destination:str, new_weight:int):
            if self.graph.has_edge(origin, destination):
                with self.path_locks[(origin, destination)]:
                    self.graph[origin][destination]["weight"] = new_weight
                #TODO: notify other servers
                return True
            else:
                print(f"[SERVER] Could not update edge weight({origin}, {destination})")
                return False
            
        

##
#   @brief: Método decrementa os assentos de todos os voos passados. Caso, após o decremento
#   o número de assentos zere, o grafo e a matriz são atualizados.
#   Ao fim, os arquivos do grafo e dos trechos são atualizados
#
#   @param routes: lista de tuplas contendo todos os trechos que devem ser decrementados
#   @return: True se a operação for bem sucedida. Caso contrário, False
## 
    def dec_all_routes(self, routes:list[tuple[str,str]]):
        raise NotImplementedError()

##
#   @brief: Método busca os três menores caminhos disponíveis entre a origem e o destino.
#
#   @param: match - nó de origem
#   @param: destination - nó de destino
#   @return: Lista com as informações dos voos nos caminhos. Retorna None caso: a
#   origem seja igual ao destino, a origem ou o destino não sejam nós do grafo ou
#   nenhum caminho disponível seja encontrado
## 
    def search_route(self, match:str, destination:str):
        try:
            if match == destination:
                raise ValueError()
            
            shortest_paths:list = list(nx.shortest_simple_paths(self.graph, source=match, target=destination,weight="weight"))
            return shortest_paths[:3]
        except (nx.NetworkXNoPath, nx.NetworkXError, ValueError) as err:
            return None
        
            
##
#   @brief: Classe usada para gerenciamento do arquivo de users
## 

class UsersData:
    #Mutex para acesso ao arquivo de users
    users_file_lock = Lock()

    ##
    #   @brief: Método usado para carregar o arquivo de usuários
    #   @return: dict contém as informaões do arquivo JSON.
    #
    #   @raises: FileNotFoundError caso o arquivo não seja encontrado
    ##
    @classmethod
    def load_users(cls):
        try:
            with cls.users_file_lock:
                with open(FilePathsManagement.USERS_FILE_PATH.value, 'r') as file:
                    users = load(file)
            
            return users
        
        except FileNotFoundError:
            print(f'[SERVER] Could not find users file')
            raise
    
##
#   @brief: Método atualiza o arquivo de usuários com a nova informação
#   @param: email - email do novo user
#   @param: token - token do novo user
#   @return: True se a operação for bem sucedida. Caso contrário, False
## 
    @classmethod
    def save_user(cls, email, token):
        try:
            with cls.users_file_lock:
                with open(FilePathsManagement.USERS_FILE_PATH.value, 'r+') as file:
                    users:dict = load(file)
                    if email in users:
                        raise ValueError('User already exists!')
                    else:
                        file.seek(0)
                        users[email] = token
                        dump(users, file, indent=4)
            return True
        except FileNotFoundError:
            print(f'[SERVER] Users file not found!')
            return False
        except ValueError:
            print(f'[SERVER] User email already exists.')
            return False
        
