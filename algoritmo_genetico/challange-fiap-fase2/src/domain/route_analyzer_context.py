# src/domain/route_analyzer_context.py
import json
from typing import List, Dict, Any
from src.domain.route import Route
from src.domain.delivery_point import DeliveryPoint
from src.domain.product import Product
from src.domain.vehicle import VehicleType

class RouteAnalyzerContext:
    """
    Classe para agregar e serializar a informação da melhor rota e do contexto
    do VRP para análise por um Large Language Model (LLM).
    
    A LLM receberá uma representação clara da solução VRP encontrada pelo AG.
    """

    def __init__(self, best_route: Route, depot: DeliveryPoint, fleet: List[VehicleType]):
        """
        Inicializa o contexto de análise.
        
        Args:
            best_route: A melhor rota (indivíduo) encontrado pelo AG.
            depot: O ponto de depósito.
            fleet: A frota de veículos disponível.
        """
        self.best_route = best_route
        self.depot = depot
        self.fleet = fleet
        self.final_fitness = getattr(best_route, 'fitness', 0.0)
        self.vehicle_usage = getattr(best_route, 'vehicle_usage', {})


    def _serialize_product(self, product: Product) -> Dict[str, Any]:
        """Serializa o objeto Product para Dict."""
        if product is None:
            return {}
            
        return {
            "id": getattr(product, 'id', None),
            "name": getattr(product, 'name', 'N/A'),
            "weight_g": f"{getattr(product, 'weight', 0.0):.1f}g",
            "volume_cm3": f"{getattr(product, 'volume', 0.0):.0f}cm³",
            "priority": getattr(product, 'priority', 0),
            "is_fragile": getattr(product, 'is_fragile', False)
        }

    def _serialize_delivery_point(self, dp: DeliveryPoint, is_depot: bool = False) -> Dict[str, Any]:
        """Serializa o DeliveryPoint e o seu produto aninhado."""
        return {
            "type": "Depot" if is_depot else "Delivery",
            "x": int(dp.x),
            "y": int(dp.y),
            "product_details": self._serialize_product(dp.product)
        }
        
    def _serialize_vehicle_type(self, vt: VehicleType) -> Dict[str, Any]:
        """Serializa o objeto VehicleType para Dict."""
        return {
            "type": vt.name,
            "max_count": vt.count,
            "max_weight_g": f"{vt.max_weight:.0f}g",
            "max_volume_cm3": f"{vt.max_volume:.0f}cm³",
            "autonomy_km": f"{vt.autonomy:.1f}km",
            "cost_per_km": f"{vt.cost_per_km:.2f}"
        }

    def to_llm_json(self, generation: int) -> str:
        """
        Gera uma string JSON completa e formatada com a solução e o contexto
        para ser enviada ao LLM.
        """
        
        # 1. Serializar Contexto Global
        context_data = {
            "generation": generation,
            "final_fitness_score": f"{self.final_fitness:.6f}",
            "depot": self._serialize_delivery_point(self.depot, is_depot=True),
            "available_fleet": [self._serialize_vehicle_type(v) for v in self.fleet],
            "vehicle_usage_count": self.vehicle_usage
        }

        # 2. Serializar a Rota Otimizada (Segmentos VRP)
        routes_data = []
        optimized_routes = getattr(self.best_route, 'routes', [self.best_route])
        
        for route_segment in optimized_routes:
            # Obtém a distância e o veículo de cada segmento
            distance = route_segment.distancia_roundtrip(self.depot) if route_segment.delivery_points else 0.0
            vehicle_name = getattr(route_segment, 'vehicle_type', 'N/A')
            
            # Mapeia a sequência de pontos
            points_sequence = [
                self._serialize_delivery_point(dp) for dp in route_segment.delivery_points
            ]
            
            # Adicionar segmento VRP
            routes_data.append({
                "vehicle_assigned": vehicle_name,
                "total_distance_km": f"{distance:.2f}km",
                "delivery_sequence": points_sequence
            })
            
        # 3. Estrutura Final
        final_data = {
            "context_summary": context_data,
            "optimized_routes": routes_data
        }
        
        # Usa indent=2 para formatar o JSON, tornando-o fácil de ler para a LLM
        return json.dumps(final_data, indent=2)