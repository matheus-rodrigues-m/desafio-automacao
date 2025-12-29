from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as playw:
        # 1. Iniciando o navegador (headless=False para ver a tela e ver se vai funcionar bem)
        print("🚀 Iniciando o browser...")
        browser = playw.firefox.launch(headless=False, slow_mo=500) # slow_mo pra ver melhor
        page = browser.new_page()

        # 2. Acessar a home (goto)
        print("🔗 Acessando comparajogos.com.br...")
        page.goto("https://www.comparajogos.com.br/")

        # 3. Clicar em "Populares da Semana"
        print("👆 Clicando em 'Populares da Semana'...")
        
        # Localizar o Título "Populares da Semana" para garantir que carregou
        print("🔍 Procurando seção 'Populares da Semana'...")
        titulo_secao = page.get_by_text("Populares da Semana", exact=False).first
        titulo_secao.wait_for()

        # 4. Localizar os cards de jogos DENTRO dessa seção (ou próximos a ela)
        # Usar "a" que tem '/item/' no href, pra garantir ser item da lista
        print("🃏 Coletando links dos jogos no carrossel...")

        # Pegar todos os cards da "page" com o link de '/item'
        cards = page.locator("a[href^='/item/']").all()

        # Por enquanto pegar só os primeiros 5 para o teste
        # Depois vou melhorar para pegar todos do carrossel
        
        game_links = []
        count = 0
        for card in cards:
            if count >= 5: break # Teste de 5 cards
            
            # Precisamos do link (href) de cada item
            href = card.get_attribute("href")
            
            # Evitar duplicatas ou links vazios
            if href and href not in game_links:
                full_link = f"https://www.comparajogos.com.br{href}"
                game_links.append(full_link)
                print(f"🎮 Encontrado: {full_link}")
                count += 1

        print(f"✅ Total de jogos identificados: {len(game_links)}")
        
        # Salva em um arquivo temporário para validar se deu certo
        with open("temp_links.txt", "w") as f:
            for link in game_links:
                f.write(link + "\n")

        browser.close()

if __name__ == "__main__":
    run()