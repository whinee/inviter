import shlex
import sys
from subprocess import call


def format():
    run("isort .")

def run(s: str):
    call(shlex.split(s))

def push(v: list[int]=None):
    msg = inquirer.text(message="Enter commit message", default="")
    format()
    run("git add .")
    if msg != "":
        msg = f"{msg},"
    if v:
        run(f"git commit -am '{msg}https://hyk.fr.to/changelog#v{'-'.join([str(i) for i in v])}'")
    else:
        run(f"git commit -am '{msg or 'push'}'")
    run("git push")

def main():
    match inquirer.list_input(
        message="What action do you want to take",
        choices=[
            ["Copy constants to project folder", "cp"],
            ["Format code", "f"],
            ["Generate documentation", "docs"],
            ["Push to github", "gh"],
        ]
    ):
        case "f":
            format()
        case "docs":
            from scripts import md_vars
            md_vars.main()
            run("mkdocs build")
            if inquirer.confirm(
                "Do you want to push this to github?",
                default=False
            ):
                push()
        case "gh":
            push()
        case _:
            pass

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        if sys.argv[1] == "req":
            run(f'pip install --require-virtualenv pyyaml')
            import yaml
            with open('dev.yml', 'r') as f:
                y = yaml.safe_load(f)
            ls = []
            for c in y["env"]["dev"]["req"]:
                ls.append(f'-r {y["requirements"][c]}')
            run(f'pip install --require-virtualenv {" ".join(ls)}')
        elif sys.argv[1] == "docs":
            from scripts import md_vars

            md_vars.main()
    else:
        import inquirer

        main()