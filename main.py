import os
import time
from Rule_system import RuleEngine
from AI_system import CorrectorGramatical

def transformar():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    archivos = [
        (os.path.join(base_dir, 'output_MSLG2SPA.txt'), os.path.join(base_dir, 'MSLG2SPA.txt')),
        (os.path.join(base_dir, 'output_SPA2MSLG.txt'), os.path.join(base_dir, 'SPA2MSLG.txt'))
    ]
    
    for in_file, out_file in archivos:
        if os.path.exists(in_file):
            with open(in_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            with open(out_file, 'w', encoding='utf-8') as out_f:
                for line in lines[1:]:
                    parts = line.strip('\n').split('\t')
                    if len(parts) >= 2:
                        id_val = parts[0]
                        system_output = parts[-1] 
                        out_f.write(f'"{id_val}"\t"{system_output}"\n')
            print(f"Transformado {in_file} a {out_file}")

def main():
    test_mslg = 'MSLG2SPA_test.txt'
    test_spa = 'SPA2MSLG_test.txt'

    rule_engine = RuleEngine()
    corrector = CorrectorGramatical()

    print("\n--- Processing Test Files ---")
    
    # MSLG2SPA
    if os.path.exists(test_mslg):
        with open(test_mslg, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        with open('output_MSLG2SPA.txt', 'w', encoding='utf-8') as out_f:
            out_f.write("ID\tMSLG_Original\tSPA_AI_Translated\n")
            total_lines = len(lines[1:])
            for i, line in enumerate(lines[1:]):
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    id_val, mslg_text = parts[0], parts[1]
                    
                    print(f"[{i+1}/{total_lines}] MSLG2SPA: Evaluando '{id_val}'")
                    gem_trans = corrector.corregir(mslg_text)
                    
                    out_f.write(f"{id_val}\t{mslg_text}\t{gem_trans}\n")
                    
                    # Evitar rate limits (15 requests/min) en Google AI Studio (Free Tier)
                    if i < total_lines - 1:
                        time.sleep(4.1)               
        print("Saved output_MSLG2SPA.txt")

    # SPA2MSLG
    if os.path.exists(test_spa):
        with open(test_spa, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        with open('output_SPA2MSLG.txt', 'w', encoding='utf-8') as out_f:
            out_f.write("ID\tSPA_Original\tMSLG_Translated_Rules\n")
            for line in lines[1:]:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    id_val, spa_text = parts[0], parts[1]
                    rule_trans = rule_engine.spa_to_mslg(spa_text)
                    out_f.write(f"{id_val}\t{spa_text}\t{rule_trans}\n")
        print("Saved output_SPA2MSLG.txt")

if __name__ == '__main__':
    main()
    transformar()
