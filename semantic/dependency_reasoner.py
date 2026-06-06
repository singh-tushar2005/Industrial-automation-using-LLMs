"""Industrial dependency reasoning over semantic graph topology.

This module performs higher-order graph reasoning on existing SemanticGraph
structures. It does not modify graph topology, extract relationships, or
perform AST traversal. It only analyzes the connected industrial dependency
network to derive transitive influences, safety chains, critical paths, and
subsystem impact.

The reasoner treats the graph as a behavioral propagation model:
- edges encode how industrial state flows
- paths encode indirect influence
- cycles represent feedback or mutual dependency
"""

from collections import deque

try:
    from semantic.semantic_graph import SemanticGraph, SemanticGraphEdge
except ModuleNotFoundError:
    from semantic_graph import SemanticGraph, SemanticGraphEdge


# ------------------------------------------------------------------
# Influence semantics
# ------------------------------------------------------------------

POSITIVE_RELATIONS = {"enables", "triggers", "activates"}
NEGATIVE_RELATIONS = {"disables"}
SEQUENTIAL_RELATIONS = {"sequences"}

SAFETY_KEYWORDS = {"Safety", "Guard", "Door", "EStop", "Emergency", "Interlock", "Fault"}
TIMER_KEYWORDS = {"TON", "TOF", "TP", "Timer"}


# ------------------------------------------------------------------
# DependencyChain
# ------------------------------------------------------------------

class DependencyChain:
    """Represent one transitive influence path through the semantic graph.

    A chain is a sequence of directed edges from a source node to a target
    node, carrying an inferred industrial influence type and propagation
    depth.
    """

    def __init__(self, source, target, path_edges, depth):
        self.source = source
        self.target = target
        self.path_edges = list(path_edges)
        self.depth = depth
        self.influence_type = self._infer_influence()
        self.summary = self._build_summary()

    def _infer_influence(self):
        """Derive the industrial influence type from edge relations."""

        relations = {edge.relation for edge in self.path_edges}

        if relations & NEGATIVE_RELATIONS:
            return "negative / protective"

        if relations & POSITIVE_RELATIONS and not (relations - POSITIVE_RELATIONS - SEQUENTIAL_RELATIONS):
            return "positive / permissive"

        if relations & SEQUENTIAL_RELATIONS and not (relations - SEQUENTIAL_RELATIONS):
            return "sequential"

        if "depends_on" in relations and len(relations) == 1:
            return "conditional"

        return "complex / mixed"

    def _build_summary(self):
        """Build a human-readable description of this chain."""

        if not self.path_edges:
            return f"{self.source} directly relates to {self.target}"

        parts = [self.source]
        for edge in self.path_edges:
            parts.append(f"{edge.relation} {edge.target}")

        return " → ".join(parts)

    def to_dict(self):
        """Return a serializable dictionary representation."""

        return {
            "source": self.source,
            "target": self.target,
            "depth": self.depth,
            "influence_type": self.influence_type,
            "path_edges": [edge.to_dict() for edge in self.path_edges],
            "summary": self.summary,
        }

    def __repr__(self):
        return (
            f"DependencyChain({self.source!r} → {self.target!r}, "
            f"depth={self.depth}, influence={self.influence_type!r})"
        )


# ------------------------------------------------------------------
# DependencyReasoner
# ------------------------------------------------------------------

class DependencyReasoner:
    """Perform industrial dependency reasoning over a SemanticGraph.

    The reasoner is a read-only analysis layer. It consumes a populated
    SemanticGraph and derives transitive influences, safety chains,
    critical paths, and subsystem impact reports.
    """

    MAX_DEPTH = 10

    def __init__(self, graph):
        if not isinstance(graph, SemanticGraph):
            raise TypeError("Expected SemanticGraph instance")
        self.graph = graph

    # ------------------------------------------------------------------
    # Core traversal primitives
    # ------------------------------------------------------------------

    def find_downstream_dependencies(self, node_id, max_depth=None):
        """Return DependencyChains from node_id to all reachable targets.

        This answers: "What systems are affected by this node?"
        """

        max_depth = max_depth or self.MAX_DEPTH
        chains = []

        for target in self.graph.neighbors(node_id):
            for edge in self.graph.outgoing_edges(node_id):
                if edge.target == target:
                    chains.append(DependencyChain(node_id, target, [edge], 1))

        self._dfs_downstream(node_id, [], chains, set(), max_depth)
        return chains

    def _dfs_downstream(self, current, path_edges, chains, visited, max_depth):
        """Depth-first expansion of downstream paths."""

        if len(path_edges) >= max_depth:
            return

        if current in visited:
            return

        visited.add(current)

        for edge in self.graph.outgoing_edges(current):
            next_node = edge.target
            new_path = path_edges + [edge]

            if len(new_path) >= 2:
                chains.append(DependencyChain(
                    new_path[0].source,
                    next_node,
                    new_path,
                    len(new_path),
                ))

            self._dfs_downstream(next_node, new_path, chains, visited.copy(), max_depth)

    def find_upstream_dependencies(self, node_id, max_depth=None):
        """Return DependencyChains from all reachable sources to node_id.

        This answers: "What influences this node?"
        """

        max_depth = max_depth or self.MAX_DEPTH
        chains = []

        for source in self.graph.predecessors(node_id):
            for edge in self.graph.incoming_edges(node_id):
                if edge.source == source:
                    chains.append(DependencyChain(source, node_id, [edge], 1))

        self._dfs_upstream(node_id, [], chains, set(), max_depth)
        return chains

    def _dfs_upstream(self, current, path_edges, chains, visited, max_depth):
        """Depth-first expansion of upstream paths (reverse direction)."""

        if len(path_edges) >= max_depth:
            return

        if current in visited:
            return

        visited.add(current)

        for edge in self.graph.incoming_edges(current):
            prev_node = edge.source
            new_path = [edge] + path_edges

            if len(new_path) >= 2:
                chains.append(DependencyChain(
                    prev_node,
                    new_path[-1].target,
                    new_path,
                    len(new_path),
                ))

            self._dfs_upstream(prev_node, new_path, chains, visited.copy(), max_depth)

    def find_transitive_dependencies(self, node_id):
        """Return the set of all node identifiers reachable from node_id."""

        reachable = set()
        queue = deque([node_id])
        visited = {node_id}

        while queue:
            current = queue.popleft()
            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    reachable.add(neighbor)
                    queue.append(neighbor)

        return reachable

    def trace_dependency_paths(self, source, target, max_depth=None):
        """Return all DependencyChains from source to target."""

        max_depth = max_depth or self.MAX_DEPTH
        chains = []
        self._dfs_trace(source, target, [], chains, set(), max_depth)
        return chains

    def _dfs_trace(self, current, target, path_edges, chains, visited, max_depth):
        if current == target and path_edges:
            chains.append(DependencyChain(
                path_edges[0].source,
                target,
                list(path_edges),
                len(path_edges),
            ))
            return

        if len(path_edges) >= max_depth:
            return

        if current in visited:
            return

        visited.add(current)

        for edge in self.graph.outgoing_edges(current):
            self._dfs_trace(
                edge.target,
                target,
                path_edges + [edge],
                chains,
                visited.copy(),
                max_depth,
            )

    # ------------------------------------------------------------------
    # Industrial reasoning
    # ------------------------------------------------------------------

    def analyze_safety_chains(self):
        """Find all dependency chains involving safety-critical edges or nodes.

        A safety chain contains at least one `enables` or `disables` edge,
        or involves a node whose name contains safety-related terms.
        """

        all_chains = []
        for node in self.graph.nodes():
            chains = self.find_downstream_dependencies(node.node_id)
            for chain in chains:
                if self._is_safety_chain(chain):
                    all_chains.append(chain)

        return self._deduplicate_chains(all_chains)

    def analyze_timer_chains(self):
        """Find all dependency chains originating from timer nodes."""

        all_chains = []
        for node in self.graph.nodes():
            if any(kw in node.node_id for kw in TIMER_KEYWORDS):
                chains = self.find_downstream_dependencies(node.node_id)
                all_chains.extend(chains)

        return self._deduplicate_chains(all_chains)

    def analyze_critical_paths(self):
        """Identify the longest and most connected dependency chains.

        Critical paths are those with the greatest depth or those that
        connect multiple subsystems.
        """

        all_chains = []
        for node in self.graph.nodes():
            all_chains.extend(self.find_downstream_dependencies(node.node_id))

        if not all_chains:
            return []

        max_depth = max(chain.depth for chain in all_chains)
        return [chain for chain in all_chains if chain.depth == max_depth]

    def analyze_control_paths(self):
        """Identify critical control paths from upstream nodes to actuators.

        For every actuator node, find all upstream dependency chains.
        Keep chains containing at least one control-critical edge relation
        (enables, triggers, activates, controls). Ignore chains that pass
        through contains, uses, or schedules edges.
        """

        CRITICAL_RELATIONS = {"enables", "triggers", "activates", "controls"}
        IGNORED_RELATIONS = {"contains", "uses", "schedules"}

        results = []
        for node in self.graph.nodes():
            if node.node_kind != "actuator":
                continue

            actuator_id = node.node_id
            all_chains = self.find_upstream_dependencies(actuator_id)

            filtered = []
            for chain in all_chains:
                relations = {edge.relation for edge in chain.path_edges}
                if relations & IGNORED_RELATIONS:
                    continue
                if relations & CRITICAL_RELATIONS:
                    filtered.append(chain)

            filtered = self._deduplicate_chains(filtered)

            results.append({
                "actuator": actuator_id,
                "chain_count": len(filtered),
                "critical_paths": [
                    {
                        "source": chain.source,
                        "target": chain.target,
                        "depth": chain.depth,
                        "summary": chain.summary,
                    }
                    for chain in filtered
                ],
            })

        return results

    def analyze_safety_impact(self):
        """Assess safety impact by tracing downstream reach from safety nodes.

        For every node whose name matches safety-related keywords, find all
        downstream dependencies and classify impact severity based on the
        kinds of industrial systems that can be reached.
        """

        results = []
        for node in self.graph.nodes():
            if not any(kw in node.node_id for kw in SAFETY_KEYWORDS):
                continue

            node_id = node.node_id
            downstream_chains = self.find_downstream_dependencies(node_id)
            reachable = self.find_transitive_dependencies(node_id)

            affected_nodes = sorted(reachable)

            affected_actuators = []
            has_timer_or_counter = False
            for target_id in reachable:
                target_node = self.graph.get_node(target_id)
                if target_node:
                    if target_node.node_kind == "actuator":
                        affected_actuators.append(target_id)
                    if target_node.node_kind in {"timer", "counter"}:
                        has_timer_or_counter = True

            max_depth = 0
            if downstream_chains:
                max_depth = max(chain.depth for chain in downstream_chains)

            if affected_actuators:
                severity = "HIGH"
            elif has_timer_or_counter:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            results.append({
                "safety_node": node_id,
                "affected_nodes": affected_nodes,
                "affected_actuators": sorted(affected_actuators),
                "depth": max_depth,
                "severity": severity,
            })

        return results

    def analyze_failure_propagation(self):
        """Trace downstream propagation from failure-source nodes.

        Failure sources are nodes whose identifiers start with Fault,
        Alarm, Warning, Trip, or Error. For each source, downstream
        dependency chains are collected to determine propagation depth
        and impacted systems.
        """

        FAILURE_PREFIXES = {"Fault", "Alarm", "Warning", "Trip", "Error"}

        results = []
        for node in self.graph.nodes():
            if not any(node.node_id.startswith(prefix) for prefix in FAILURE_PREFIXES):
                continue

            node_id = node.node_id
            chains = self.find_downstream_dependencies(node_id)
            reachable = self.find_transitive_dependencies(node_id)

            impacted_nodes = sorted(reachable)

            impacted_actuators = []
            for target_id in reachable:
                target_node = self.graph.get_node(target_id)
                if target_node and target_node.node_kind == "actuator":
                    impacted_actuators.append(target_id)

            max_depth = 0
            if chains:
                max_depth = max(chain.depth for chain in chains)

            deduped = self._deduplicate_chains(chains)
            chain_summaries = [chain.summary for chain in deduped]

            results.append({
                "source": node_id,
                "propagation_depth": max_depth,
                "impacted_nodes": impacted_nodes,
                "impacted_actuators": sorted(impacted_actuators),
                "chain_summaries": chain_summaries,
            })

        return results

    def analyze_state_machines(self):
        """Build state transition maps and detect structural properties.

        Uses existing ``transitions_to`` relationships to identify states,
        transitions, reachability, terminal states, and cycles.
        """

        transitions = []
        state_set = set()
        for edge in self.graph.edges():
            if edge.relation == "transitions_to":
                transitions.append((edge.source, edge.target))
                state_set.add(edge.source)
                state_set.add(edge.target)

        for node in self.graph.nodes():
            if node.node_kind == "state":
                state_set.add(node.node_id)

        states = sorted(state_set)
        if not states:
            return {
                "states": [],
                "transitions": [],
                "reachable_states": [],
                "unreachable_states": [],
                "terminal_states": [],
                "cycles": [],
            }

        adjacency = {s: [] for s in states}
        for src, tgt in transitions:
            if src in adjacency:
                adjacency[src].append(tgt)

        # Reachable states: all states reachable from any state that has
        # outgoing transitions_to edges.
        start_states = [s for s in states if adjacency.get(s)]
        reachable_states = set()
        for start in start_states:
            visited = set()
            stack = [start]
            while stack:
                current = stack.pop()
                if current not in visited:
                    visited.add(current)
                    for neighbor in adjacency.get(current, []):
                        if neighbor not in visited:
                            stack.append(neighbor)
            reachable_states.update(visited)
        reachable_states = sorted(reachable_states)

        unreachable_states = sorted([s for s in states if s not in reachable_states])

        terminal_states = sorted([s for s in states if not adjacency.get(s)])

        cycles = []
        found = set()

        for start in states:
            path = []
            in_path = set()

            def dfs(node):
                path.append(node)
                in_path.add(node)
                for neighbor in adjacency.get(node, []):
                    if neighbor in in_path:
                        idx = path.index(neighbor)
                        cycle = path[idx:]
                        if cycle:
                            min_val = min(cycle)
                            min_idx = cycle.index(min_val)
                            normalized = tuple(cycle[min_idx:] + cycle[:min_idx])
                            if normalized not in found:
                                found.add(normalized)
                                cycles.append(list(normalized))
                    elif neighbor not in in_path:
                        dfs(neighbor)
                path.pop()
                in_path.remove(node)

            dfs(start)

        return {
            "states": states,
            "transitions": transitions,
            "reachable_states": reachable_states,
            "unreachable_states": unreachable_states,
            "terminal_states": terminal_states,
            "cycles": cycles,
        }

    def analyze_subsystem_influence(self):
        """Map each node to the set of downstream node kinds it influences."""

        influence_map = {}
        for node in self.graph.nodes():
            downstream = self.find_transitive_dependencies(node.node_id)
            influenced_kinds = set()
            for target_id in downstream:
                target_node = self.graph.get_node(target_id)
                if target_node:
                    influenced_kinds.add(target_node.node_kind)
            influence_map[node.node_id] = {
                "node_kind": node.node_kind,
                "direct_targets": sorted(self.graph.neighbors(node.node_id)),
                "transitive_targets": sorted(downstream),
                "influenced_kinds": sorted(influenced_kinds),
            }
        return influence_map

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_reasoning_report(self):
        """Return a comprehensive structured reasoning report."""

        safety_chains = self.analyze_safety_chains()
        timer_chains = self.analyze_timer_chains()
        critical_paths = self.analyze_critical_paths()
        control_paths = self.analyze_control_paths()
        safety_impact = self.analyze_safety_impact()
        failure_propagation = self.analyze_failure_propagation()
        state_machines = self.analyze_state_machines()
        subsystem_influence = self.analyze_subsystem_influence()

        # Collect high-impact nodes (nodes with many transitive connections)
        high_impact = [
            node_id
            for node_id, data in subsystem_influence.items()
            if len(data["transitive_targets"]) >= 3
        ]

        return {
            "safety_chains": [chain.to_dict() for chain in safety_chains],
            "safety_chain_count": len(safety_chains),
            "timer_chains": [chain.to_dict() for chain in timer_chains],
            "timer_chain_count": len(timer_chains),
            "critical_paths": [chain.to_dict() for chain in critical_paths],
            "critical_path_count": len(critical_paths),
            "control_paths": control_paths,
            "control_path_count": sum(p["chain_count"] for p in control_paths),
            "safety_impact": safety_impact,
            "safety_impact_count": len(safety_impact),
            "failure_propagation": failure_propagation,
            "failure_propagation_count": len(failure_propagation),
            "state_machines": state_machines,
            "state_machine_count": len(state_machines.get("states", [])),
            "subsystem_influence": subsystem_influence,
            "high_impact_nodes": sorted(high_impact),
            "graph_node_count": self.graph.node_count(),
            "graph_edge_count": self.graph.edge_count(),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_safety_chain(self, chain):
        """Return True if the chain involves safety-critical semantics."""

        if chain.path_edges:
            relations = {edge.relation for edge in chain.path_edges}
            if relations & {"enables", "disables"}:
                return True

        if SAFETY_KEYWORDS & {chain.source, chain.target}:
            return True

        return any(
            any(kw in edge.source or kw in edge.target for kw in SAFETY_KEYWORDS)
            for edge in chain.path_edges
        )

    def _deduplicate_chains(self, chains):
        """Remove duplicate chains by their source-target-edge signature."""

        seen = set()
        unique = []
        for chain in chains:
            key = (chain.source, chain.target, tuple(
                (edge.source, edge.relation, edge.target) for edge in chain.path_edges
            ))
            if key not in seen:
                seen.add(key)
                unique.append(chain)
        return unique
