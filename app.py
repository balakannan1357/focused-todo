import os
import streamlit as st
import chess
import chess.svg
from typing import Optional

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

# Helper to get environment tokens
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# If using anthropic client
if anthropic and ANTHROPIC_API_KEY:
    anthropic_client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
else:
    anthropic_client = None


def request_openai(prompt: str) -> str:
    if not openai:
        return 'openai package not installed.'
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error from OpenAI: {e}"


def request_anthropic(prompt: str) -> str:
    if not anthropic_client:
        return 'anthropic client not configured.'
    try:
        response = anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"Error from Anthropic: {e}"


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
            agent = 'OpenAI' if move_number % 2 == 0 else 'Anthropic'
            prompt = f"Current board in FEN: {board.fen()}\nProvide next move in algebraic notation only."
            if agent == 'OpenAI':
                move_str = request_openai(prompt)
            else:
                move_str = request_anthropic(prompt)

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
