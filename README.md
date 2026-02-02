# Gerenciador de Senhas

Um gerenciador de senhas seguro e minimalista desenvolvido em Python, que utiliza criptografia de ponta para proteger suas credenciais.

## Descrição

Este projeto é um gerenciador de senhas baseado em linha de comando (CLI) que permite armazenar, buscar, atualizar e deletar senhas de forma segura. Todas as senhas são criptografadas utilizando a biblioteca `cryptography` com o algoritmo Fernet (AES-128 em modo CBC), e a chave de criptografia é derivada de uma senha mestra usando PBKDF2-HMAC-SHA256 com 100.000 iterações.

## Funcionalidades

- **Criptografia robusta**: Senhas protegidas com Fernet (AES-128)
- **Senha mestra**: Acesso ao gerenciador protegido por senha única
- **Adicionar senhas**: Cadastre novas credenciais de forma segura
- **Buscar senhas**: Encontre rapidamente as senhas por nome do serviço
- **Listar serviços**: Visualize todos os serviços cadastrados
- **Atualizar senhas**: Modifique senhas e usuários existentes
- **Deletar senhas**: Remova credenciais que não são mais necessárias
- **Armazenamento local**: Dados salvos em arquivo JSON criptografado

## Tecnologias Utilizadas

- **Python 3.13+**
- **cryptography**: Biblioteca para criptografia de dados
- **JSON**: Armazenamento local de dados
- **getpass**: Entrada segura de senhas no terminal

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/gerenciador-de-senhas.git
cd gerenciador-de-senhas
```

2. Crie um ambiente virtual:
```bash
python3 -m venv venv
```

3. Ative o ambiente virtual:
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Como Usar

1. Execute o programa:
```bash
python main.py
```

2. Na primeira execução, você será solicitado a criar uma **senha mestra**. **Não esqueça esta senha!** Ela é necessária para acessar todas as suas credenciais.

3. Após configurar a senha mestra, você terá acesso ao menu principal com as seguintes opções:
   - **1**: Adicionar nova senha
   - **2**: Buscar senha existente
   - **3**: Listar todos os serviços cadastrados
   - **4**: Atualizar senha existente
   - **5**: Deletar senha
   - **0**: Sair do programa

## Estrutura do Projeto

```
gerenciador-de-senhas/
├── venv/                  # Ambiente virtual (não versionado)
├── main.py               # Arquivo principal com interface CLI
├── crypto_utils.py       # Funções de criptografia
├── db_manager.py         # Gerenciamento do banco de dados JSON
├── senhas.json          # Arquivo de dados (criado automaticamente, não versionado)
├── requirements.txt     # Dependências do projeto
├── .gitignore          # Arquivos ignorados pelo Git
└── README.md           # Documentação do projeto
```

## Segurança

- **Derivação de chave segura**: Utiliza PBKDF2-HMAC-SHA256 com 100.000 iterações
- **Salt único**: Cada instalação gera um salt aleatório para maior segurança
- **Criptografia forte**: AES-128 em modo CBC via Fernet
- **Senha mestra irrecuperável**: Se você esquecer a senha mestra, não há como recuperar os dados (design intencional de segurança)
- **Armazenamento local**: Suas senhas nunca saem do seu computador

## Avisos Importantes

- **Nunca compartilhe sua senha mestra** com ninguém
- **Faça backups regulares** do arquivo `senhas.json` em local seguro
- **Não versione o arquivo `senhas.json`** no Git (já está no .gitignore)
- Se você **esquecer a senha mestra**, não há recuperação possível - todos os dados serão perdidos

## Redefinir Senha Mestra

Para redefinir a senha mestra (isso apagará todos os dados):

```bash
rm senhas.json
python main.py
```

O programa solicitará que você configure uma nova senha mestra.

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abrir um Pull Request

## Possíveis Melhorias Futuras

- [ ] Gerador de senhas aleatórias fortes
- [ ] Exportar/Importar backup criptografado
- [ ] Busca parcial por nome de serviço
- [ ] Indicador de força de senha
- [ ] Copiar senha para clipboard automaticamente
- [ ] Interface gráfica (GUI) com Tkinter ou PyQt
- [ ] Categorização de senhas (trabalho, pessoal, etc.)
- [ ] Histórico de alterações de senhas

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Autor

Desenvolvido por [Rodrigo Emilio]

---

**Dica**: Este é um projeto educacional. Para uso em produção, considere soluções estabelecidas como Bitwarden, KeePass ou 1Password.
