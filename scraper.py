from playwright.sync_api import sync_playwright
import csv

def run():
    with sync_playwright() as playw:
        # 1. Iniciando o navegador (headless=False por padrão - Ver bot atuando)
        run_mode_input = ""
        run_mode = True
        while run_mode_input != "headless" and run_mode_input != "headful" and run_mode_input != "1" and run_mode_input != "2":
            print("Selecione o modo: headless (1) / headful (2)")
            run_mode_input = input()
            if run_mode_input == "headless" or run_mode_input == "1":
                run_mode = True
            elif run_mode_input == "headful" or run_mode_input == "2":
                run_mode = False
            else:
                print("❌ Valor inserido inválido\n")

        print("🚀 Iniciando o browser...")
        browser = playw.firefox.launch(headless=run_mode, slow_mo=500) # slow_mo pra ver melhor
        page = browser.new_page()

        # 2. Acessar a home (goto)
        print("🔗 Acessando comparajogos.com.br...")
        page.goto("https://www.comparajogos.com.br/")

        # 3. Clicar em "Populares da Semana"
        print("👆 Clicando em 'Populares da Semana'...")
        
        # Localizar o Título "Populares da Semana"
        print("🔍 Procurando seção 'Populares da Semana'...")
        titulo_secao = page.get_by_text("Populares da Semana", exact=False).first
        titulo_secao.wait_for()

        # Pegar o item mais acima na hierarquia
        secao_populares = titulo_secao.locator("xpath=../..")

        # 4. Localizar os cards de jogos DENTRO dessa seção (ou próximos a ela)
        # Usar "a" que tem '/item/' no href, pra garantir ser item da lista
        print("🃏 Coletando links dos jogos no carrossel...")

        # Pegar todos os cards da "page" com o link de '/item'
        cards = secao_populares.locator("a[href^='/item/']").all()

        # Por enquanto pegar só os primeiros 5 para o teste
        # Depois vou melhorar para pegar todos do carrossel
        
        game_links = []
        for card in cards:
            # Precisamos do link (href) de cada item
            # É o que vem depois do endereço principal do site
            href = card.get_attribute("href")
            
            # Evitar duplicatas ou links vazios
            if href and href not in game_links:
                full_link = f"https://www.comparajogos.com.br{href}"
                if full_link not in game_links:
                    game_links.append(full_link)
                    print(f"   🎮 Encontrado: {full_link}")

        print(f"✅ Total de jogos identificados: {len(game_links)}")
        

        # ENTRANDO NOS DETALHES DE CADA ITEM
        dados_finais = []

        for link in game_links:
            print(f"\nAcessando: {link}")
            try:
                page.goto(link, timeout=60000)
                page.wait_for_load_state("domcontentloaded")
                
                # Pegar título da aba do navegador.
                # Estava dando errado com o título do item, então fui pelo da página
                full_title = page.title() 
                # Remover sufixos (ex: "Wingspan | Compara Jogos")
                # Aí remove o " | Compara Jogos", fica só o Wingspan
                # Separando pelo '|', pegue apenas o item do índice 0
                # Que é o nome do jogo
                title = full_title.split("|")[0].strip()
                if title.lower().startswith("jogo "):
                    title = title[5:] # Remove os primeiros 5 caracteres ("Jogo ")
                print(f"🏷️  Jogo Identificado: {title}")

                # Lista de Ofertas
                # Try Except pra conferir se tem ofertas
                try:
                    # Espera 10s, se aparecer algum link com "'/api/redirect'", tudo certo
                    # Essa parte é para o link de redirecionamento para a página da oferta
                    page.wait_for_selector("a[href^='/api/redirect']", timeout=10000)
                except:
                    print("   ⚠️ Time out esperando ofertas. Pode ser que não tenha estoque.")

                # Pega todas as ofertas presentes (com link pra "/api/redirect")
                offer_links = page.locator("a[href^='/api/redirect']").all()
                
                if not offer_links:
                    print("   ⚠️ Nenhuma oferta encontrada (lista vazia).")
                
                for offer in offer_links:
                    # Seletor subindo 3 níveis
                    # O link está num espaço diferente do preço, não no mesmo nível
                    # Aí subi até o elemento que tem dentro dele tanto o nome/link quanto o preço
                    offer_row = offer.locator("xpath=../../..") 
                    
                    # Ler o texto da linha inteira
                    raw_text = offer_row.inner_text()
                    # Limpeza de quebras de linha
                    clean_text = " | ".join([line.strip()
                                             for line in raw_text.split('\n')
                                             if line.strip()])
                    
                    offer_url = f"https://www.comparajogos.com.br{offer.get_attribute('href')}"
                    
                    # Regex setado para 2 casas decimais
                    # Evita pegar o número de parcelas (ex: 9x) que vem logo depois do preço
                    import re
                    # Procura R$ Depois tira o que tiver EXATAMENTE 2 digitos depois da ','
                    # Por exemplo em "499,90 9x" ele tira o "9x"
                    preco_match = re.search(r"R\$\s?[\d\.]+,[\d]{2}", clean_text)
                    preco_encontrado = preco_match.group(0) if preco_match else "Esgotado/Sem Preço"

                    print(f"   🛒 Oferta: {clean_text[:50]}... | 💲 Preço: {preco_encontrado}")

                    dados_finais.append({
                        "jogo": title,
                        "loja": clean_text.split("|")[0].strip(), # Tenta pegar só o nome da loja
                        "preco": preco_encontrado,
                        "link": offer_url
                    })
                
                # Pausa entre requisições
                # time.sleep(2)

            except Exception as e:
                print(f"   ❌ Erro neste link: {e}")

        # Persistência (Salvar CSV) ---
        if dados_finais:
            print(f"\n💾 Salvando {len(dados_finais)} ofertas em 'games_data.csv'...")
            # '-sig' pra avisar o Excel que o arquivo tem acentos
            with open("games_data.csv", "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["jogo", "loja", "preco", "link"])
                writer.writeheader()
                writer.writerows(dados_finais)
            print("✅ Arquivo 'games_data.csv' gerado com sucesso!")
        
        browser.close()

if __name__ == "__main__":
    run()