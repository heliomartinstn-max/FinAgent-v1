from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from api.models import APIToken
import json

User = get_user_model()


class APITokenAuthTests(TestCase):
    """Testa a segurança de autenticação por token Bearer."""

    def setUp(self):
        """Cria um usuário e token de teste antes de cada teste."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@finagent.com',
            password='senha123',
            nome_completo='Usuário de Teste'
        )
        self.token = APIToken.objects.create(user=self.user, descricao='Token de teste')

    def test_acesso_sem_token_retorna_401(self):
        """Deve retornar 401 se nenhum token for enviado."""
        response = self.client.post('/api/v1/risk/analyze/', content_type='application/json')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertIn('erro', data)

    def test_acesso_com_token_invalido_retorna_401(self):
        """Deve retornar 401 se o token enviado não existir no banco."""
        response = self.client.post(
            '/api/v1/risk/analyze/',
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer token_invalido_que_nao_existe'
        )
        self.assertEqual(response.status_code, 401)

    def test_acesso_com_formato_errado_retorna_401(self):
        """Deve retornar 401 se o cabeçalho não seguir o formato 'Bearer <token>'."""
        response = self.client.post(
            '/api/v1/risk/analyze/',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}'  # Formato errado (Token ao invés de Bearer)
        )
        self.assertEqual(response.status_code, 401)


class RiskAnalyzeTests(TestCase):
    """Testa o endpoint de análise de risco de crédito."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser2',
            email='test2@finagent.com',
            password='senha123',
            nome_completo='Usuário de Teste 2'
        )
        self.token = APIToken.objects.create(user=self.user, descricao='Token teste risco')
        self.auth_header = f'Bearer {self.token.key}'
        self.url = '/api/v1/risk/analyze/'
        self.payload_valido = {
            "empresa_nome": "Empresa Teste Ltda.",
            "faturamento_anual": 1200000,
            "endividamento_total": 300000,
            "liquidez_corrente": 1.8,
            "rentabilidade_pl": 14.5
        }

    def test_analise_com_dados_validos_retorna_200(self):
        """Deve retornar 200 e os campos esperados com dados corretos."""
        response = self.client.post(
            self.url,
            data=json.dumps(self.payload_valido),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth_header
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('classificacao', data)
        self.assertIn('probabilidade_inadimplencia', data)
        self.assertIn('recomendacao', data)

    def test_analise_sem_campo_obrigatorio_retorna_400(self):
        """Deve retornar 400 e indicar o campo ausente."""
        payload_incompleto = {"empresa_nome": "Empresa X"}  # Falta todos os campos numéricos
        response = self.client.post(
            self.url,
            data=json.dumps(payload_incompleto),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth_header
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('campos_invalidos', data)
        self.assertIn('faturamento_anual', data['campos_invalidos'])

    def test_analise_com_faturamento_negativo_retorna_400(self):
        """Deve retornar 400 se faturamento for negativo."""
        payload = self.payload_valido.copy()
        payload['faturamento_anual'] = -1000
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth_header
        )
        self.assertEqual(response.status_code, 400)


class ForecastPredictTests(TestCase):
    """Testa o endpoint de previsão de tendências financeiras."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser3',
            email='test3@finagent.com',
            password='senha123',
            nome_completo='Usuário de Teste 3'
        )
        self.token = APIToken.objects.create(user=self.user, descricao='Token teste forecast')
        self.auth_header = f'Bearer {self.token.key}'
        self.url = '/api/v1/forecast/predict/'

    def test_forecast_com_dados_validos_retorna_200(self):
        """Deve retornar 200 e os campos de projeção e SWOT."""
        payload = {
            "empresa_nome": "Empresa Forecast S.A.",
            "historico_receitas": [100000, 115000, 130000, 125000, 140000],
            "meses_projecao": 3
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth_header
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('analise_tendencia', data)
        self.assertIn('valores_projetados', data)
        self.assertIn('swot', data)
        self.assertIn('plano_acao', data)
        self.assertEqual(len(data['valores_projetados']), 3)

    def test_forecast_com_historico_menor_que_3_retorna_400(self):
        """Deve retornar 400 se o histórico tiver menos de 3 períodos."""
        payload = {
            "empresa_nome": "Empresa Y",
            "historico_receitas": [100000, 120000],  # Só 2 meses — inválido!
            "meses_projecao": 3
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth_header
        )
        self.assertEqual(response.status_code, 400)

    def test_forecast_com_projecao_acima_de_12_retorna_400(self):
        """Deve retornar 400 se tentar projetar mais de 12 meses."""
        payload = {
            "empresa_nome": "Empresa Z",
            "historico_receitas": [100000, 120000, 130000, 145000],
            "meses_projecao": 15  # Acima do limite de 12!
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth_header
        )
        self.assertEqual(response.status_code, 400)
