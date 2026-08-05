# The organ-code tenant firewall gate is failing on PyAutoHands

Type: bug
Target: PyAutoHands
Repos:
- PyAutoHands
- pyautohands
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

The organ-code tenant firewall gate is failing on PyAutoHands. The body-map drift checker (scripts/repos_sync.py --check) exits 1 on its 'tenant firewall (organ code)' leg, so the gate is red. Six files under PyAutoHands carry hardcoded instance facts while absent from the firewall allowlist — two in the autohands package (check_search_memory.py, env_config.py) and four in its test suite — and the checker prints the offending line numbers for each. Every other leg of the drift check passes, so this single leg is what keeps the gate red. For each file decide whether the hardcoded instance name is legitimate, in which case extend the allowlist, or whether it should be parameterised out of the organ code so the firewall stays meaningful. Restore the gate to green.

<!-- formalised by the Intake (Conception) Agent on 2026-08-05 from user-intake -->
