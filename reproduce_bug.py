import pytest
from unittest.mock import MagicMock
from nuvemshop_sdk.utils.pagination import paginate

def test_paginate_with_dict_response_bug():
    # Mock de um fetcher que retorna um dicionário
    mock_fetcher = MagicMock(side_effect=[
        {"products": [{"id": 1}, {"id": 2}]},
        []
    ])
    
    # Agora esperatamos um TypeError porque adicionamos a guarda defensiva
    with pytest.raises(TypeError) as excinfo:
        list(paginate(mock_fetcher, per_page=50))
    
    assert "must return a list" in str(excinfo.value)
    print("Sucesso: Guarda defensiva capturou o erro esperado!")

def test_resource_crud_unwrapping():
    # Simular o comportamento corrigido do ResourceCRUD.list
    from nuvemshop_sdk.resources.base import ResourceCRUD
    
    mock_http = MagicMock()
    mock_http.get.return_value = {"products": [{"id": 10}]}
    
    resource = ResourceCRUD(mock_http)
    resource.endpoint = "products"
    
    result = resource.list()
    assert result == [{"id": 10}], f"Deveria ter desenvelopado o dict, mas obteve {result}"
    print("Sucesso: ResourceCRUD agora desenvelopa dicionários corretamente!")

if __name__ == "__main__":
    try:
        test_paginate_with_dict_response_bug()
        print("Teste passou (bug não encontrado)")
    except AssertionError as e:
        print(f"Bug confirmado: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
