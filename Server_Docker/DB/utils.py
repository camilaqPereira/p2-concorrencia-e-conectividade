from enum import Enum
from json import load, dump
import os
import numpy as np
from scipy.sparse import csr_matrix, csgraph
from threading import Lock

## 
#   @brief: Classe utilizada para o gerenciamento dos arquivos utilizados no armazenamento de dados do servidor
#   @note: Extende a classe Enum
##
class FilePathsManagement(Enum):
    PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    NODES_FILE_PATH = PARENT_DIR+'\\DB\\matches_and_destinations.txt'
    ROUTES_DATA_FILE_PATH = PARENT_DIR+'\\DB\\routes_data.json'
    USERS_FILE_PATH = PARENT_DIR+'\\DB\\users.json'
    TICKETS_FILE_PATH = PARENT_DIR+'\\DB\\tickets.json'
    GRAPH_FILE_PATH = PARENT_DIR+'\\DB\\graph.json'


##
#   @brief: Classe utilizada para o armazenamento das informações de cada rota
##
class Route:

    def __init__(self, match:str = '', destination:str = '', sits:int = 0, id:str = ''):
        self.match = match
        self.destination = destination
        self.sits = sits
        self.id = id

    def __repr__(self):
        return f"Route('{self.match}', '{self.destination}',{self.sits}, '{self.id}')"
    
##
#   @brief: Método retorna um dict representativo da instância
#   @return dict com todos os valores dos atributos da instância
##
    def as_dict(self):
        return {'match': self.match, 'destination': self.destination, 'sits': self.sits, 'id': self.id}

    ## 
    #   @brief: Método utilizado para atualizar os atributos de instância de um objeto
    ##
    def from_dict(self, data):
        self.match = data['match']
        self.destination = data['destination']
        self.sits = data['sits']
        self.id = data['id']

## 
#   @brief: Classe utilizada para o gerenciamento do grafo de trechos e dos dados dos voos
##
class ServerData:

    matrix_lock = Lock() #mutex para o acesso à matriz de adjacência
    flights_lock = Lock() #mutes para o acess aos dados dos trechos
    adjacency_lock = Lock() #mutex para o acesso à lista de adjacência

    def __init__(self):
        self.adjacency_list:dict[int, list[tuple[int,int]]] = self.__init_adjacency_list()
        self.sparse_matrix:csr_matrix = self.__create_sparse_matrix()
        self.matches_and_destinations:list[str] = self.__init_matches_and_destinations()
        self.flights:dict[tuple[int,int], Route] = self.__init_flights()
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
#   @brief: Método utilizado para customizar o carregamento de arquivo do tipo json com chaves do tipo tuple
#   @return loaded_dict - objeto do tipo dict 
##
    def __parse_to_dict(self, item):
        loaded_dict = {int(key): value for key, value in item}
        
        for key in loaded_dict:
            loaded_dict[key] = [tuple(row) for row in loaded_dict[key]]
        
        return loaded_dict

##
#   @brief: Método utilizado inicializar a lista de adjacência das rotas
#   @return adj_list - dict carregado do arquivo de users do servidor.
#   Caso contrário, retorna um dict vazio
#   Cada linha da matriz indica um nó vizinho e o respectivo peso da aresta
##
    def __init_adjacency_list(self):
        try:
            with open(FilePathsManagement.GRAPH_FILE_PATH.value, 'r') as file:
                adj_list = load(file, object_pairs_hook=self.__parse_to_dict)
        
        except FileNotFoundError:
            adj_list = {}
        
        return adj_list

##
#   @brief: Método utilizado inicializar a matriz esparsa de adjacência das rotas
#   @return Objeto do tipo csr_matrix 
##
    def __create_sparse_matrix(self):
        nodes_count = len(self.adjacency_list.keys())
        mtx = np.zeros((nodes_count, nodes_count))

        for vertex, neighbor in self.adjacency_list.items():
            for item in neighbor:
                mtx[vertex, item[0]] = item[1]
        
        return csr_matrix(mtx, dtype=int)

##
#   @brief: Método utilizado inicializar a lista de origens e destinos
#   @return nodes - lista carregado do arquivo de nós. Caso contrário, retorna uma lista vazia
##
    def __init_matches_and_destinations(self):
        try:
            with open(FilePathsManagement.NODES_FILE_PATH.value, 'r') as nodes_file:
                nodes = nodes_file.read()
            nodes = list(nodes.split(","))
        
        except FileNotFoundError:
            nodes = []
        
        return nodes 
    
##
#   @brief: Método utilizado carregar os dados dos voos
#   @return flights - dict cujas chaves são tuplas no formato (origem, destino) e os valores são objetos do tipo Route
#   Caso o arquivo não exista, retorna um dict vazio
##
    def __init_flights(self):
        flights:dict[tuple[int,int], Route] = {}

        try:
            with open(FilePathsManagement.ROUTES_DATA_FILE_PATH.value, 'r') as flights_file:
                flights = load(flights_file, object_pairs_hook=self.__parse_flights_json)
            
        except FileNotFoundError:
            pass
        
        return flights

    def __parse_flights_json(self, item):
        return {eval(key): eval(value) for key, value in item}

##
#   @brief: Método utilizado atualizar o valor de uma aresta na lista de adjacência e na matriz esparsa
#   @param: origin - nó origem
#   @param: destination - nó destino
#   @param: new_weiht - novo valor da aresta
#   @raises KeyError se origin não for um nó no grafo
#           ValueError se origin e destination não forem adjacentes
## 
    def __set_graph_edge_weight(self, origin:int, destination:int, new_weight:int):
        try:
            neighbors = self.adjacency_list[origin]
            for neighbor in neighbors:

                if neighbor[0] == destination:
                    index = neighbors.index(neighbor)
                    self.adjacency_list[origin][index] = (destination, new_weight)
                    
                    with ServerData.matrix_lock:
                        self.sparse_matrix[origin, destination] = new_weight
                    return
            raise ValueError('Origin and destination are not adjacent')           
        except KeyError as err1:
            print(f'[SERVER] Match is not a key in adjacency list {err1}')
            raise
        except ValueError as err2:
            print(f'[SERVER] Could not update weight. {err2}')
            raise

##
#   @brief: Método decrementa os assentos de todos os voos passados. Caso, após o decremento
#   o número de assentos zere, o grafo e a matriz são atualizados.
#   Ao fim, os arquivos do grafo e dos trechos são atualizados
#
#   @param routes: lista de tuplas contendo todos os trechos que devem ser decrementados
#   @return: True se a operação for bem sucedida. Caso contrário, False
## 
    def dec_all_routes(self, routes:list[tuple[str,str]]):
        with ServerData.flights_lock:
            routes_keys = []
            # Verificando a disponibilidade das rotas
            for route in routes: 
                try:
                    flight_key = (self.matches_and_destinations.index(route[0]), self.matches_and_destinations.index(route[1]))
                    if not self.flights[flight_key].sits:
                        return False
                    routes_keys.append(flight_key)
                
                except ValueError as err:
                    print(f'[SERVER] Could not find node. {err}')
                    return False
                
                except KeyError as err2:
                    print(f'[SERVER] Could not find route. {err2} ')
                    return False
            #Decrementando os assentos
            for route in routes_keys:
                self.flights[route].sits -= 1

                #Atualizando o grafo e a matrix caso número de assentos zere
                if not self.flights[route].sits:
                    self.__set_graph_edge_weight(route[0], route[1], 9999)
           
            #Atualizando arquivo de trechos
            with open(FilePathsManagement.ROUTES_DATA_FILE_PATH.value, 'w') as file:
                serialized = {str(key): repr(value) for key, value in self.flights.items()}
                dump(serialized, file, indent=4)
       
        #Atualizando arquivo da lista de adjacência
        with ServerData.adjacency_lock:
            with open(FilePathsManagement.GRAPH_FILE_PATH.value, 'w') as file:
                dump(self.adjacency_list, file, indent=4)
        
        return True

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
            if match == destination: #verificando se os nós são iguais
                raise ValueError()
            
            match_index = self.matches_and_destinations.index(match)
            destination_index = self.matches_and_destinations.index(destination)
        except ValueError:
            return None

        with ServerData.matrix_lock:
            shortest_paths, predecessors_mtx = csgraph.yen(self.sparse_matrix, source = match_index, sink = destination_index, K=3, return_predecessors=True)

        if shortest_paths.size:
            paths = []
            for i in range(len(shortest_paths)):
                if(shortest_paths[i] > 9999): #checando por rotas esgotadas
                    continue
                
                new_path = []
                current_node = destination_index
                while current_node != match_index:
                    new_path.append(int(current_node))
                    current_node = predecessors_mtx[i,current_node]
                new_path.append(match_index)
                new_path.reverse()
                paths.append(new_path)
            return self.__convert_paths(paths)
        
        return None

##
#   @brief: Método busca as informações da lista de trechos passadas como parâmetros
#
#   @param paths: lista contendo os trechos  serem buscados
#   @return: lista contendo as informaões das rotas/voos
## 
    def __convert_paths(self, paths:list[list[int]]):
        routes = []

        with ServerData.flights_lock:
            for i in range(len(paths)):
                routes.append([])
                for j in range(len(paths[i])-1):
                    key = (paths[i][j], paths[i][j+1])
                    routes[i].append(self.flights[key].as_dict())
        return routes

            
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
        