from .base import ResourceCRUD

class AbandonedCheckouts(ResourceCRUD):
    endpoint = "checkouts"

    def post_cart_coupon(self, cart_id: int, cupom_id: int) -> dict | str:
        """
        Aplica um cupom de desconto em um carrinho abandonado.

        Args:
            cart_id (int): ID do carrinho que irá receber o cupom de desconto.
            cupom_id (int): ID do cupom a ser aplicado.

        Returns:
            dict | str: Resposta da API ou mensagem de erro.
        """
        endpoint = f"{self.endpoint}/{cart_id}/coupon"
        try:
            response = self.client.post(endpoint, data={"coupon_id": cupom_id})
            return response
        except Exception as e:
            return f"Erro ao aplicar cupom: {e}"
