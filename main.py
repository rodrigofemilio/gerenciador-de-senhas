#############################
# Imports
#############################

import getpass
from crypto_utils import (
    gerar_chave_from_senha, 
    criptografar, 
    descriptografar, 
    gerar_salt
)
from db_manager import (
    inicializar_db,
    adicionar_senha,
    buscar_senha,
    listar_servicos,
    deletar_senha,
    atualizar_senha,
    salvar_salt,
    obter_salt
)

#############################
# Senha mestra
#############################

# Configura a senha mestra na primeira execução
def configurar_senha_mestra():
    print("\n=== PRIMEIRA EXECUÇÃO ===")
    print("Configure sua senha mestra (não esqueça dela!)")
    
    while True:
        senha1 = getpass.getpass("Digite a senha mestra: ")
        senha2 = getpass.getpass("Confirme a senha mestra: ")
        
        if senha1 == senha2:
            salt = gerar_salt()
            salvar_salt(salt)
            print("\n✓ Senha mestra configurada com sucesso!")
            return gerar_chave_from_senha(senha1, salt)
        else:
            print("\n✗ As senhas não coincidem. Tente novamente.\n")

# Verifica a senha mestra nas proximas execuções
def verificar_senha_mestra():
    """Verifica a senha mestra"""
    salt = obter_salt()
    
    if not salt:
        return configurar_senha_mestra()
    
    tentativas = 3
    while tentativas > 0:
        senha = getpass.getpass("\nDigite a senha mestra: ")
        try:
            chave = gerar_chave_from_senha(senha, salt)
            # Tenta descriptografar algo para verificar se a senha está correta
            # Se houver senhas salvas, testa com a primeira
            servicos = listar_servicos()
            if servicos:
                item = buscar_senha(servicos[0])
                descriptografar(item['senha'], chave)
            return chave
        except:
            tentativas -= 1
            if tentativas > 0:
                print(f"\n✗ Senha incorreta! Tentativas restantes: {tentativas}")
            else:
                print("\n✗ Número máximo de tentativas excedido!")
                exit()

#############################
# Menu Principal e funções
#############################

# Exibe o menu principal
def menu_principal():
    print("\n" + "="*40)
    print("    GERENCIADOR DE SENHAS")
    print("="*40)
    print("\n1. Adicionar senha")
    print("2. Buscar senha")
    print("3. Listar serviços")
    print("4. Atualizar senha")
    print("5. Deletar senha")
    print("0. Sair")
    print("\n" + "="*40)

# Funções do menu principal
def main():
    inicializar_db()
    
    print("\n" + "="*40)
    print("  BEM-VINDO AO GERENCIADOR DE SENHAS")
    print("="*40)
    
    chave = verificar_senha_mestra()
    
    while True:
        menu_principal()
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == '1':
            print("\n--- ADICIONAR SENHA ---")
            servico = input("Nome do serviço: ").strip()
            usuario = input("Usuário/Email: ").strip()
            senha = getpass.getpass("Senha: ")
            
            senha_criptografada = criptografar(senha, chave)
            sucesso, mensagem = adicionar_senha(servico, usuario, senha_criptografada)
            print(f"\n{'✓' if sucesso else '✗'} {mensagem}")
        
        elif opcao == '2':
            print("\n--- BUSCAR SENHA ---")
            servico = input("Nome do serviço: ").strip()
            
            item = buscar_senha(servico)
            if item:
                senha_descriptografada = descriptografar(item['senha'], chave)
                print(f"\n✓ Senha encontrada!")
                print(f"Serviço: {item['servico']}")
                print(f"Usuário: {item['usuario']}")
                print(f"Senha: {senha_descriptografada}")
            else:
                print("\n✗ Serviço não encontrado!")
        
        elif opcao == '3':
            print("\n--- SERVIÇOS CADASTRADOS ---")
            servicos = listar_servicos()
            if servicos:
                for i, servico in enumerate(servicos, 1):
                    print(f"{i}. {servico}")
            else:
                print("Nenhum serviço cadastrado ainda.")
        
        elif opcao == '4':
            print("\n--- ATUALIZAR SENHA ---")
            servico = input("Nome do serviço: ").strip()
            
            item = buscar_senha(servico)
            if item:
                print(f"\nServiço encontrado: {item['servico']}")
                print(f"Usuário atual: {item['usuario']}")
                
                novo_usuario = input("Novo usuário (Enter para manter): ").strip()
                nova_senha = getpass.getpass("Nova senha: ")
                
                nova_senha_criptografada = criptografar(nova_senha, chave)
                sucesso, mensagem = atualizar_senha(
                    servico, 
                    nova_senha_criptografada, 
                    novo_usuario if novo_usuario else None
                )
                print(f"\n{'✓' if sucesso else '✗'} {mensagem}")
            else:
                print("\n✗ Serviço não encontrado!")
        
        elif opcao == '5':
            print("\n--- DELETAR SENHA ---")
            servico = input("Nome do serviço: ").strip()
            confirma = input(f"Tem certeza que deseja deletar '{servico}'? (s/n): ").strip().lower()
            
            if confirma == 's':
                sucesso, mensagem = deletar_senha(servico)
                print(f"\n{'✓' if sucesso else '✗'} {mensagem}")
            else:
                print("\n✗ Operação cancelada.")
        
        elif opcao == '0':
            print("\n👋 Até logo!")
            break
        
        else:
            print("\n✗ Opção inválida!")

if __name__ == "__main__":
    main()