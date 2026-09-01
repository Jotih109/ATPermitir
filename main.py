import os
import sys
import time
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright, TimeoutError as PlaywrightTimeoutError

# Garante suporte a caracteres UTF-8 no console Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Carrega variáveis do .env
load_dotenv()

PEP_LOGIN = os.getenv("PEP_LOGIN")
PEP_SENHA = os.getenv("PEP_SENHA")
HEADLESS = os.getenv("HEADLESS", "false").strip().lower() in ("1", "true", "sim")
TIMEOUT_PADRAO = int(os.getenv("PEP_TIMEOUT", "45000"))  # 45 segundos

if not PEP_LOGIN or not PEP_SENHA:
    print("❌ ERRO: Defina 'PEP_LOGIN' e 'PEP_SENHA' no arquivo .env antes de executar.")
    sys.exit(1)


def aguardar_e_clicar(locator, nome: str, timeout: int = TIMEOUT_PADRAO, delay_antes: float = 0.5, delay_depois: float = 1.0) -> None:
    """Aguarda o elemento ficar pronto, visível e habilitado antes de clicar com segurança."""
    print(f"⏳ Aguardando '{nome}'...", flush=True)
    try:
        locator.wait_for(state="visible", timeout=timeout)
        if delay_antes > 0:
            time.sleep(delay_antes)
        locator.scroll_into_view_if_needed(timeout=3000)
        locator.click(timeout=timeout)
        print(f"✅ Clicado em: '{nome}'", flush=True)
        if delay_depois > 0:
            time.sleep(delay_depois)
    except PlaywrightTimeoutError:
        print(f"❌ Timeout ao aguardar '{nome}' (limite: {timeout/1000:.0f}s)", flush=True)
        raise
    except Exception as e:
        print(f"❌ Erro ao clicar em '{nome}': {e}", flush=True)
        raise


def run(playwright: Playwright) -> None:
    print("🚀 Iniciando navegador...", flush=True)
    browser = playwright.chromium.launch(
        headless=HEADLESS,
        slow_mo=50
    )
    context = browser.new_context(viewport={"width": 1366, "height": 768})
    page = context.new_page()
    page.set_default_timeout(TIMEOUT_PADRAO)

    try:
        # ====== 1. ETAPA DE LOGIN ======
        print("\n--- [1/5] Realizando Login no Medicina Direta PEP ---", flush=True)
        page.goto("https://pep.medicinadireta.com.br/", wait_until="domcontentloaded")
        time.sleep(2.0)

        login_frame = page.frame_locator('iframe[name="content"]')
        
        # Preenchimento seguro de usuário com disparo de eventos
        print("⏳ Preenchendo Usuário...", flush=True)
        login_input = login_frame.locator("#id_sc_field_txt_login, input[name='txt_login']")
        login_input.click()
        login_input.type(PEP_LOGIN, delay=30)
        login_input.evaluate("el => { el.dispatchEvent(new Event('change', {bubbles:true})); el.dispatchEvent(new Event('blur', {bubbles:true})); }")
        time.sleep(1.5)

        # Preenchimento seguro de senha com disparo de eventos
        print("⏳ Preenchendo Senha...", flush=True)
        pass_input = login_frame.locator("#id_sc_field_txt_senha, input[name='txt_senha']")
        pass_input.click()
        pass_input.type(PEP_SENHA, delay=30)
        pass_input.evaluate("el => { el.dispatchEvent(new Event('change', {bubbles:true})); el.dispatchEvent(new Event('blur', {bubbles:true})); }")
        time.sleep(1.0)

        print("⏳ Autenticando...", flush=True)
        btn_autenticar = login_frame.locator("#sc_autenticar_bot, button:has-text('Continuar'), a#sc_autenticar_bot")
        btn_autenticar.click()

        # Aguarda o menu principal carregar
        print("⏳ Aguardando carregamento do sistema pós-login...", flush=True)
        page.wait_for_selector("#item_20", timeout=TIMEOUT_PADRAO)
        print("✅ Login efetuado com sucesso!", flush=True)
        time.sleep(1.5)

        # ====== 2. NAVEGAÇÃO NO MENU ======
        print("\n--- [2/5] Navegando nos Menus ---", flush=True)
        
        # Hover em Área Clínica
        print("⏳ Abrindo menu 'Área Clínica'...", flush=True)
        page.locator("#item_20").hover()
        time.sleep(1.0)

        # Hover em Configuração
        print("⏳ Abrindo submenu 'Configuração'...", flush=True)
        page.locator("#item_242").hover()
        time.sleep(1.0)

        # Clique em Configurar Impressão PDF
        item_pdf = page.locator("a:has-text('Configurar Impressão PDF'), a:has-text('Configurar Impressao PDF'), #item_285").first
        aguardar_e_clicar(item_pdf, "Item 'Configurar Impressão PDF'", delay_depois=3.5)
        page.mouse.move(10, 10)  # Afasta o mouse para fechar menus suspensos

        # ====== 3. LOCALIZANDO FRAME DE CONFIGURAÇÃO ======
        print("\n--- [3/5] Acessando Modelo de Impressão ---", flush=True)
        config_frame = None
        for f in page.frames:
            if "menu_inicial_item_285_iframe" in f.name:
                config_frame = f
                break

        if not config_frame:
            for f in page.frames:
                if "grid_receitas_config_pdf" in f.url:
                    config_frame = f
                    break

        if not config_frame:
            raise Exception("Não foi possível localizar o frame de configuração de impressão.")

        # Clicar no botão Editar (linha 11 ou primeiro disponível)
        btn_editar = config_frame.locator("#id_sc_field_cmp_editar_11, a[id*='cmp_editar_11']").first
        if btn_editar.count() == 0:
            btn_editar = config_frame.locator("a[id*='cmp_editar']").first

        aguardar_e_clicar(btn_editar, "Botão Editar Modelo", delay_depois=3.0)

        # ====== 4. PERMISSÃO DE USUÁRIOS ======
        print("\n--- [4/5] Aplicando Permissão de Usuários ---", flush=True)
        btn_perm = config_frame.locator("a#btn_permissao, a[onclick*='modal_permissao'], :text('Permissão de Usuários')").first
        aguardar_e_clicar(btn_perm, "Botão 'Permissão de Usuários'", delay_depois=1.5)

        modal_perm = config_frame.locator("#modal-permissao")
        modal_perm.wait_for(state="visible", timeout=10000)

        btn_move_perm = modal_perm.locator("button.moveall, button:has-text('>>')").first
        if btn_move_perm.count() > 0 and btn_move_perm.is_visible():
            btn_move_perm.click()
            time.sleep(1.0)

        btn_salvar_perm = modal_perm.locator("button:has-text('Salvar'), button[onclick*='salvar_permissao']").first
        aguardar_e_clicar(btn_salvar_perm, "Salvar Permissões", delay_depois=1.0)
        modal_perm.wait_for(state="hidden", timeout=10000)
        time.sleep(1.0)
        print("✅ Permissão de Usuários aplicada e salva!", flush=True)

        # ====== 5. PADRÃO DE IMPRESSÃO ======
        print("\n--- [5/5] Aplicando Padrão de Impressão ---", flush=True)
        btn_padrao = config_frame.locator("a#btn_padrao, a[onclick*='modal_padrao'], :text('Padrão de Impressão')").first
        aguardar_e_clicar(btn_padrao, "Botão 'Padrão de Impressão'", delay_depois=1.5)

        modal_padrao = config_frame.locator("#modal-padrao")
        modal_padrao.wait_for(state="visible", timeout=10000)

        # Aba Receita
        aba_receita = modal_padrao.locator("button:has-text('Receita'), a:has-text('Receita')").first
        if aba_receita.count() > 0:
            aba_receita.click()
            time.sleep(0.8)
            btn_move_rec = modal_padrao.locator("button.moveall, button:has-text('>>')").first
            if btn_move_rec.count() > 0 and btn_move_rec.is_visible():
                btn_move_rec.click()
                time.sleep(0.8)

        # Aba Exame
        aba_exame = modal_padrao.locator("button:has-text('Exame'), a:has-text('Exame')").first
        if aba_exame.count() > 0:
            aba_exame.click()
            time.sleep(0.8)
            btn_move_exame = modal_padrao.locator("button.moveall, button:has-text('>>')").first
            if btn_move_exame.count() > 0 and btn_move_exame.is_visible():
                btn_move_exame.click()
                time.sleep(0.8)

        btn_salvar_padrao = modal_padrao.locator("button:has-text('Salvar'), button[onclick*='salvar_padrao']").first
        aguardar_e_clicar(btn_salvar_padrao, "Salvar Padrão de Impressão", delay_depois=1.0)
        modal_padrao.wait_for(state="hidden", timeout=10000)
        time.sleep(1.5)
        print("✅ Padrão de Impressão aplicado e salvo!", flush=True)

        # ====== SALVAR MODELO GERAL ======
        print("\n💾 Salvando configurações gerais do modelo...", flush=True)
        btn_salvar_geral = config_frame.locator("a#btn_salvar[onclick*='salvar()'], a.scButton_default:has-text('Salvar')").first
        aguardar_e_clicar(btn_salvar_geral, "Salvar Modelo Geral", delay_depois=3.0)

        print("\n=======================================================")
        print("🎉 CONFIGURAÇÃO DE PERMITIR PDF CONCLUÍDA COM SUCESSO!")
        print("=======================================================\n")
        time.sleep(2.0)

    except Exception as e:
        print(f"\n❌ Falha durante a execução: {e}", flush=True)
        raise

    finally:
        print("🔒 Encerrando navegador...", flush=True)
        try:
            context.close()
            browser.close()
        except Exception:
            pass


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
