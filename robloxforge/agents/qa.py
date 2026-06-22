"""QA agent: reviews generated code for bugs/exploits and writes TestEZ specs."""

from __future__ import annotations

from ..models import GeneratedFile, QAReport
from .base import Agent

_REVIEW_SYSTEM = """\
You are a Roblox QA and security engineer. You hunt for: client-trust exploits \
(server accepting unvalidated remote args, client-set currency/positions), \
DataStore data-loss risks (no retry, no session locking, saving on a dead \
session), race conditions, nil-indexing, memory leaks (unbound connections), and \
design risks that will hurt retention or invite cheating. You are concrete: cite \
the file and the exact problem, and give the fix.\
"""

_TEST_SYSTEM = """\
You are a Roblox engineer writing automated tests with TestEZ. You write focused \
*.spec.luau ModuleScripts that return a function for TestEZ to run, covering the \
pure/server logic of the game's core systems (economy math, progression, \
validation helpers). Put specs under shared/__tests__/ or alongside modules as \
`Name.spec.luau`. `Name.spec.luau` = ModuleScript. Write real assertions.\
"""


class QAAgent(Agent):
    name = "QA"
    topic = "qa"
    system_prompt = _REVIEW_SYSTEM

    def review(self, files: list[GeneratedFile]) -> QAReport:
        listing = "\n\n".join(f"--- {f.path} ---\n{f.content}" for f in files)
        prompt = (
            "Review this generated Roblox project. Find bugs, exploit vectors, "
            "data-loss risks, and retention/design risks. Then give a verdict "
            "(ship / fix-first) with rationale. Do NOT include test files here.\n\n"
            f"PROJECT FILES:\n{listing}"
        )
        report = self.ask_model(prompt, QAReport, max_tokens=12_000)
        report.test_files = []  # tests are generated separately, below
        return report

    def write_tests(self, files: list[GeneratedFile]) -> list[GeneratedFile]:
        listing = "\n\n".join(f"--- {f.path} ---\n{f.content}" for f in files)
        # Swap to the test-writing persona for this call.
        self.system_prompt = _TEST_SYSTEM
        try:
            return self.ask_files(
                "Write TestEZ specs covering the core server/shared logic of this "
                "project (economy, progression, validation). One spec per system.\n\n"
                f"PROJECT FILES:\n{listing}",
                max_tokens=24_000,
            )
        finally:
            self.system_prompt = _REVIEW_SYSTEM
