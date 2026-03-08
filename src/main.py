from src.utils.data_loader import cargar_desde_json
from src.repository.repository import registrar_proyecto, buscar_candidatos
from src.services.geminis.metrics import mostrar_metricas_finales 

if __name__ == "__main__":
    print("🚀 Sistema Student Match - AI Service Running")
    
    # Cargar datos iniciales
    proyectos_prueba = cargar_desde_json() 
    
    for proy in proyectos_prueba:
        print(f"\n🔍 Proyecto: {proy['titulo']}")
        
        # Lógica de Opción 3: Guardamos vector en DB de Python/IA
        v_proy = registrar_proyecto(proy['id'], proy['titulo'], proy['descripcion'])
        
        # Búsqueda matemática
        candidatos = buscar_candidatos(v_proy)
        
        print(f"🏆 Top 3 Candidatos:")
        for c in candidatos[:3]:
            print(f"  - {c[0]} ({c[2]:.2%}) | Skills: {c[1]}")

    mostrar_metricas_finales()