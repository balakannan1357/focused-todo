import os
import streamlit as st
import chess
import chess.svg
from typing import Optional

try:
    import openai
except ImportError:
    openai = None

# Helper to configure Azure OpenAI
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-13")

AGENT1_DEPLOYMENT = os.getenv("AGENT1_DEPLOYMENT", "gpt-deployment-1")
AGENT2_DEPLOYMENT = os.getenv("AGENT2_DEPLOYMENT", "gpt-deployment-2")

if openai and AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT:
    openai.api_type = "azure"
    openai.api_key = AZURE_OPENAI_API_KEY
    openai.api_base = AZURE_OPENAI_ENDPOINT
    openai.api_version = AZURE_OPENAI_API_VERSION


def request_gpt(deployment: str, prompt: str) -> str:
    """Call Azure OpenAI deployment and return the text response."""
    if not openai:
        return "openai package not installed."
    try:
        response = openai.ChatCompletion.create(
            engine=deployment,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error from Azure OpenAI: {e}"


def evaluate_board(board: chess.Board) -> int:
    """Simple material evaluation. Positive for white advantage."""
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0,
    }
    value = 0
    for piece_type in piece_values:
        value += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        value -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
    return value


def display_board(board: chess.Board):
    svg = chess.svg.board(board=board)
    st.components.v1.html(svg, height=400)


def main():
    st.title("AI Chess Battle")
    st.write("Two AI agents play chess using GPT models.")

    board = chess.Board()
    num_moves = st.number_input("Number of moves", min_value=1, max_value=100, value=10)
    start_button = st.button("Start Game")

    if start_button:
        for move_number in range(num_moves):
            agent = "Agent 1" if move_number % 2 == 0 else "Agent 2"
            deployment = AGENT1_DEPLOYMENT if move_number % 2 == 0 else AGENT2_DEPLOYMENT
            prompt = f"Current board in FEN: {board.fen()}\nProvide next move in algebraic notation only."
            move_str = request_gpt(deployment, prompt)

            st.write(f"**{agent} move {move_number+1}:** {move_str}")

            try:
                move = board.parse_san(move_str)
                board.push(move)
            except Exception as e:
                st.write(f"Invalid move from {agent}: {e}")
                break

            display_board(board)

            if board.is_game_over():
                st.write("Game over!", board.result())
                break

        score = evaluate_board(board)
        if score > 0:
            st.write("White advantage")
        elif score < 0:
            st.write("Black advantage")
        else:
            st.write("Even position")

        st.write(f"Evaluation score: {score}")


if __name__ == "__main__":
    main()
