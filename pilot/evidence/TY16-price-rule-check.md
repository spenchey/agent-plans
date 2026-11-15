# Price-beside-APR check (Toyota end tags and emails)

Checked 2026-10-09 by the pilot (Accuracy role) against the live VDPs on motorinnautogroup.com (HTTP 200) and the source files on Mini 2.

## Governing reading (coordinator, 2026-10-09)
The rule bans OEM customer cash or bonus cash netted into a price shown beside a special APR, because the buyer cannot get both. A dealer discount is not OEM cash. Source agreeing with it: sources/OFFER-FACTS.md rule 1, "Never print a cash-netted price next to a rate ... Use advertised price = price + $180 only, with the APR."
Note on wording: the stored memory line says "never beside a special APR unless the bulletin says the cash stacks". That is the shorter paraphrase; OFFER-FACTS rule 1 and the coordinator's reading are the operative text, and Spencer approved the GH subject and preheader pairing "$48,991 / 4.99%" (TY24).

## Unit breakdowns on the live VDPs
| Unit | VDP breakdown | Toyota cash in the price? | Verdict |
|---|---|---|---|
| TTT7049 Grand Highlander Hybrid XLE | MSRP $49,311, Dealer Discount $500, Internet Price $48,811, Doc Fee +$180, Final Price $48,991 | No (College and Military -$500 are separate buyer-eligibility offers, not netted) | Price $48,991 beside 4.99% APR passes |
| TTT7015 4Runner TRD Off-Road Premium | MSRP $64,152, Dealer Discount $4,884, Internet Price $59,268, Doc Fee +$180, Final Price $59,448 | No (same separate College and Military offers) | Price $59,448 beside 4.99% APR passes |
| TTT7050 Tundra SR5 | MSRP $58,269, Customer Cash -$1,000, Doc Fee +$180, Final Price $57,449 | Yes, $1,000 Toyota Customer Cash is netted on the VDP | Not netted beside a rate: the end tag is rate-only, no price; emails use $58,449 (price + $180), never $57,449 |

Athena (inventory_source_of_truth, internet_price) agrees: GH 48,811, 4Runner 59,268, Tundra 58,269; advertised = internet price + $180.

## End tags
endtag/cfg_group-chat.json and cfg_feet-off.json carry the rate only (4.99% APR up to 48 months); the price appears as a separate super from the live VDP. cfg_not-a-drop.json is rate-only with "Or $1,000 Toyota Customer Cash. Choose one."
