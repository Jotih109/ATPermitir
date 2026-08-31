import os
import sys
import time
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright, TimeoutError as PlaywrightTimeoutError

# Carrega as variáveis do arquivo .env
load_dotenv()

PEP_LOGIN = os.getenv("PEP_LOGIN")
PEP_SENHA = os.getenv("PEP_SENHA")
HEADLESS = os.getenv("HEADLESS", "false").strip().lower() in ("1", "true", "sim")
TIMEOUT_PADRAO = int(os.getenv("PEP_TIMEOUT", "30000"))  # 30 segundos por padrão

if not PEP_LOGIN or not PEP_SENHA:
    print("❌ ERRO: Defina 'PEP_LOGIN' e 'PEP_SENHA' no arquivo .env antes de executar.")
    sys.exit(1)


def esperar_e_clicar(locator, nome: str, timeout: int = TIMEOUT_PADRAO) -> None:
    """Aguarda o elemento ficar visível/disponível e realiza o clique."""
    print(f"⏳ Aguardando '{nome}'...")
    try:
        locator.wait_for(state="visible", timeout=timeout)
        locator.click()
        print(f"✅ Clicado em: '{nome}'")
    except PlaywrightTimeoutError:
        print(f"❌ Timeout ao aguardar elemento: '{nome}' (limite de {timeout/1000:.0f}s)")
        raise


def esperar_e_preencher(locator, valor: str, nome: str, timeout: int = TIMEOUT_PADRAO) -> None:
    """Aguarda o campo ficar visível e insere o valor."""
    print(f"⏳ Preenchendo '{nome}'...")
    try:
        locator.wait_for(state="visible", timeout=timeout)
        locator.fill(valor)
        print(f"✅ Preenchido: '{nome}'")
    except PlaywrightTimeoutError:
        print(f"❌ Timeout ao aguardar campo: '{nome}' (limite de {timeout/1000:.0f}s)")
        raise


def run(playwright: Playwright) -> None:
    print("🚀 Iniciando navegador...")
    browser = playwright.chromium.launch(headless=HEADLESS)
    context = browser.new_context(viewport={"width": 1366, "height": 768})
    page = context.new_page()
    page.set_default_timeout(TIMEOUT_PADRAO)

    try:
        print("🌐 Acessando PEP...")
        page.goto("https://pep.medicinadireta.com.br/", wait_until="domcontentloaded")

        # ====== LOGIN ======
        login_frame = page.frame_locator('iframe[name="content"]')
        esperar_e_preencher(login_frame.get_by_role("textbox", name="Usuário"), PEP_LOGIN, "Usuário")
        esperar_e_preencher(login_frame.get_by_role("textbox", name="Senha"), PEP_SENHA, "Senha")
        esperar_e_clicar(login_frame.locator("#sc_autenticar_bot"), "Botão Autenticar / Entrar")

        # ====== NAVEGAÇÃO NO MENU ======
        esperar_e_clicar(page.get_by_role("link", name="Área Clínica"), "Menu Área Clínica")
        esperar_e_clicar(page.get_by_role("link", name="Configuração"), "Submenu Configuração")
        esperar_e_clicar(page.get_by_role("link", name="Configurar Impressão PDF"), "Item Configurar Impressão PDF")

        # ====== CONFIGURAÇÃO DE IMPRESSÃO PDF ======
        config_frame = page.frame_locator('iframe[name="menu_inicial_item_285_iframe"]')

        # 1. Clicar em Editar (linha 11)
        esperar_e_clicar(config_frame.locator("#id_sc_field_cmp_editar_11"), "Editar (Item 11)")

        # 2. Seção Permissão
        esperar_e_clicar(config_frame.locator("#btn_permissao"), "Aba/Botão Permissão")
        esperar_e_clicar(config_frame.get_by_role("button", name=">>"), "Mover Todos (>>)")
        esperar_e_clicar(config_frame.get_by_role("button", name="Salvar"), "Salvar Permissões")

        # 3. Seção Padrão
        esperar_e_clicar(config_frame.locator("#btn_padrao"), "Aba/Botão Padrão")
        esperar_e_clicar(config_frame.get_by_role("button", name=">>"), "Mover Todos Padrão (>>)")

        # 4. Selecionar Exame e mover
        esperar_e_clicar(config_frame.locator("#div_btn_padrao").get_by_text("Exame"), "Opção Exame")
        esperar_e_clicar(config_frame.get_by_role("button", name=">>"), "Mover Exame (>>)")

        # 5. Salvar Configurações
        esperar_e_clicar(config_frame.get_by_role("button", name="Salvar"), "Salvar Padrão")
        esperar_e_clicar(config_frame.locator("a").filter(has_text="Salvar"), "Salvar Geral")

        print("🎉 Processo concluído com sucesso!")
        time.sleep(2)

    except Exception as e:
        print(f"❌ Ocorreu um erro durante a execução: {e}")
        raise

    finally:
        print("🔒 Fechando navegador...")
        context.close()
        browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
