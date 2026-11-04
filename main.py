"""PyUron 1.0 — Lanzador de Ejemplos."""
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 PyUron 1.0 — Ejemplos disponibles:")
    print("  1) 2D Coin Collector (Círculos, HUD, Save/Load)")
    print("  2) Salir")
    
    choice = input("Elige un ejemplo (1-2): ")
    if choice == "1":
        script = Path("examples/2d_coin_collector/main.py")
        subprocess.run([sys.executable, str(script)])
    else:
        print("¡Hasta pronto!")

if __name__ == "__main__":
    main()
