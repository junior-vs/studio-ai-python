# src/domain/generation_record.py
from typing import Dict, Any, Optional
from src.domain.route import Route

class GenerationRecord:
    """
    Estrutura de dados para armazenar a melhor solução de uma única geração
    e os seus metadados.
    """
    def __init__(self, generation: int, best_route: Route, 
                 max_fitness: float, mean_fitness: float, 
                 total_cost: float, vehicle_usage: Optional[Dict[str, int]] = None):
        """
        Args:
            generation: O número da geração.
            best_route: Cópia da melhor rota (Route) da geração.
            max_fitness: O fitness máximo (melhor) da geração.
            mean_fitness: O fitness médio da população da geração.
            total_cost: O custo total da melhor rota (inverso do fitness).
            vehicle_usage: Uso da frota (se VRP).
        """
        self.generation = generation
        self.best_route = best_route
        self.max_fitness = max_fitness
        self.mean_fitness = mean_fitness
        self.total_cost = total_cost
        self.vehicle_usage = vehicle_usage if vehicle_usage is not None else {}
        
    def get_route_data(self) -> Dict[str, Any]:
        """Retorna uma estrutura de dados aninhada da Route para serialização."""
        # Isto é uma simplificação. A serialização completa ocorreria aqui.
        
        # Como a rota já pode ter sido "splitada" em rotas menores no VRP,
        # retornamos a estrutura completa.
        optimized_routes = getattr(self.best_route, 'routes', [self.best_route])
        
        route_segments_data = []
        for segment in optimized_routes:
            # Simplificação: apenas a sequência de pontos
            sequence = [f"P({int(dp.x)}, {int(dp.y)})" for dp in segment.delivery_points]
            route_segments_data.append({
                "vehicle": getattr(segment, 'vehicle_type', 'N/A'),
                "sequence": sequence
            })
            
        return {
            "routes_segments": route_segments_data,
            "overall_sequence": [f"P({int(dp.x)}, {int(dp.y)})" for dp in self.best_route.delivery_points]
        }

    def to_llm_json_data(self) -> Dict[str, Any]:
        """Prepara o dicionário de dados para serialização JSON."""
        return {
            "generation": self.generation,
            "max_fitness": f"{self.max_fitness:.6f}",
            "mean_fitness": f"{self.mean_fitness:.6f}",
            "total_cost": f"{self.total_cost:.2f}",
            "vehicle_usage": self.vehicle_usage,
            "route_details": self.get_route_data()
        }