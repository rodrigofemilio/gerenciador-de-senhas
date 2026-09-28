"""Interface clássica de linha de comando."""

import getpass

from cryptography.fernet import InvalidToken

from crypto_utils import descriptografar, gerar_chave_from_senha, gerar_salt, criptografar
from db_manager import (
    adicionar_senha,
    atualizar_senha,
    buscar_senha,
    deletar_senha,
    inicializar_db,
    listar_servicos,
    obter_salt,
    obter_verificador,
    salvar_salt,
    salvar_verificador,
)


def configurar_senha_mestra():
    print("\n=== PRIMEIRA EXECUÇÃO ===")
    print("Configure sua senha mestra (não esqueça dela!)")
    while True:
        senha1 = getpass.getpass("Digite a senha mestra: ")
        senha2 = getpass.getpass("Confirme a senha mestra: ")
        if senha1 and senha1 == senha2:
            salt = gerar_salt()
            salvar_salt(salt)
            print("\n✓ Senha mestra configurada com sucesso!")
            chave = gerar_chave_from_senha(senha1, salt)
            salvar_verificador(criptografar("cofre-valido", chave))
            return chave
        print("\n✗ As senhas não coincidem ou estão vazias. Tente novamente.\n")


def verificar_senha_mestra():
    salt = obter_salt()
    if not salt:
        return configurar_senha_mestra()

    for tentativas in range(3, 0, -1):
        senha = getpass.getpass("\nDigite a senha mestra: ")
        chave = gerar_chave_from_senha(senha, salt)
        servicos = listar_servicos()
        try:
            verificador = obter_verificador()
            if verificador:
                descriptografar(verificador, chave)
            elif servicos:
                descriptografar(buscar_senha(servicos[0])["senha"], chave)
                salvar_verificador(criptografar("cofre-valido", chave))
            return chave
        except InvalidToken:
            if tentativas > 1:
                print(f"\n✗ Senha incorreta! Tentativas restantes: {tentativas - 1}")
    raise SystemExit("\n✗ Número máximo de tentativas excedido!")


def menu_principal():
    print("\n" + "=" * 40)
    print("    GERENCIADOR DE SENHAS")
    print("=" * 40)
    print("\n1. Adicionar senha\n2. Buscar senha\n3. Listar serviços")
    print("4. Atualizar senha\n5. Deletar senha\n0. Sair")
    print("\n" + "=" * 40)


def main():
    inicializar_db()
    print("\n" + "=" * 40 + "\n  BEM-VINDO AO GERENCIADOR DE SENHAS\n" + "=" * 40)
    chave = verificar_senha_mestra()

    while True:
        menu_principal()
        opcao = input("\nEscolha uma opção: ").strip()
        if opcao == "1":
            servico = input("Nome do serviço: ").strip()
            usuario = input("Usuário/Email: ").strip()
            senha = getpass.getpass("Senha: ")
            sucesso, mensagem = adicionar_senha(servico, usuario, criptografar(senha, chave))
            print(f"\n{'✓' if sucesso else '✗'} {mensagem}")
        elif opcao == "2":
            item = buscar_senha(input("Nome do serviço: ").strip())
            if item:
                print(f"\nServiço: {item['servico']}\nUsuário: {item['usuario']}"
                      f"\nSenha: {descriptografar(item['senha'], chave)}")
            else:
                print("\n✗ Serviço não encontrado!")
        elif opcao == "3":
            servicos = listar_servicos()
            print("\n".join(f"{i}. {s}" for i, s in enumerate(servicos, 1))
                  or "Nenhum serviço cadastrado ainda.")
        elif opcao == "4":
            servico = input("Nome do serviço: ").strip()
            if buscar_senha(servico):
                usuario = input("Novo usuário (Enter para manter): ").strip()
                senha = getpass.getpass("Nova senha: ")
                sucesso, mensagem = atualizar_senha(
                    servico, criptografar(senha, chave), usuario or None
                )
                print(f"\n{'✓' if sucesso else '✗'} {mensagem}")
            else:
                print("\n✗ Serviço não encontrado!")
        elif opcao == "5":
            servico = input("Nome do serviço: ").strip()
            if input(f"Deletar '{servico}'? (s/n): ").strip().lower() == "s":
                sucesso, mensagem = deletar_senha(servico)
                print(f"\n{'✓' if sucesso else '✗'} {mensagem}")
        elif opcao == "0":
            print("\n👋 Até logo!")
            return
        else:
            print("\n✗ Opção inválida!")
