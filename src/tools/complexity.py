"""Complexity estimator tool for technical feasibility assessment."""


def complexity_estimator(components: str, has_hardware: str, needs_realtime: str) -> str:
    """Estimate the technical complexity of building a startup's product.
    Use this tool to assess how difficult the technical implementation will be.

    :param components: Comma-separated list of major technical components, e.g. 'computer vision, IoT sensors, ML pipeline, web dashboard'
    :param has_hardware: Whether the product involves custom hardware. Must be 'yes' or 'no'
    :param needs_realtime: Whether the product requires real-time processing. Must be 'yes' or 'no'
    :returns: A complexity assessment with score and breakdown
    """
    component_list = [c.strip() for c in components.split(",")]
    num_components = len(component_list)
    hw = has_hardware.lower().strip() == "yes"
    rt = needs_realtime.lower().strip() == "yes"

    # Base complexity from component count
    if num_components <= 2:
        base = 3
        base_label = "Low"
    elif num_components <= 4:
        base = 5
        base_label = "Medium"
    elif num_components <= 6:
        base = 7
        base_label = "High"
    else:
        base = 9
        base_label = "Very High"

    # Modifiers
    modifiers = []
    score = base
    if hw:
        score += 2
        modifiers.append("+2 for hardware (supply chain, manufacturing, iteration cycles)")
    if rt:
        score += 1
        modifiers.append("+1 for real-time requirements (latency, infrastructure)")

    score = min(score, 10)

    # Estimate team size
    if score <= 3:
        team = "2-3 engineers"
    elif score <= 6:
        team = "4-8 engineers"
    elif score <= 8:
        team = "8-15 engineers"
    else:
        team = "15+ engineers"

    return (
        f"Complexity Score: {score}/10 ({base_label} base)\n"
        f"Components ({num_components}): {', '.join(component_list)}\n"
        f"Hardware: {'Yes' if hw else 'No'}\n"
        f"Real-time: {'Yes' if rt else 'No'}\n"
        f"Modifiers: {'; '.join(modifiers) if modifiers else 'None'}\n"
        f"Estimated team size: {team}"
    )
