"""Qualification script to build, install, and test the Genre Pack wheel in an isolated venv."""

import os
import subprocess
import sys
import tempfile
import json
from pathlib import Path

import hashlib
import zipfile

def run_cmd(cmd: list[str], cwd: str | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    environ = os.environ.copy()
    environ["PYTHONUTF8"] = "1"
    if env:
        environ.update(env)
    res = subprocess.run(cmd, cwd=cwd, env=environ, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"STDOUT:\n{res.stdout}")
        print(f"STDERR:\n{res.stderr}")
        raise RuntimeError(f"Command failed with exit code {res.returncode}")
    return res

def main():
    root = Path(__file__).parent.parent.resolve()
    print("1. Building wheel...")
    build_dir = tempfile.mkdtemp(prefix="auteur_build_")
    run_cmd([sys.executable, "-m", "pip", "install", "hatchling", "build"], cwd=str(root))
    run_cmd([sys.executable, "-m", "build", "--wheel", "--outdir", build_dir], cwd=str(root))

    wheels = list(Path(build_dir).glob("*.whl"))
    if not wheels:
        raise RuntimeError("No wheel found after build.")
    wheel_path = wheels[0]
    
    wheel_bytes = wheel_path.read_bytes()
    wheel_sha256 = hashlib.sha256(wheel_bytes).hexdigest()
    with zipfile.ZipFile(wheel_path) as z:
        wheel_file_count = len(z.namelist())
        namelist = z.namelist()
        yaml_present = any("erotic_fiction/0.1.0.yaml" in f or "0.1.0.yaml" in f for f in namelist)

    print(f"Built wheel: {wheel_path.name}")
    print(f"  Package Version: 0.37.0")
    print(f"  Wheel SHA-256  : {wheel_sha256}")
    print(f"  Wheel File Count: {wheel_file_count}")
    print(f"  Pack YAML Present: {yaml_present}")

    print("2. Creating isolated venv...")
    venv_dir = tempfile.mkdtemp(prefix="auteur_venv_")
    run_cmd([sys.executable, "-m", "venv", venv_dir])

    if sys.platform == "win32":
        py_bin = str(Path(venv_dir) / "Scripts" / "python.exe")
        auteur_bin = str(Path(venv_dir) / "Scripts" / "auteur.exe")
    else:
        py_bin = str(Path(venv_dir) / "bin" / "python")
        auteur_bin = str(Path(venv_dir) / "bin" / "auteur")

    print("3. Installing wheel into venv...")
    run_cmd([py_bin, "-m", "pip", "install", str(wheel_path)])

    print("4. Executing qualification matrix from unrelated directory...")
    work_dir = tempfile.mkdtemp(prefix="auteur_work_")

    # Qualification Check 1: Import from site-packages & version check
    res_import = run_cmd([py_bin, "-c", "import auteur; print(auteur.__file__); print(auteur.__version__)"], cwd=work_dir)
    stdout_lines = res_import.stdout.strip().splitlines()
    installed_file = stdout_lines[0]
    installed_ver = stdout_lines[1]
    assert "site-packages" in installed_file or "dist-packages" in installed_file or "venv" in installed_file.lower()
    assert installed_ver == "0.37.0"
    print(f"  [PASS] Import from site-packages (version {installed_ver})")

    # Qualification Check 2: Pack list & inspect
    res_list = run_cmd([auteur_bin, "genre", "pack", "list", "--json"], cwd=work_dir)
    packs = json.loads(res_list.stdout)
    assert any(p["pack_id"] == "erotic_fiction" for p in packs)
    print("  [PASS] Pack list")

    res_inspect = run_cmd([auteur_bin, "genre", "pack", "inspect", "erotic_fiction", "--json"], cwd=work_dir)
    pack_info = json.loads(res_inspect.stdout)
    assert pack_info["pack_id"] == "erotic_fiction"
    print("  [PASS] Pack inspect")

    # Qualification Check 3: Opinionated recommendation & persistent disk storage
    res_rec = run_cmd([auteur_bin, "genre", "recommend", "--premise", "A story of desire and identity transformation", "--json"], cwd=work_dir)
    rec_data = json.loads(res_rec.stdout)
    rec_id = rec_data["recommendation_id"]
    assert rec_data["recommended_pack_id"] == "erotic_fiction"
    print("  [PASS] Opinionated recommendation")

    # Qualification Check 4: Recommendation durability across CLI invocations / process restarts
    res_inspect_rec = run_cmd([auteur_bin, "genre", "recommendation", "inspect", rec_id, "--json"], cwd=work_dir)
    inspected_rec = json.loads(res_inspect_rec.stdout)
    assert inspected_rec["recommendation_id"] == rec_id
    assert inspected_rec["recommended_profile_id"] == rec_data["recommended_profile_id"]
    print("  [PASS] Recommendation artifact durability across process restart")

    # Qualification Check 5: Zero pre-acceptance mutation
    ident_yaml = """title: Test Story
core_answer: Desire and identity transformation
target_experience:
  primary: desire
  progression: rising
  avoid: []
story_type:
  medium: novel
  mode: intimate
  genre: romance
  subgenres: []
  target_audience: adult
central_engine:
  want: Surrender to desire.
  resistance: Fear of exposure.
  conflict: Desire vs self-image.
  stakes: Isolation vs transformation.
  change: Replaces pride with intimacy.
"""
    ident_path = Path(work_dir) / "story_identity.yaml"
    ident_path.write_text(ident_yaml, encoding="utf-8")

    res_rec2 = run_cmd([auteur_bin, "genre", "recommend", "--project", work_dir, "--json"], cwd=work_dir)
    rec_data2 = json.loads(res_rec2.stdout)
    rec_id2 = rec_data2["recommendation_id"]

    assert ident_path.read_text(encoding="utf-8") == ident_yaml
    print("  [PASS] Zero pre-acceptance mutation")

    # Qualification Check 6: Explicit acceptance updates Identity
    run_cmd([auteur_bin, "genre", "recommendation", "accept", rec_id2, "--project", work_dir, "--confirm"], cwd=work_dir)
    updated_yaml = ident_path.read_text(encoding="utf-8")
    assert "genre_profile:" in updated_yaml
    assert "primary_pack_id: erotic_fiction" in updated_yaml
    print("  [PASS] Explicit acceptance updates Identity")

    # Qualification Check 7: Restart persistence
    res_show = run_cmd([auteur_bin, "genre", "profile", "show", "--project", work_dir, "--json"], cwd=work_dir)
    prof_data = json.loads(res_show.stdout)
    assert prof_data["primary_pack_id"] == "erotic_fiction"
    print("  [PASS] Restart persistence")

    # Qualification Check 8: Pack version & hash persist
    assert "primary_pack_version" in prof_data
    assert "pack_content_hash" in prof_data
    print("  [PASS] Pack version and hash persist")

    # Qualification Check 9: Genre validation
    res_val = run_cmd([auteur_bin, "genre", "validate", "--project", work_dir, "--json"], cwd=work_dir)
    diags = json.loads(res_val.stdout)
    assert isinstance(diags, list)
    print("  [PASS] Genre validation")

    # Qualification Check 10: Genre diagnosis
    res_diag = run_cmd([auteur_bin, "genre", "diagnose", "--project", work_dir, "--json"], cwd=work_dir)
    diags2 = json.loads(res_diag.stdout)
    assert isinstance(diags2, list)
    print("  [PASS] Genre diagnosis")

    print("\nALL INSTALLED WHEEL QUALIFICATION MATRIX CHECKS PASSED!")

if __name__ == "__main__":
    main()
