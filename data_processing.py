import pandas as pd
import numpy as np
from datetime import datetime, date
import os
import logging
from typing import List, Dict, Optional, Tuple
from cache_manager import cache_manager, cached_dataframe
from config_paths import BASE_DIR, DATA_DIR, PROCESSED_DIR

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, file_path: Optional[str] = None):
        """
        Inicializa o processador de dados.
        
        Args:
            file_path: Caminho opcional para o arquivo de dados. Se não fornecido, usa o caminho padrão.
        """
        # Tenta usar Parquet primeiro, depois Excel
        parquet_path = os.path.join(PROCESSED_DIR, "temp.parquet")
        excel_path = file_path or os.path.join(DATA_DIR, "temp.xlsx")
        
        # Prioriza Parquet se existir
        if os.path.exists(parquet_path):
            self.file_path = parquet_path
            self.use_parquet = True
            logger.info(f"Usando arquivo Parquet: {self.file_path}")
        else:
            self.file_path = excel_path
            self.use_parquet = False
            logger.info(f"Usando arquivo Excel: {self.file_path}")
        
        self.df = None
        self.cidades = []
        self.anos = []
        self.cidade_uf = {
            'Rio Branco': 'AC',
            'Maceió': 'AL',
            'Macapá': 'AP',
            'Manaus': 'AM',
            'Salvador': 'BA',
            'Fortaleza': 'CE',
            'Brasília': 'DF',
            'Vitória': 'ES',
            'Goiânia': 'GO',
            'São Luís': 'MA',
            'Cuiabá': 'MT',
            'Campo Grande': 'MS',
            'Belo Horizonte': 'MG',
            'Belém': 'PA',
            'João Pessoa': 'PB',
            'Curitiba': 'PR',
            'Recife': 'PE',
            'Teresina': 'PI',
            'Rio de Janeiro': 'RJ',
            'Natal': 'RN',
            'Porto Alegre': 'RS',
            'Porto Velho': 'RO',
            'Boa Vista': 'RR',
            'Florianópolis': 'SC',
            'São Paulo': 'SP',
            'Aracaju': 'SE',
            'Palmas': 'TO'
        }
        # NÃO carrega dados no __init__ - será carregado sob demanda (lazy loading)
        # Isso permite que o servidor inicie rapidamente no Render
        # self.load_data()  # REMOVIDO para permitir inicialização rápida

    def load_data(self) -> pd.DataFrame:
        """
        Carrega os dados do arquivo Parquet (prioritário) ou Excel.
        
        Returns:
            DataFrame com os dados carregados.
        """
        try:
            logger.info(f"Tentando carregar dados do arquivo: {self.file_path}")
            
            if not os.path.exists(self.file_path):
                logger.warning(f"Arquivo não encontrado: {self.file_path}")
                logger.info(f"Tentando localizar arquivo em DATA_DIR: {DATA_DIR}")
                # Tenta encontrar em DATA_DIR
                filename = os.path.basename(self.file_path)
                alt_path = os.path.join(DATA_DIR, filename)
                if os.path.exists(alt_path):
                    logger.info(f"Arquivo encontrado em DATA_DIR: {alt_path}")
                    self.file_path = alt_path
                else:
                    logger.error(f"Arquivo não encontrado em nenhum local. Verifique se {filename} está em {DATA_DIR}")
                    return pd.DataFrame()
            
            # Tenta carregar do cache primeiro
            cache_key = f"main_data_{os.path.getmtime(self.file_path) if os.path.exists(self.file_path) else 0}"
            cached_df = cache_manager.get(cache_key)
            if cached_df is not None:
                logger.info("Dados carregados do cache")
                self.df = cached_df
                self.cidades = sorted(cached_df["cidade"].unique())
                self.anos = sorted(cached_df["year"].unique())
                return cached_df
            
            logger.info("Arquivo encontrado, iniciando leitura...")
            
            # Carrega Parquet ou Excel
            if self.use_parquet:
                df = pd.read_parquet(self.file_path, engine='pyarrow')
                logger.info(f"Dados Parquet lidos com sucesso. Shape: {df.shape}")
            else:
                df = pd.read_excel(self.file_path)
                logger.info(f"Dados Excel lidos com sucesso. Shape: {df.shape}")
            
            # Processa apenas se necessário (Parquet já vem processado)
            if not self.use_parquet:
                logger.info("Processando dados...")
                df["index"] = pd.to_datetime(df["index"], errors="coerce")
                if "isHW" in df.columns:
                    df["isHW"] = df["isHW"].apply(lambda x: str(x).upper())
                if "index" in df.columns:
                    df["year"] = df["index"].dt.year
                    df["month"] = df["index"].dt.month
                
                # Filtrar dados até 2023
                if "year" in df.columns:
                    df = df[df["year"] <= 2023]
            
            self.df = df
            self.cidades = sorted(df["cidade"].unique())
            self.anos = sorted(df["year"].unique())
            
            # Salva no cache
            cache_manager.set(cache_key, df, use_joblib=True)
            
            logger.info(f"Dados processados com sucesso. Cidades encontradas: {len(self.cidades)}")
            logger.info(f"Anos encontrados: {len(self.anos)}")
            return df
                
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {str(e)}")
            logger.exception("Detalhes do erro:")
            return pd.DataFrame()

    @cached_dataframe(key_prefix="hw_monthly")
    def calculate_hw_monthly(self, cidade: str, ano: int) -> pd.DataFrame:
        """
        Calcula a frequência mensal de ondas de calor para um ano específico.
        
        Args:
            cidade: Nome da cidade
            ano: Ano para análise
            
        Returns:
            DataFrame com a frequência mensal
        """
        if self.df is None or self.df.empty:
            logger.warning("DataFrame vazio, não é possível calcular frequência mensal")
            return pd.DataFrame()
            
        # Filtra os dados para a cidade e ano específicos
        dff = self.df[
            (self.df["cidade"] == cidade) & 
            (self.df["year"] == ano)
        ].copy()
        
        # Converte a coluna de data para datetime se ainda não for
        dff["index"] = pd.to_datetime(dff["index"])
        
        # Cria um DataFrame com todos os meses do ano
        all_months = pd.date_range(start=f"{ano}-01-01", end=f"{ano}-12-31", freq="M")
        all_months_df = pd.DataFrame({
            "mes": all_months.strftime("%B"),
            "month": all_months.month
        })
        
        # Calcula a frequência de ondas de calor por mês
        monthly_counts = dff[dff["isHW"] == "TRUE"].groupby(dff["index"].dt.month).size().reset_index(name="frequencia")
        monthly_counts.columns = ["month", "frequencia"]
        
        # Combina com todos os meses e preenche com 0 onde não há ondas de calor
        monthly_counts = all_months_df.merge(
            monthly_counts, on="month", how="left"
        ).fillna({"frequencia": 0})
        
        # Ordena os meses corretamente
        month_order = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        monthly_counts["mes"] = monthly_counts["mes"].map(lambda x: x)
        monthly_counts = monthly_counts.sort_values("month")
        
        return monthly_counts[["mes", "frequencia"]]

    @cached_dataframe(key_prefix="hw_monthly_all")
    def calculate_hw_monthly_all_years(self, cidade: str) -> pd.DataFrame:
        """
        Calcula a frequência mensal de ondas de calor para todos os anos.
        
        Args:
            cidade: Nome da cidade
            
        Returns:
            DataFrame com a frequência mensal total
        """
        if self.df is None or self.df.empty:
            logger.warning("DataFrame vazio, não é possível calcular frequência mensal")
            return pd.DataFrame()
            
        # Filtra os dados para a cidade específica
        dff = self.df[self.df["cidade"] == cidade].copy()
        
        # Converte a coluna de data para datetime se ainda não for
        dff["index"] = pd.to_datetime(dff["index"])
        
        # Cria um DataFrame com todos os meses
        all_months = pd.DataFrame({
            "mes": ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"],
            "month": range(1, 13)
        })
        
        # Calcula a frequência de ondas de calor por mês
        monthly_counts = dff[dff["isHW"] == "TRUE"].groupby(dff["index"].dt.month).size().reset_index(name="frequencia")
        monthly_counts.columns = ["month", "frequencia"]
        
        # Combina com todos os meses e preenche com 0 onde não há ondas de calor
        monthly_counts = all_months.merge(
            monthly_counts, on="month", how="left"
        ).fillna({"frequencia": 0})
        
        # Ordena os meses corretamente
        monthly_counts = monthly_counts.sort_values("month")
        
        return monthly_counts[["mes", "frequencia"]]

    @cached_dataframe(key_prefix="hw_events")
    def calculate_hw_events(self, cidade: str, ano: int) -> pd.DataFrame:
        """
        Calcula os eventos de ondas de calor por mês para um ano específico.
        Um evento é considerado quando há 3 ou mais dias consecutivos de onda de calor (isHW == TRUE).
        
        Args:
            cidade: Nome da cidade
            ano: Ano para análise
            
        Returns:
            DataFrame com os eventos de ondas de calor por mês
        """
        if self.df is None or self.df.empty:
            logger.warning("DataFrame vazio, não é possível calcular eventos de ondas de calor")
            return pd.DataFrame()

        df_cidade = self.df[self.df['cidade'] == cidade].copy()
        df_cidade_ano = df_cidade[df_cidade['index'].dt.year == ano].copy()
        
        # Identifica os dias de onda de calor (isHW == TRUE)
        df_cidade_ano['isHW_bool'] = df_cidade_ano['isHW'] == "TRUE"
        
        # Agrupa por períodos consecutivos de isHW_bool
        # Reseta o índice para garantir que a numeração do grupo seja sequencial após o filtro do ano
        df_cidade_ano = df_cidade_ano.reset_index()
        df_cidade_ano['group'] = (df_cidade_ano['isHW_bool'] != df_cidade_ano['isHW_bool'].shift()).cumsum()
        
        # Filtra apenas os grupos que são ondas de calor (isHW_bool == True)
        hw_groups = df_cidade_ano[df_cidade_ano['isHW_bool']].copy()
        
        # Calcula a duração de cada período de onda de calor
        hw_periods = hw_groups.groupby(['month', 'group']).size().reset_index(name='duration')
        
        # Filtra apenas períodos com 3 ou mais dias
        hw_periods = hw_periods[hw_periods['duration'] >= 3]
        
        # Conta o número de eventos (grupos válidos) por mês
        # Usa o group para contar cada evento único
        hw_events = hw_periods.groupby(['month'])['group'].nunique().reset_index(name='frequencia')
        
        # Cria o DataFrame final com todos os meses
        months = pd.DataFrame({
            'mes': ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"],
            'month': range(1, 13)
        })
        
        # Combina com todos os meses e preenche com 0 onde não há eventos
        hw_events = pd.merge(
            months,
            hw_events,
            on='month',
            how='left'
        ).fillna({'frequencia': 0})
        
        # Ordena os meses corretamente
        hw_events = hw_events.sort_values('month')
        
        return hw_events[['mes', 'frequencia']]

    @cached_dataframe(key_prefix="hw_events_all")
    def calculate_hw_events_all_years(self, cidade: str) -> pd.DataFrame:
        """
        Calcula os eventos de ondas de calor por mês para todos os anos.
        Um evento é considerado quando há 3 ou mais dias consecutivos de onda de calor (isHW == TRUE).
        
        Args:
            cidade: Nome da cidade
            
        Returns:
            DataFrame com os eventos de ondas de calor por mês para todos os anos
        """
        if self.df is None or self.df.empty:
            logger.warning("DataFrame vazio, não é possível calcular eventos de ondas de calor")
            return pd.DataFrame()

        df_cidade = self.df[self.df['cidade'] == cidade].copy()

        # Identifica os dias de onda de calor (isHW == TRUE)
        df_cidade['isHW_bool'] = df_cidade['isHW'] == "TRUE"
        
        # Agrupa por períodos consecutivos de isHW_bool
        df_cidade['group'] = (df_cidade['isHW_bool'] != df_cidade['isHW_bool'].shift()).cumsum()
        
        # Filtra apenas os grupos que são ondas de calor (isHW_bool == True)
        hw_groups = df_cidade[df_cidade['isHW_bool']].copy()
        
        # Calcula a duração de cada período de onda de calor
        # Precisamos agrupar por year, month e group para a duração correta por mês/evento
        hw_periods = hw_groups.groupby(['year', 'month', 'group']).size().reset_index(name='duration')
        
        # Filtra apenas períodos com 3 ou mais dias
        hw_periods = hw_periods[hw_periods['duration'] >= 3]
        
        # Conta o número de eventos (grupos válidos) por mês ao longo de todos os anos
        # Usa o group para contar cada evento único
        hw_events = hw_periods.groupby(['month'])['group'].nunique().reset_index(name='frequencia')
        
        # Cria o DataFrame final com todos os meses
        months = pd.DataFrame({
            'mes': ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"],
            'month': range(1, 13)
        })
        
        # Combina com todos os meses e preenche com 0 onde não há eventos
        hw_events = pd.merge(
            months,
            hw_events,
            on='month',
            how='left'
        ).fillna({'frequencia': 0})
        
        # Ordena os meses corretamente
        hw_events = hw_events.sort_values('month')
        
        return hw_events[['mes', 'frequencia']]

    def get_heat_wave_days(self, cidade: str) -> List[date]:
        """
        Retorna os dias com ondas de calor (isHW == TRUE) para uma cidade.
        
        Args:
            cidade: Nome da cidade
            
        Returns:
            Lista de datas com ondas de calor
        """
        if self.df is None or self.df.empty:
            logger.warning("DataFrame vazio, não é possível obter dias de ondas de calor")
            return []
            
        # Filtra apenas onde isHW é explicitamente 'TRUE'
        return self.df[
            (self.df['cidade'] == cidade) &
            (self.df['isHW'] == "TRUE")
        ]['index'].dt.date.tolist()

    @cached_dataframe(key_prefix="heatmap_data")
    def prepare_heatmap_data(self) -> pd.DataFrame:
        """
        Prepara dados para o heatmap de ondas de calor (dias) por ano e cidade.
        
        Returns:
            DataFrame formatado para o heatmap
        """
        if self.df is None or self.df.empty:
            logger.warning("DataFrame vazio, não é possível preparar dados do heatmap")
            return pd.DataFrame()
            
        # Agrupa os dados por cidade e ano, contando apenas os dias que são ondas de calor
        df_heatmap_days = self.df[
            (self.df["isHW"] == "TRUE") # Filtra apenas dias de onda de calor
        ].groupby(
            ["cidade", "year"]
        ).size().reset_index(name="count") # Renomeia para 'count' para consistência com eventos
        
        # Preenche combinações de cidade/ano sem dias de onda de calor com 0, incluindo todos os anos de 1981 a 2023
        all_combinations = pd.MultiIndex.from_product(
            [self.cidades, list(range(1981, 2024))],
            names=["cidade", "year"]
        ).to_frame(index=False)
        
        df_heatmap_days = all_combinations.merge(
            df_heatmap_days, on=["cidade", "year"], how="left"
        ).fillna({"count": 0})
        
        return df_heatmap_days

    def get_available_years(self):
        """Retorna a lista de anos disponíveis nos dados."""
        if self.df is not None and not self.df.empty:
            return sorted(self.df['year'].unique().tolist())
        return []

    def get_heat_wave_events(self, cidade: str) -> List[date]:
        """
        Retorna uma lista de datas que fazem parte de eventos de ondas de calor
        (3 ou mais dias consecutivos com isHW == TRUE).
        
        Args:
            cidade: Nome da cidade
            
        Returns:
            Lista de datas que fazem parte de eventos de ondas de calor
        """
        if self.df is None or self.df.empty:
            logger.warning("DataFrame vazio, não é possível obter dias de eventos de ondas de calor")
            return []
            
        df_cidade = self.df[self.df['cidade'] == cidade].copy()
        
        # Identifica os dias de onda de calor (isHW == TRUE)
        df_cidade['isHW_bool'] = df_cidade['isHW'] == "TRUE"
        
        # Agrupa por períodos consecutivos de isHW_bool
        df_cidade['group'] = (df_cidade['isHW_bool'] != df_cidade['isHW_bool'].shift()).cumsum()
        
        # Filtra apenas os grupos que são ondas de calor (isHW_bool == True)
        hw_groups = df_cidade[df_cidade['isHW_bool']].copy()

        # Calcula a duração de cada período (sem agrupar por mês ou ano aqui)
        hw_periods = hw_groups.groupby('group').size().reset_index(name='duration')
        
        # Filtra apenas períodos com 3 ou mais dias
        valid_groups = hw_periods[hw_periods['duration'] >= 3]['group'].tolist()
        
        # Retorna as datas dos períodos válidos
        return df_cidade[df_cidade['group'].isin(valid_groups)]['index'].dt.date.tolist()

    @cached_dataframe(key_prefix="heatmap_events")
    def prepare_heatmap_events_data(self) -> pd.DataFrame:
        """
        Prepara dados para o heatmap de eventos de ondas de calor (3+ dias) por ano e cidade.
        Um evento é definido como uma sequência de 3 ou mais dias consecutivos com isHW == TRUE.
        
        Returns:
            DataFrame formatado para o heatmap de eventos
        """
        if self.df is None or self.df.empty:
            logger.warning("DataFrame vazio, não é possível preparar dados do heatmap de eventos")
            return pd.DataFrame()

        df_copy = self.df.copy()

        # Identifica os dias de onda de calor (isHW == TRUE)
        df_copy['isHW_bool'] = df_copy['isHW'] == "TRUE"

        # Ordena por cidade e data para garantir sequência correta
        df_copy = df_copy.sort_values(['cidade', 'index'])

        # Identifica períodos consecutivos de ondas de calor para cada cidade
        df_copy['_temp_group'] = df_copy.groupby('cidade')['isHW_bool'].transform(
            lambda x: (x != x.shift()).cumsum()
        )

        # Filtra apenas os dias que são ondas de calor
        hw_sequences = df_copy[df_copy['isHW_bool']].copy()

        # Calcula a duração de cada sequência por cidade e grupo
        sequence_durations = hw_sequences.groupby(['cidade', '_temp_group']).size().reset_index(name='duration')

        # Identifica os grupos que correspondem a eventos (duração >= 3)
        event_groups = sequence_durations[sequence_durations['duration'] >= 3][['cidade', '_temp_group']].copy()

        # Marca os dias que fazem parte de eventos de onda de calor
        df_copy['is_event'] = False
        
        # Merge com event_groups para marcar os dias que estão nos grupos válidos
        df_copy = pd.merge(
            df_copy.reset_index(drop=True), 
            event_groups.reset_index(drop=True), 
            on=['cidade', '_temp_group'], 
            how='left', 
            indicator=True
        )
        
        df_copy['is_event'] = df_copy['_merge'] == 'both'
        df_copy = df_copy.drop(columns=['_merge', '_temp_group'])

        # Identifica o início de cada evento (primeiro dia de cada sequência válida)
        df_copy['event_start'] = df_copy.groupby('cidade')['is_event'].transform(
            lambda x: (x & (~x.shift().fillna(False))).astype(int)
        )

        # Conta o número de eventos por cidade e ano
        df_heatmap_events = df_copy.groupby(['cidade', 'year'])['event_start'].sum().reset_index(name='count')

        # Preenche combinações de cidade/ano sem eventos com 0
        all_combinations = pd.MultiIndex.from_product(
            [self.cidades, list(range(1981, 2024))],
            names=['cidade', 'year']
        ).to_frame(index=False)

        df_heatmap_events = all_combinations.merge(
            df_heatmap_events, on=['cidade', 'year'], how='left'
        ).fillna({'count': 0})

        return df_heatmap_events 