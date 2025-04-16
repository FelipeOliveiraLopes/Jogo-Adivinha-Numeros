import flet as ft
import random
import os

pontuacoes = []
jogadores = []
indice_jogador = 0

def salvar_pontuacao(nome, pontos):
    with open("pontuacoes_flet.txt", "a") as arquivo:
        arquivo.write(f"{nome}:{pontos}\n")

def carregar_ranking():
    if not os.path.exists("pontuacoes_flet.txt"):
        return []
    with open("pontuacoes_flet.txt", "r") as arquivo:
        pontuacoes = []
        for linha in arquivo:
            nome, pontos = linha.strip().split(":")
            pontuacoes.append((nome, int(pontos)))
        pontuacoes.sort(key=lambda x: x[1], reverse=True)
        return pontuacoes[:10]

def main(page: ft.Page):
    page.title = "Jogo do Número Secreto - Multiplayer"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "auto"

    nome_jogador = ft.TextField(label="Nome do jogador", width=300)
    adicionar_btn = ft.ElevatedButton("Adicionar jogador")
    jogadores_texto = ft.Text("")
    iniciar_btn = ft.ElevatedButton("Iniciar jogo", disabled=True)

    dificuldade = ft.Dropdown(
        label="Escolha a dificuldade",
        options=[
            ft.dropdown.Option("1 - Fácil (1 a 10)"),
            ft.dropdown.Option("2 - Médio (1 a 20)"),
            ft.dropdown.Option("3 - Difícil (1 a 50)")
        ],
        width=300
    )

    chute_input = ft.TextField(label="Digite seu palpite", width=200)
    tentar_btn = ft.ElevatedButton("Tentar", disabled=True)
    mensagem = ft.Text()
    resultado = ft.Text()
    tentativas_restantes = ft.Text()
    ranking_texto = ft.Text()

    estado = {
        "limite": 10,
        "tentativas_max": 5,
        "tentativas": 0,
        "numero_secreto": 0,
        "pontos": 0
    }

    def atualizar_jogadores():
        jogadores_texto.value = "Jogadores: " + ", ".join(jogadores)
        iniciar_btn.disabled = len(jogadores) == 0
        page.update()

    def adicionar_jogador(e):
        nome = nome_jogador.value.strip()
        if nome and nome not in jogadores:
            jogadores.append(nome)
            nome_jogador.value = ""
            atualizar_jogadores()

    def iniciar_jogo(e):
        if not dificuldade.value:
            mensagem.value = "Escolha uma dificuldade!"
            page.update()
            return

        if dificuldade.value.startswith("1"):
            estado["limite"] = 10
            estado["tentativas_max"] = 5
        elif dificuldade.value.startswith("2"):
            estado["limite"] = 20
            estado["tentativas_max"] = 4
        else:
            estado["limite"] = 50
            estado["tentativas_max"] = 3

        proximo_jogador()

    def proximo_jogador():
        global indice_jogador
        if indice_jogador >= len(jogadores):
            mostrar_ranking_final()
            return

        estado["numero_secreto"] = random.randint(1, estado["limite"])
        estado["tentativas"] = 0
        estado["pontos"] = 0
        chute_input.value = ""
        resultado.value = ""
        mensagem.value = f"🎮 {jogadores[indice_jogador]}, tente adivinhar entre 1 e {estado['limite']}"
        tentativas_restantes.value = f"Tentativas restantes: {estado['tentativas_max']}"
        tentar_btn.disabled = False
        page.update()

    def tentar_chute(e):
        if not chute_input.value.isdigit():
            resultado.value = "Digite um número válido!"
            page.update()
            return

        chute = int(chute_input.value)
        estado["tentativas"] += 1

        if chute == estado["numero_secreto"]:
            estado["pontos"] = (estado["limite"] * 2) - (estado["tentativas"] * 3)
            resultado.value = f"🎉 Acertou! Pontuação: {estado['pontos']} pontos"
            tentar_btn.disabled = True
            salvar_pontuacao(jogadores[indice_jogador], estado["pontos"])
            proximo()
        elif chute < estado["numero_secreto"]:
            resultado.value = "❌ Errou! Dica: o número é maior."
        else:
            resultado.value = "❌ Errou! Dica: o número é menor."

        if estado["tentativas"] >= estado["tentativas_max"] and chute != estado["numero_secreto"]:
            resultado.value = f"💥 Fim de jogo! Era {estado['numero_secreto']}."
            tentar_btn.disabled = True
            salvar_pontuacao(jogadores[indice_jogador], 0)
            proximo()

        tentativas_restantes.value = f"Tentativas restantes: {estado['tentativas_max'] - estado['tentativas']}"
        page.update()

    def fechar_dialogo_e_proximo(e):
        page.dialog.open = False
        proximo_jogador()
        page.update()

    def proximo():
        global indice_jogador
        indice_jogador += 1
        page.dialog = ft.AlertDialog(
            title=ft.Text("Próximo jogador"),
            content=ft.Text("Clique para continuar"),
            actions=[ft.TextButton("Continuar", on_click=fechar_dialogo_e_proximo)],
            open=True
        )
        page.update()

    def mostrar_ranking_final():
        ranking = carregar_ranking()
        ranking_texto.value = "🏆 Ranking dos Melhores:\n" + "\n".join([f"{i+1}º - {n}: {p} pts" for i, (n, p) in enumerate(ranking)])
        mensagem.value = "Fim do jogo para todos os jogadores!"
        page.update()

    adicionar_btn.on_click = adicionar_jogador
    iniciar_btn.on_click = iniciar_jogo
    tentar_btn.on_click = tentar_chute

    page.add(
        ft.Column([
            ft.Text("👥 Adicione jogadores"),
            nome_jogador,
            adicionar_btn,
            jogadores_texto,
            dificuldade,
            iniciar_btn,
            mensagem,
            chute_input,
            tentar_btn,
            resultado,
            tentativas_restantes,
            ranking_texto
        ], width=500)
    )

ft.app(target=main, view=ft.WEB_BROWSER)
