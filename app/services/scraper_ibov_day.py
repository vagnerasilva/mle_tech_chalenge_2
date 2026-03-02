#!/usr/bin/env python3
"""
Scraper para extrair dados do portfólio diário do IBOV da B3.
Extrai TODAS as linhas da tabela com paginação automática.
"""

import json
import time
from typing import List, Dict, Optional
import logging
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError
from app.utils.data_cleaners import clean_number, clean_percentage, clean_text

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IBOVScraper:
    def __init__(self):
        self.url = "https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br"
        self.output_file = "ibov_day_portfolio.json"
        self.timeout = 30000  # 30 segundos
        self.retry_attempts = 3
        self.retry_delay = 2  # segundos
        
    
    def _wait_for_table(self, page: Page) -> bool:
        """Espera a tabela carregar."""
        try:
            page.wait_for_selector('table.table.table-responsive-sm.table-responsive-md tbody', 
                                 timeout=self.timeout)
            return True
        except PlaywrightTimeoutError:
            logger.error("Timeout aguardando tabela carregar")
            return False
    
    def _extract_table_data(self, page: Page) -> List[Dict]:
        """Extrai dados da tabela atual."""
        data = []
        
        try:
            # Encontra todas as linhas do tbody
            rows = page.query_selector_all('table.table.table-responsive-sm.table-responsive-md tbody tr')
            
            for row in rows:
                cells = row.query_selector_all('td')
                if len(cells) >= 5:  # Verifica se temos todas as colunas esperadas
                    try:
                        item = {
                            "codigo": clean_text(cells[0].text_content()),
                            "acao": clean_text(cells[1].text_content()),
                            "tipo": clean_text(cells[2].text_content()),
                            "qtde_teorica": clean_number(cells[3].text_content()),
                            "part_pct": clean_percentage(cells[4].text_content())
                        }
                        data.append(item)
                    except Exception as e:
                        logger.warning(f"Erro ao processar linha: {e}")
                        continue
            
            logger.info(f"Extraídas {len(data)} linhas da página atual")
            return data
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados da tabela: {e}")
            return []
    
    def _go_to_next_page(self, page: Page) -> bool:
        """Tenta ir para a próxima página."""
        try:
            # Procura pelo botão "next" (próxima página)
            next_button = page.query_selector('li.pagination-next a')
            
            if not next_button:
                logger.info("Botão 'next' não encontrado - fim da paginação")
                return False
            
            # Verifica se o botão está desabilitado
            class_attr = next_button.get_attribute('class') or ''
            parent = next_button.query_selector('..')
            parent_class = parent.get_attribute('class') or '' if parent else ''
            
            if 'disabled' in class_attr or 'disabled' in parent_class:
                logger.info("Botão 'next' desabilitado - fim da paginação")
                return False
            
            # Clica no botão next
            logger.info("Indo para a próxima página...")
            next_button.click()
            
            # Espera um pouco para a página carregar
            time.sleep(2)
            
            # Espera a tabela carregar novamente
            if not self._wait_for_table(page):
                logger.error("Falha ao carregar tabela na próxima página")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao navegar para próxima página: {e}")
            return False
    
    def _scrape_with_retry(self) -> Optional[List[Dict]]:
        """Executa o scraping com mecanismo de retry."""
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Tentativa {attempt + 1} de {self.retry_attempts}")
                
                with sync_playwright() as p:
                    # Inicia browser headless
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    )
                    page = context.new_page()
                    
                    # Navega para a URL
                    logger.info(f"Acessando: {self.url}")
                    page.goto(self.url, timeout=self.timeout)
                    
                    # Espera a tabela carregar
                    if not self._wait_for_table(page):
                        logger.error("Falha ao carregar tabela inicial")
                        browser.close()
                        continue
                    
                    all_data = []
                    page_count = 0
                    
                    # Loop de paginação
                    while True:
                        page_count += 1
                        logger.info(f"Processando página {page_count}")
                        
                        # Extrai dados da página atual
                        page_data = self._extract_table_data(page)
                        all_data.extend(page_data)
                        
                        # Tenta ir para próxima página
                        if not self._go_to_next_page(page):
                            break
                    
                    browser.close()
                    return all_data
                    
            except Exception as e:
                logger.error(f"Erro na tentativa {attempt + 1}: {e}")
                if attempt < self.retry_attempts - 1:
                    logger.info(f"Aguardando {self.retry_delay} segundos antes de tentar novamente...")
                    time.sleep(self.retry_delay)
        
        return None
    
    def _validate_data(self, data: List[Dict]) -> List[Dict]:
        """Valida e remove duplicatas dos dados."""
        if not data:
            return []
        
        # Remove duplicatas baseadas no código
        seen_codes = set()
        validated_data = []
        duplicates = 0
        
        for item in data:
            code = item.get('codigo', '')
            if code and code not in seen_codes:
                seen_codes.add(code)
                validated_data.append(item)
            elif code:
                duplicates += 1
                logger.warning(f"Código duplicado encontrado e removido: {code}")
        
        if duplicates > 0:
            logger.warning(f"Removidas {duplicates} duplicatas")
        
        return validated_data
    
    def _save_json(self, data: List[Dict]) -> bool:
        """Salva dados em arquivo JSON."""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Dados salvos em: {self.output_file}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo JSON: {e}")
            return False
    
    def run(self) -> bool:
        """Executa o scraper completo."""
        logger.info("Iniciando scraper do IBOV Day Portfolio")
        
        # Executa scraping com retry
        raw_data = self._scrape_with_retry()
        
        if raw_data is None:
            logger.error("Falha total no scraping após todas as tentativas")
            return False
        
        # Valida dados
        validated_data = self._validate_data(raw_data)
        
        # Salva JSON
        if not self._save_json(validated_data):
            return False
        
        # Imprime resumo
        print("\n" + "="*50)
        print("RESUMO DA COLETA")
        print("="*50)
        print(f"Total de registros coletados: {len(validated_data)}")
        print(f"Arquivo gerado: {self.output_file}")
        print("\nPrimeiros 5 registros:")
        for i, item in enumerate(validated_data[:5]):
            print(f"{i+1}. {item}")
        if len(validated_data) > 5:
            print("...")
        print("="*50)
        
        return True

def main():
    """Função principal."""
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
