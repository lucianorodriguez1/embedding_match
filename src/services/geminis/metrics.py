stats = {"total_tokens": 0, "api_calls": 0}

def registrar_metricas(texto):
    global stats
    tokens = len(texto) // 4  # Estimación rápida
    stats["api_calls"] += 1
    stats["total_tokens"] += tokens
    return tokens

def mostrar_metricas_finales():
    print("\n" + "="*30)
    print("📊 MÉTRICAS DE CONSUMO API")
    print(f"Llamadas totales: {stats['api_calls']}")
    print(f"Tokens estimados: {stats['total_tokens']}")
    print("="*30)