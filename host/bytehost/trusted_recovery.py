"""Generic isolated execution with an independently pinned capability policy.

This separate trusted credential context never executes project build commands.
The native BF planner owns the archive/signature sequence inside the image.
"""
from pathlib import Path
from .errors import require
from .process import isolated
from .storage import digest, load, no_links


def trusted_isolated(spec):
    policy_path = Path(spec["policy_file"]).absolute()
    no_links(policy_path)
    require(digest(policy_path) == spec["policy_sha256"], "TRUST_ANCHOR", "Trusted policy differs from independent pin")
    policy = load(policy_path)
    require(policy["image"] == spec["image"], "TRUST_ANCHOR", "Execution image was not independently approved")
    forbidden = [Path(path).absolute() for path in spec["forbidden_sources"]]
    require(forbidden, "ISOLATION", "Explicit inaccessible input roots required")
    for mount in spec["mounts"]:
        source = Path(mount["source"]).absolute()
        no_links(source)
        require(not any(source.is_relative_to(path) or path.is_relative_to(source) for path in forbidden),
                "ISOLATION", "Forbidden original/reference path would be exposed")
        rule = policy["mounts"].get(mount["target"])
        require(rule is not None and mount["readonly"] == rule["readonly"], "ISOLATION", "Mount differs from approved capability policy")
        if not mount["readonly"]:
            source.mkdir(parents=True, exist_ok=True)
            require(not any(source.iterdir()), "EXISTS", "Trusted output mount must start empty")
        require(not policy_path.is_relative_to(source), "ISOLATION", "Policy must stay outside the execution context")
    return isolated(spec)
