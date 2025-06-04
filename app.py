import os
import time
import random
import streamlit as st
import chess
import chess.svg
from typing import Optional
from streamlit.delta_generator import DeltaGenerator

try:
    import openai
except ImportError:
    openai = None

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = "802NW0xA2QMipBYGxGlFfgr14BwgzRS17fmR64Td367x0NGFQovsJQQJ99BFACYeBjFXJ3w3AAAAACOG4GDB"
AZURE_OPENAI_ENDPOINT = "https://chess-codex-foundry.cognitiveservices.azure.com/"
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"

AGENT1_DEPLOYMENT = "gpt-4.1"
AGENT2_DEPLOYMENT = "grok-3"

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
            messages=[
                {"role": "system", "content": "You are a creative and strong chess-playing AI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,  # Add more randomness
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


def display_board(board: chess.Board, container: Optional[DeltaGenerator] = None):
    svg = chess.svg.board(board=board)
    if container:
        container.markdown(svg, unsafe_allow_html=True)
    else:
        st.markdown(svg, unsafe_allow_html=True)


def build_prompt(board: chess.Board) -> str:
    """Build a prompt including move history in SAN format safely with variation."""
    temp_board = chess.Board()
    history_san = []
    for move in board.move_stack:
        san_move = temp_board.san(move)
        history_san.append(san_move)
        temp_board.push(move)

    player = "White" if board.turn == chess.WHITE else "Black"
    random_hint = random.randint(1, 100000)  # Add variation
    prompt = (
        f"You are a chess AI playing as {player}.\n"
        f"Current board FEN: {board.fen()}\n"
        f"Move history: {' '.join(history_san) if history_san else 'None'}\n"
        f"Session hint: {random_hint}\n"
        "Your move in SAN or UCI format only. Do not explain—just return the move."
    )
    return prompt


def main():
    st.title("AI Chess Battle")
    st.write("Two AI agents play chess using GPT models.")

    board = chess.Board()
    num_moves = st.number_input("Number of moves", min_value=1, max_value=100, value=10)
    start_button = st.button("Start Game")

    if start_button:
        board_placeholder = st.empty()
        log_placeholder = st.empty()
        logs = []

        for move_number in range(num_moves):
            agent = "Agent 1" if board.turn == chess.WHITE else "Agent 2"
            deployment = AGENT1_DEPLOYMENT if board.turn == chess.WHITE else AGENT2_DEPLOYMENT

            prompt = build_prompt(board)
            move_str = request_gpt(deployment, prompt)
            logs.append(f"**{agent} move {move_number+1}:** {move_str}")
            log_placeholder.markdown("\n".join(logs))

            # Try SAN, then fallback to UCI if valid length
            try:
                try:
                    move = board.parse_san(move_str)
                except ValueError:
                    if len(move_str) in [4, 5]:
                        move = chess.Move.from_uci(move_str)
                        if move not in board.legal_moves:
                            raise ValueError(f"Illegal UCI move: {move_str}")
                    else:
                        raise ValueError(f"Invalid UCI format: {move_str}")

                if move in board.legal_moves:
                    board.push(move)
                else:
                    raise ValueError("Move not legal")

            except Exception as e:
                logs.append(f"Invalid move from {agent}: {e}")
                log_placeholder.markdown("\n".join(logs))
                break

            display_board(board, board_placeholder)

            if board.is_game_over():
                logs.append(f"Game over! Result: {board.result()}")
                log_placeholder.markdown("\n".join(logs))
                break

            time.sleep(1)

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
