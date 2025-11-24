import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).parent.parent / ".github" / "scripts" / "update_pyproject_version.py"


def _load_module():
    # Ensure the repository root is on sys.path so `dq_docker` is importable
    repo_root = Path(__file__).parent.parent.resolve()
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    # If `toml` isn't installed in the test environment, provide a tiny
    # shim that supports `load(path)` and `dumps(data)` for our simple tests.
    if 'toml' not in sys.modules:
        import types
        import re

        fake = types.ModuleType('toml')

        def _load(path):
            text = Path(path).read_text(encoding='utf-8')
            m = re.search(r'version\s*=\s*["\']([^"\']+)["\']', text)
            if m:
                return {'project': {'version': m.group(1)}}
            return {}

        def _dumps(data):
            proj = data.get('project', {})
            parts = []
            if proj:
                parts.append('[project]')
                v = proj.get('version')
                if v is not None:
                    parts.append(f'version = "{v}"')
            return "\n".join(parts) + "\n"

        fake.load = _load
        fake.dumps = _dumps
        sys.modules['toml'] = fake

    spec = importlib.util.spec_from_file_location("update_pyproject_version", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_increment_patch_existing_version(tmp_path):
    mod = _load_module()
    p = tmp_path / "pyproject.toml"
    p.write_text('[project]\nversion = "1.2.3"\n')

    rc = mod.increment_patch(p)
    assert rc == 0

    text = p.read_text(encoding="utf-8")
    assert 'version = "1.2.4"' in text


def test_increment_patch_missing_version(tmp_path):
    mod = _load_module()
    p = tmp_path / "pyproject.toml"
    p.write_text('name = "example"\n')

    rc = mod.increment_patch(p)
    assert rc == 0

    text = p.read_text(encoding="utf-8")
    # The script defaults missing versions to 0.1.1
    assert '0.1.1' in text


def test_set_patch_to_pr_number(tmp_path):
    mod = _load_module()
    p = tmp_path / "pyproject.toml"
    p.write_text('[project]\nversion = "2.5.0"\n')

    rc = mod.set_patch_to(p, 99)
    assert rc == 0

    text = p.read_text(encoding="utf-8")
    assert 'version = "2.5.99"' in text


def test_main_pr_mode_and_increment_mode(tmp_path):
    mod = _load_module()
    p = tmp_path / "pyproject.toml"
    p.write_text('[project]\nversion = "3.4.5"\n')

    # PR mode: argv = [prog, PR_NUMBER, path]
    rc = mod.main(["prog", "123", str(p)])
    assert rc == 0
    assert '3.4.123' in p.read_text(encoding="utf-8")

    # Increment mode: should bump patch by 1
    rc = mod.main(["prog", str(p)])
    assert rc == 0
    # After previous PR step the version was 3.4.123, incrementing yields 3.4.124
    assert '3.4.124' in p.read_text(encoding="utf-8")
