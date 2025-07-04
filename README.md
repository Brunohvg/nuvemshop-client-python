🧰 nuvemshop-client-python
Um cliente Python robusto e intuitivo para a API da Nuvemshop (Tiendanube).

Desenvolvido para simplificar a criação de integrações, scripts e SDKs, com foco em organização, reuso e fácil manutenção.

🚀 Funcionalidades
✅ Cliente HTTP Resiliente: Gerencia requisições, autenticação e tratamento de erros de forma automática, com suporte a timeouts e retentativas configuráveis.

✅ Paginação Automática: Busque todos os recursos de um endpoint (ex: todos os produtos) com uma única chamada ao método .list_all().

✅ Fluxo de Autenticação OAuth 2.0: Módulo auxiliar para obter o access_token e store_id de novas lojas.

✅ Recursos Modulares: Operações da API organizadas por recursos (Products, Orders, Customers, etc.).

✅ Interface Fluida: Interaja com a API de forma natural com a factory embutida (client.products.get()).

✅ Estrutura Extensível: Uma classe ResourceCRUD genérica permite adicionar novos endpoints da API rapidamente.

✅ Projeto Instalável: Empacotado com pyproject.toml para ser facilmente instalado e distribuído.

📦 Instalação e Configuração
Clone o repositório:

git clone https://github.com/Brunohvg/nuvemshop-client-python.git
cd nuvemshop-client-python

Instale as dependências:

pip install -e .

Configure suas credenciais:
Para o fluxo de autenticação, crie um arquivo .env na raiz do projeto e adicione as credenciais da sua aplicação Nuvemshop. A biblioteca usa python-decouple para carregar essas variáveis.

CLIENT_ID="SEU_CLIENT_ID"
CLIENT_SECRET="SEU_CLIENT_SECRET"

🔧 Como Usar
O uso da biblioteca é dividido em dois passos principais: Autenticação e Comunicação com a API.

Passo 1: Autenticação (Obtendo o Access Token)
Use o módulo auth para trocar o code de autorização por um access_token e store_id.

from nuvemshop_client.auth import get_access_token
# ...
credentials = get_access_token("codigo_recebido_pela_nuvemshop")
access_token = credentials.get("access_token")
store_id = credentials.get("store_id")

Passo 2: Interagindo com a API
Com as credenciais, instancie o NuvemshopClient.

from nuvemshop_client import NuvemshopClient

client = NuvemshopClient(
    store_id=store_id,
    access_token=access_token,
    timeout=45,  # Opcional: tempo de espera por resposta
    retries=5    # Opcional: número de retentativas em caso de erro
)

# Obter um produto específico
produto = client.products.get(resource_id=12345)

# Obter TODOS os pedidos da loja, sem se preocupar com paginação
todos_os_pedidos = client.orders.list_all()

✨ Funcionalidades Avançadas
Paginação Automática
Para buscar todos os itens de um recurso sem precisar controlar as páginas manualmente, use o método .list_all().

# Em vez de fazer um loop em client.products.list(page=1), client.products.list(page=2)...
# Faça apenas isso:
todos_os_produtos = client.products.list_all(per_page=200) # per_page maior é mais eficiente

print(f"Total de produtos encontrados: {len(todos_os_produtos)}")

Este método está disponível em todos os recursos que herdam de ResourceCRUD.

Resiliência (Timeouts e Retentativas)
Ao inicializar o NuvemshopClient, você pode passar parâmetros para torná-lo mais robusto contra falhas de rede.

timeout: Tempo em segundos que o cliente esperará por uma resposta antes de desistir.

retries: Quantas vezes o cliente tentará novamente uma requisição que falhou por erros de servidor (como 500, 503) ou limite de requisições (429).

📚 Recursos Suportados
A maioria dos recursos suporta os métodos list, list_all, get, create, update, e delete.

client.products

client.orders

client.customers

client.abandoned_checkouts

client.webhooks

client.stores

❗ Tratamento de Erros
A biblioteca lança exceções específicas para facilitar a captura de erros:

NuvemshopClientError: Erro genérico na comunicação com a API.

NuvemshopClientAuthenticationError: Falha na autenticação.

NuvemshopClientNotFoundError: O recurso solicitado não foi encontrado (erro 404).

Sempre envolva as chamadas da biblioteca em blocos try/except para tratar possíveis falhas.

try:
    produto = client.products.get(99999999)
except NuvemshopClientNotFoundError as e:
    print(f"Produto não encontrado: {e}")
except NuvemshopClientError as e:
    print(f"Ocorreu um erro na API: {e}")
