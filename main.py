"""Ponto de entrada do Gerenciador de Senhas."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Gerenciador de Senhas")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="abre a interface clássica no terminal",
    )
    args = parser.parse_args()

    if args.cli:
        from cli import main as iniciar_cli

        iniciar_cli()
    else:
        from gui import main as iniciar_gui

        iniciar_gui()


if __name__ == "__main__":
    main()
