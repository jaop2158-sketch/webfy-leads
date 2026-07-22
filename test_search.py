from duckduckgo_search import DDGS
import time

def test_fetch(nicho, cidade):
    queries = [
        f"{nicho} em {cidade}",
        f"consultorio {nicho} {cidade}",
        f"clinica {nicho} {cidade}",
        f"atendimento {nicho} {cidade}"
    ]
    all_results = []
    
    for q in queries:
        try:
            with DDGS() as ddg:
                res = list(ddg.text(q, max_results=10))
                print(f"Query '{q}': {len(res)} resultados")
                all_results.extend(res)
        except Exception as e:
            print(f"Erro em '{q}': {e}")
        time.sleep(1)
        
    return all_results

results = test_fetch("psicologo", "curitiba")
print(f"Total acumulado: {len(results)}")
for r in results[:5]:
    print("-", r.get("title"), "|", r.get("href"))
