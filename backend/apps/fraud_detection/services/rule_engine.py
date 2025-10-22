def apply_rules(transaction, rules):
    results = []
    for rule in rules:
        if rule["type"] == "threshold" and transaction["amount"] > rule["limit"]:
            results.append({"rule": rule["name"], "alert": True})
    return results
