def render_template(template: str, variables: dict) -> str:
    """Render notification template with placeholders."""
    output = template
    for key, value in variables.items():
        output = output.replace(f"{{{{{key}}}}}", str(value))
    return output
