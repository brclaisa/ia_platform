from app.agents.graph import build_graph, get_compiled_graph


class TestGraphStructure:
    def test_graph_builds_without_error(self):
        graph = build_graph()
        assert graph is not None

    def test_graph_compiles_without_error(self):
        compiled = get_compiled_graph()
        assert compiled is not None

    def test_graph_has_all_nodes(self):
        graph = build_graph()
        node_names = set(graph.nodes.keys())
        expected = {"compliance", "router", "rag", "direct", "synthesizer"}
        assert expected.issubset(node_names)
