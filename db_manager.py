#############################
# Imports
#############################

import json
import os

DB_FILE = 'senhas.json'

#############################
# funções para criar e manipular o banco de dados
#############################

# cria o arquivo de banco de dados se não existir
def inicializar_db():
    if not os.path.exists(DB_FILE):
        data = {
            'salt': None,
            'senhas': []
        }
        salvar_db(data)

# carrega o banco de dados
def carregar_db():
    if not os.path.exists(DB_FILE):
        inicializar_db()
    
    with open(DB_FILE, 'r') as f:
        return json.load(f)
    
# salva o banco de dados
def salvar_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Adiciona uma nova senha ao banco de dados
def adicionar_senha(servico, usuario, senha_criptografada):
    data = carregar_db()
    
    # Verifica se já existe
    for item in data['senhas']:
        if item['servico'].lower() == servico.lower():
            return False, "Serviço já cadastrado!"
    
    data['senhas'].append({
        'servico': servico,
        'usuario': usuario,
        'senha': senha_criptografada
    })
    
    salvar_db(data)
    return True, "Senha adicionada com sucesso!"

# Busca uma senha pelo nome do serviço
def buscar_senha(servico):
    data = carregar_db()
    
    for item in data['senhas']:
        if item['servico'].lower() == servico.lower():
            return item
    
    return None

# Lista todos os serviços cadastrados
def listar_servicos():
    data = carregar_db()
    return [item['servico'] for item in data['senhas']]

# Deleta uma senha pelo nome do serviço
def deletar_senha(servico):
    data = carregar_db()
    
    for i, item in enumerate(data['senhas']):
        if item['servico'].lower() == servico.lower():
            data['senhas'].pop(i)
            salvar_db(data)
            return True, "Senha deletada com sucesso!"
    
    return False, "Serviço não encontrado!"

# Atualiza uma senha existente
def atualizar_senha(servico, nova_senha_criptografada, novo_usuario=None):
    data = carregar_db()
    
    for item in data['senhas']:
        if item['servico'].lower() == servico.lower():
            item['senha'] = nova_senha_criptografada
            if novo_usuario:
                item['usuario'] = novo_usuario
            salvar_db(data)
            return True, "Senha atualizada com sucesso!"
    
    return False, "Serviço não encontrado!"

#############################
# Funções para manipular o salt
#############################

# Salva o salt no banco de dados
def salvar_salt(salt):
    data = carregar_db()
    data['salt'] = salt.hex()
    salvar_db(data)

# Obtém o salt do banco de dados
def obter_salt():
    data = carregar_db()
    if data['salt']:
        return bytes.fromhex(data['salt'])
    return None