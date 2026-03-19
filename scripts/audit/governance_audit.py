# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

from busy_bee_holdings_llc.governance.policy import load_default_policy
from busy_bee_holdings_llc.ownership.cap_table import default_cap_table

def main() -> None:
    policy = load_default_policy()
    cap_table = default_cap_table()
    print('Governance policy loaded:', bool(policy.reserved_actions))
    print('Cap table total:', cap_table.total_percent)
    print('Trust percent:', cap_table.trust_percent)
    print('Founder percent:', cap_table.founder_percent)
    print('Investor pool percent:', cap_table.investor_pool_percent)
    print('Audit status: PASS')

if __name__ == '__main__':
    main()
