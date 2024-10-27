import geopandas as gpd
from abc import ABC, abstractmethod
from collections import defaultdict
from neo4j import GraphDatabase
from typing import List, Dict
from utils.exceptions import GraphBuilderError
from utils.config import Neo4jConfig
from utils.logger import logger


class IGraphBuilder(ABC):
    @abstractmethod
    def build_graph(self, elements: gpd.GeoDataFrame) -> None:
        pass


class GraphBuilder(IGraphBuilder):
    """
    A class for building and managing graph structures in Neo4j.

    This class implements the IGraphBuilder interface and provides methods
    for creating nodes and relationships in Neo4j.
    """

    def __init__(self, config: Neo4jConfig):
        """
        Initialize the GraphBuilder with Neo4j configuration.

        Args:
            config (Neo4jConfig): Configuration object for Neo4j connection.
        """
        self.driver = GraphDatabase.driver(
            config.uri, auth=(config.user, config.password)
        )

    def cleanup(self):
        """
        Remove all nodes and relationships from Neo4j.

        Raises:
            GraphBuilderError: If there's an error removing the graph.
        """
        try:
            with self.driver.session(database="neo4j") as session:
                session.run(
                    """
                    MATCH (n:Element)
                    DETACH DELETE n
                    """
                )
            logger.info("All nodes and relationships removed from Neo4j.")
        except Exception as e:
            raise GraphBuilderError(f"Error removing graph: {e}") from e

    def build_graph(self, elements: List[Dict], graph_name: str) -> None:
        """
        Build a graph in Neo4j from a list of element dictionaries.

        Args:
            elements (List[Dict]): List of dictionaries containing the elements
            to build the graph.
            graph_name (str): The name to assign to the created graph.

        Raises:
            GraphBuilderError: If there's an error building the graph.
        """
        try:
            with self.driver.session() as session:
                self._create_nodes(session, elements)
                self._create_relationships(session, elements)
            logger.info("Graph built successfully")
        except Exception as e:
            raise GraphBuilderError(f"Error building graph: {e}") from e

    def _create_nodes(self, session, elements: List[Dict]) -> None:
        """
        Create nodes in Neo4j from the elements in the list.

        Args:
            session: Neo4j session object.
            elements (List[Dict]): List of dictionaries containing the elements
            to create nodes from.
        """
        nodes = [{"id": element["id"], "name": element["name"]} for element in elements]
        session.run(
            """
            UNWIND $nodes AS node
            MERGE (e:Element {id: node.id})
            SET e.name = node.name
        """,
            nodes=nodes,
        )

    def _create_relationships(self, session, elements: List[Dict]) -> None:
        """
        Create relationships between nodes in Neo4j based on the elements' geometry.

        Args:
            session: Neo4j session object.
            elements (List[Dict]): List of dictionaries containing the elements
            to create relationships from.
        """
        connection_map = self._build_connection_map(elements)
        relationships = self._generate_relationships(connection_map)

        session.run(
            """
            UNWIND $relationships AS rel
            MATCH (a:Element {id: rel.from}), (b:Element {id: rel.to})
            MERGE (a)-[:CONNECTS_TO]->(b)
            MERGE (b)-[:CONNECTS_TO]->(a)
        """,
            relationships=relationships,
        )

    def _build_connection_map(self, elements: List[Dict]) -> Dict:
        """
        Build a map of connections between elements based on their geometry.

        Args:
            elements (List[Dict]): List of dictionaries containing the elements
            to build connections from.

        Returns:
            Dict: A dictionary mapping coordinate tuples to sets of element IDs.
        """
        connection_map = defaultdict(set)
        for element in elements:
            start_point = (
                element["geometry"][0]["lat"],
                element["geometry"][0]["lon"],
            )
            end_point = (
                element["geometry"][-1]["lat"],
                element["geometry"][-1]["lon"],
            )
            connection_map[start_point].add(element["id"])
            connection_map[end_point].add(element["id"])
        return connection_map

    def _generate_relationships(self, connection_map: Dict) -> List[Dict]:
        """
        Generate relationships between elements based on the connection map.

        Args:
            connection_map (Dict): A dictionary mapping coordinate tuples
            to sets of element IDs.

        Returns:
            List[Dict]: A list of dictionaries representing relationships
            between elements.
        """
        relationships = []
        for connected_ids in connection_map.values():
            if len(connected_ids) > 1:
                connected_list = list(connected_ids)
                relationships.extend(
                    [
                        {"from": connected_list[i], "to": connected_list[j]}
                        for i in range(len(connected_list))
                        for j in range(i + 1, len(connected_list))
                    ]
                )
        return relationships
