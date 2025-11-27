import os
import networkx as nx
from pyvis.network import Network
from jinja2 import FileSystemLoader, Environment
import pyvis
import random

def generar_grafo(similitudes, detalles):

    # ================================
    # 1. Cargar Template (Fix PyVis)
    # ================================
    template_path = os.path.join(os.path.dirname(pyvis.__file__), "templates")
    loader = FileSystemLoader(template_path)
    env = Environment(loader=loader)

    net = Network(
        height="750px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#333333",
        directed=False
    )

    net.template = env.get_template("template.html")

    # ================================
    # 2. Construir grafo con NetworkX
    # ================================
    G = nx.Graph()

    for s in similitudes:
        G.add_edge(s["providencia_1"], s["providencia_2"], weight=s["similaridad"])

    # ============
    # Clusters
    # ============
    try:
        from networkx.algorithms.community import greedy_modularity_communities
        comunidades = list(greedy_modularity_communities(G))

        cluster_map = {}
        for i, comunidad in enumerate(comunidades):
            for nodo in comunidad:
                cluster_map[nodo] = i
    except:
        cluster_map = {n: 0 for n in G.nodes()}

    # Paleta de clusters pastel
    CLUSTER_COLORS = [
        "#a6cee3", "#b2df8a", "#fb9a99",
        "#fdbf6f", "#cab2d6", "#ffff99"
    ]

    # ================================
    # 3. Colores por tipo de providencia
    # ================================
    TYPE_COLORS = {
        "Auto": "#4e79a7",
        "Tutela": "#59a14f",
        "Constitucionalidad": "#e15759",
        "Otro": "#9c755f"
    }

    # ================================
    # 4. Añadir NODOS
    # ================================
    for nombre, info in detalles.items():

        tipo = info.get("tipo", "Otro")
        tipo_color = TYPE_COLORS.get(tipo, "#9c755f")

        # Mezclar color del tipo con color del cluster
        cluster_id = cluster_map.get(nombre, 0)
        cluster_tint = CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]

        descripcion = f"""
        <div style='font-size:14px; color:#333;'>
            <b>{nombre}</b><br>
            Tipo: {tipo}<br>
            Año: {info.get("anio", "N/A")}<br><br>
            {info.get("texto", "")[:220]}...
            <br><br>
            <a href='/detalle/{nombre}/0' target='_top' style='color:#4e79a7;'>Ver más →</a>
        </div>
        """

        net.add_node(
            nombre,
            label=nombre,
            title=descripcion,
            shape="dot",
            size=25,
            color={
                "background": tipo_color,
                "border": "#333",
                "highlight": {"background": cluster_tint, "border": "#000"}
            }
        )

    # ================================
    # 5. Añadir ARISTAS
    # ================================
    for s in similitudes:
        p1 = s["providencia_1"]
        p2 = s["providencia_2"]
        sim = s["similaridad"]

        net.add_edge(
            p1,
            p2,
            value=sim * 10,
            color="#90a4ae",
            label=f"{sim:.2f}",
            font={"color": "#555", "size": 12},
            smooth=False
        )

    # ================================
    # 6. Opciones de layout + reset
    # ================================
    net.set_options("""
    {
      "interaction": {
        "hover": true,
        "navigationButtons": true
      },
      "manipulation": false,
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -5000,
          "centralGravity": 0.3,
          "springLength": 160,
          "springConstant": 0.002,
          "damping": 0.18
        }
      }
    }
    """)

    # ================================
    # 7. Incrustar botones JS: Reset + Layouts
    # ================================
    CUSTOM_JS = """
    <script>
    function resetView() {
        network.fit({animation: true});
    }

    function layoutCircular() {
        network.setOptions({
            layout: { improvedLayout: true },
            physics: false
        });
        network.once("afterDrawing", function(){
            network.setOptions({
                layout: { randomSeed: 8 },
                physics: false
            });
        });
    }

    function layoutStar() {
        network.setOptions({
            layout: { hierarchical: false },
            physics: { enabled: false }
        });
        network.stabilize();
    }

    function layoutHubSpoke() {
        network.setOptions({
            physics: { enabled: true },
            layout: { improvedLayout: true }
        });
    }
    </script>

    <div style="margin:10px 0;">
        <button onclick="resetView()" 
                style="padding:6px 12px; background:#4e79a7; color:white; border:none; border-radius:6px;">
            🔄 Reset View
        </button>

        <button onclick="layoutCircular()" 
                style="padding:6px 12px; background:#59a14f; color:white; border:none; border-radius:6px;">
            🌀 Circular
        </button>

        <button onclick="layoutStar()" 
                style="padding:6px 12px; background:#e15759; color:white; border:none; border-radius:6px;">
            ⭐ Star
        </button>

        <button onclick="layoutHubSpoke()" 
                style="padding:6px 12px; background:#9c755f; color:white; border:none; border-radius:6px;">
            🔘 Hub & Spoke
        </button>
    </div>
    """

    html_path = "static/grafo.html"
    net.write_html(html_path)

    with open(html_path, "a", encoding="utf-8") as f:
        f.write(CUSTOM_JS)

    return html_path
