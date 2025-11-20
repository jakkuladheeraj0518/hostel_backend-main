from jinja2 import Template

def render_template(template_text: str, context: dict) -> str:
    template = Template(template_text)
    return template.render(**context)
