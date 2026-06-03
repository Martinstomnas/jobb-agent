def print_step(label: str):
    print(f"\n{'─'*60}")
    print(f"  >> {label}")
    print(f"{'─'*60}")


def print_result(label: str, content: str):
    print(f"\n[{label}]\n")
    print(content)
    print()
