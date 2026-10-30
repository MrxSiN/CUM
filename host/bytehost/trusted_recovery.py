"""Generic isolated execution with an independently pinned capability policy.

This separate trusted credential context never executes project build commands.
The native BF planner owns the archive/signature sequence inside the image.
"""
from pathlib import Path
from .errors import require
from .process import isolated
from .storage import digest, load, no_links, verify_tree
from .crypto import verify_signature


def trusted_isolated(spec):
    policy_path = Path(spec["policy_file"]).absolute()
    no_links(policy_path)
    require(("policy_signature" in spec) != ("policy_sha256" in spec),
            "TRUST_ANCHOR", "Exactly one independent policy authentication method is required")
    if "policy_signature" in spec:
        verify_signature(dict(spec["policy_signature"], source=str(policy_path)))
    else:
        require(digest(policy_path) == spec["policy_sha256"], "TRUST_ANCHOR", "Trusted policy differs from independent pin")
    policy = load(policy_path)
    require(policy["format"] == "PINNED-ISOLATED-CAPABILITIES", "FORMAT", "Unknown trusted execution policy")
    require(policy["image"] == spec["image"], "TRUST_ANCHOR", "Execution image was not independently approved")
    require(policy.get("backend", "docker") == spec.get("backend", "docker"), "ISOLATION", "Isolation backend differs from approved policy")
    if spec.get("backend") == "qemu":
        require(policy["vm"] == spec["vm"] and policy["outputs"] == spec.get("outputs", []),
                "ISOLATION", "VM identity or output capabilities differ from approved policy")
    for field in ("argv", "workdir", "environment"):
        require(spec.get(field, {} if field == "environment" else None) == policy[field],
                "ISOLATION", "Execution differs from approved capability policy", field=field)
    targets = [mount["target"] for mount in spec["mounts"]]
    require(len(targets) == len(set(targets)) and set(targets) == set(policy["mounts"]),
            "ISOLATION", "Required capability mounts must appear exactly once")
    forbidden = [Path(path).absolute() for path in spec["forbidden_sources"]]
    require(forbidden, "ISOLATION", "Explicit inaccessible input roots required")
    for mount in spec["mounts"]:
        source = Path(mount["source"]).absolute()
        no_links(source)
        require(not any(source.is_relative_to(path) or path.is_relative_to(source) for path in forbidden),
                "ISOLATION", "Forbidden original/reference path would be exposed")
        rule = policy["mounts"].get(mount["target"])
        require(rule is not None and mount["readonly"] == rule["readonly"], "ISOLATION", "Mount differs from approved capability policy")
        require(source == Path(rule["source"]).absolute(), "ISOLATION", "Mount source was not independently approved")
        require(not mount.get("create"), "ISOLATION", "Trusted mounts must be provisioned before execution")
        if mount["readonly"]:
            if source.is_dir():
                verify_tree(source, rule["inventory"])
            else:
                require(source.is_file() and digest(source) == rule["sha256"],
                        "TRUST_ANCHOR", "Mounted input differs from approved bytes")
        if not mount["readonly"]:
            source.mkdir(parents=True, exist_ok=True)
            require(not any(source.iterdir()), "EXISTS", "Trusted output mount must start empty")
        require(not policy_path.is_relative_to(source), "ISOLATION", "Policy must stay outside the execution context")
    return isolated(spec)
