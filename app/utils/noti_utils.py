from jinja2 import Template

def render_template(content: str, variables: dict):
    if variables is None:
        variables = {}
    return Template(content).render(**variables)
