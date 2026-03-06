#!/usr/bin/env python3
"""
Scraper para extrair dados do portfólio diário do IBOV da B3.
"""

import pandas as pd
import time
import json
import base64
from typing import List, Dict
import logging
import requests

from app.utils.data_cleaners import clean_number, clean_percentage, clean_text
from app.utils.constants import S3_PATH

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class IBOVScraper:

    def __init__(self):

        self.base_url = "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/"

        self.execution_time = time.strftime("%Y-%m-%d")
        self.partition_column = "anomesdia"

        self.output_folder = "data_exec"
        self.output_file = None

    def _encode_params(self, page: int):

        payload = {
            "language": "pt-br",
            "pageNumber": page,
            "pageSize": 120,
            "index": "IBOV",
            "segment": "1"
        }

        encoded = base64.b64encode(json.dumps(payload).encode()).decode()

        return encoded

    def _get_page(self, page: int):

        try:

            params = self._encode_params(page)

            url = self.base_url + params

            logger.info(f"Acessando página {page}")

            response = requests.get(url, timeout=30)

            if response.status_code != 200:
                logger.error(f"Erro HTTP {response.status_code}")
                return None

            return response.json()

        except Exception as e:
            logger.error(f"Erro request: {e}")
            return None

    def _extract_table_data(self, json_data) -> List[Dict]:

        data = []

        results = json_data.get("results")

        if not results:
            return data

        for item in results:

            row = {
                "codigo": clean_text(item.get("cod")),
                "acao": clean_text(item.get("asset")),
                "tipo": clean_text(item.get("type")),
                "qtde_teorica": clean_number(str(item.get("theoricalQty"))),
                "part_pct": clean_percentage(str(item.get("part"))),
                self.partition_column: self.execution_time
            }

            data.append(row)

        logger.info(f"{len(data)} registros extraídos")

        return data

    def _scrape(self) -> List[Dict]:

        all_data = []
        page = 1

        while True:

            json_data = self._get_page(page)

            if not json_data:
                break

            page_data = self._extract_table_data(json_data)

            if not page_data:
                break

            all_data.extend(page_data)

            page += 1

        return all_data

    def _validate_data(self, data: List[Dict]) -> List[Dict]:

        seen_codes = set()
        validated_data = []

        for item in data:

            code = item["codigo"]

            if code not in seen_codes:
                seen_codes.add(code)
                validated_data.append(item)

        return validated_data

    def _save_parquet(self, data: List[Dict], local=True) -> bool:
        # try:
        #     with open("dados.json", 'w', encoding='utf-8') as f:
        #         json.dump(data, f, ensure_ascii=False, indent=2)
        #     logger.info(f"Dados salvos em: {self.output_file}")
        #     return True
        # except Exception as e:
        #     logger.error(f"Erro ao salvar arquivo JSON: {e}")
        #     return False
        try:

            output = self.output_folder if local else S3_PATH

            df = pd.DataFrame(data)

            df.to_parquet(
                output,
                engine="pyarrow",
                index=False,
                partition_cols=[self.partition_column]
            )

            self.output_file = output

            logger.info(f"Arquivo salvo em {output}")

            return True

        except Exception as e:

            logger.error(f"Erro salvando parquet: {e}")
            return False

    def run(self):

        logger.info("Iniciando scraping IBOV")

        raw_data = self._scrape()

        if not raw_data:
            logger.error("Nenhum dado coletado")
            return False

        validated_data = self._validate_data(raw_data)

        if not self._save_parquet(validated_data, local=True):
            return False

        print("\n==============================")
        print("RESUMO")
        print("==============================")
        print(f"Registros coletados: {len(validated_data)}")
        print("==============================")

        return True


def main():

    scraper = IBOVScraper()

    success = scraper.run()

    if success:
        logger.info("Scraper concluído com sucesso!")
        exit(0)
    else:
        logger.error("Scraper falhou!")
        exit(1)


if __name__ == "__main__":
    main()