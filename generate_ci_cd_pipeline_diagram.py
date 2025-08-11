import yaml
from graphviz import Digraph
from pathlib import Path

# Path to the GitHub Actions YAML
yaml_path = Path(".github/workflows/main.yaml")

# Load the GitHub Actions YAML
with open(yaml_path, "r") as file:
    workflow = yaml.safe_load(file)

# Main graph: arrange CI and CD clusters side-by-side
dot = Digraph(comment=workflow.get("name", "GitHub Actions Workflow"))
dot.attr(rankdir="LR", fontsize="10")  # LR = side-by-side clusters

jobs = workflow.get("jobs", {})

for job_name, job_data in jobs.items():
    cluster_label = "CI" if "ci" in job_name.lower() else "CD"

    with dot.subgraph(name=f"cluster_{job_name}") as c:
        # Force each cluster to be vertical
        c.attr(rankdir="TB")
        c.attr(
            label=f"{cluster_label}: {job_name}",
            style="filled",
            color="#D6EAF8",
            fontsize="12",
        )
        c.node(
            job_name,
            f"{job_name}\n({job_data.get('runs-on', '')})",
            shape="box",
            style="filled",
            fillcolor="#AED6F1",
        )

        steps = job_data.get("steps", [])
        prev_step_node = None

        for idx, step in enumerate(steps, 1):
            step_name = step.get("name", f"Step {idx}")
            step_node_id = f"{job_name}_{idx}"
            c.node(
                step_node_id,
                step_name,
                shape="rect",
                style="rounded,filled",
                fillcolor="#F9E79F",
            )

            if prev_step_node:
                c.edge(prev_step_node, step_node_id)
            else:
                c.edge(job_name, step_node_id)

            prev_step_node = step_node_id

# Footer note
dot.attr(
    label="Designed by Dmitry Zhuravlev",
    fontsize="14",
    labelloc="b",
    fontcolor="black",
    style="dashed",
)

# Save diagram
output_file = "ci_cd_pipeline_diagram_aws_beanstalk"
dot.render(output_file, format="png", cleanup=True)

print(f"Diagram generated: {output_file}.png")
