# Round 3: reading tables of the answers the pinned gate held back (test half)

Unanimous answers of the six row-computed types that the gate held back, the secondary hypothesis's three types first; written by `scripts/checkable3_secondary.py` with `scripts/explain_check.py`'s table. "asked" marks the readings the frozen conventions (`data/conventions_original.yaml`) ask.

## original/1078 (best_region_identification, wrong)

```
run 1: answer va (key id, wrong)
  own level: pass (deciding query: receipt entry 1)
  [asked] season_months = meteorological; season_year = december_of_y; date_field = CreatedDate -> id
      SELECT Account.ShippingState, CreatedDate, ClosedDate FROM Case WHERE Status = 'Closed' AND Account.ShippingState != NULL AND CreatedDate >= 2020-12-01T00:00:00Z AND CreatedDate < 2021-03-01T00:00:00Z
  season_months = meteorological; season_year = december_of_y; date_field = ClosedDate -> nv
      SELECT Account.ShippingState, CreatedDate, ClosedDate FROM Case WHERE Status = 'Closed' AND Account.ShippingState != NULL AND ClosedDate >= 2020-12-01T00:00:00Z AND ClosedDate < 2021-03-01T00:00:00Z
  season_months = meteorological; season_year = december_before_y; date_field = CreatedDate -> va
      SELECT Account.ShippingState, CreatedDate, ClosedDate FROM Case WHERE Status = 'Closed' AND Account.ShippingState != NULL AND CreatedDate >= 2019-12-01T00:00:00Z AND CreatedDate < 2020-03-01T00:00:00Z
  season_months = meteorological; season_year = december_before_y; date_field = ClosedDate -> va
      SELECT Account.ShippingState, CreatedDate, ClosedDate FROM Case WHERE Status = 'Closed' AND Account.ShippingState != NULL AND ClosedDate >= 2019-12-01T00:00:00Z AND ClosedDate < 2020-03-01T00:00:00Z
  season_months = quarter_aligned; date_field = CreatedDate -> id
      SELECT Account.ShippingState, CreatedDate, ClosedDate FROM Case WHERE Status = 'Closed' AND Account.ShippingState != NULL AND CreatedDate >= 2020-01-01T00:00:00Z AND CreatedDate < 2020-04-01T00:00:00Z
  season_months = quarter_aligned; date_field = ClosedDate -> id
      SELECT Account.ShippingState, CreatedDate, ClosedDate FROM Case WHERE Status = 'Closed' AND Account.ShippingState != NULL AND ClosedDate >= 2020-01-01T00:00:00Z AND ClosedDate < 2020-04-01T00:00:00Z
run 2: answer va (key id, wrong)
  own level: pass (deciding query: receipt entry 1)
  [asked] season_months = meteorological; season_year = december_of_y; date_field = CreatedDate -> id
      SELECT Account.ShippingState, ClosedDate, CreatedDate FROM Case WHERE Account.ShippingState != NULL AND ClosedDate != NULL AND CreatedDate != NULL AND CreatedDate >= 2020-12-01T00:00:00Z AND CreatedDate < 2021-03-01T00:00:00Z
  season_months = meteorological; season_year = december_of_y; date_field = ClosedDate -> nv
      SELECT Account.ShippingState, ClosedDate, CreatedDate FROM Case WHERE Account.ShippingState != NULL AND ClosedDate != NULL AND CreatedDate != NULL AND ClosedDate >= 2020-12-01T00:00:00Z AND ClosedDate < 2021-03-01T00:00:00Z
  season_months = meteorological; season_year = december_before_y; date_field = CreatedDate -> va
      SELECT Account.ShippingState, ClosedDate, CreatedDate FROM Case WHERE Account.ShippingState != NULL AND ClosedDate != NULL AND CreatedDate != NULL AND CreatedDate >= 2019-12-01T00:00:00Z AND CreatedDate < 2020-03-01T00:00:00Z
  season_months = meteorological; season_year = december_before_y; date_field = ClosedDate -> va
      SELECT Account.ShippingState, ClosedDate, CreatedDate FROM Case WHERE Account.ShippingState != NULL AND ClosedDate != NULL AND CreatedDate != NULL AND ClosedDate >= 2019-12-01T00:00:00Z AND ClosedDate < 2020-03-01T00:00:00Z
  season_months = quarter_aligned; date_field = CreatedDate -> id
      SELECT Account.ShippingState, ClosedDate, CreatedDate FROM Case WHERE Account.ShippingState != NULL AND ClosedDate != NULL AND CreatedDate != NULL AND CreatedDate >= 2020-01-01T00:00:00Z AND CreatedDate < 2020-04-01T00:00:00Z
  season_months = quarter_aligned; date_field = ClosedDate -> id
      SELECT Account.ShippingState, ClosedDate, CreatedDate FROM Case WHERE Account.ShippingState != NULL AND ClosedDate != NULL AND CreatedDate != NULL AND ClosedDate >= 2020-01-01T00:00:00Z AND ClosedDate < 2020-04-01T00:00:00Z
run 3: answer va (key id, wrong)
  own level: pass (deciding query: receipt entry 2)
  [asked] season_months = meteorological; season_year = december_of_y; date_field = CreatedDate -> id
      SELECT Id, CreatedDate, ClosedDate, Account.ShippingState FROM Case WHERE ClosedDate != null AND CreatedDate >= 2020-12-01T00:00:00Z AND CreatedDate < 2021-03-01T00:00:00Z
  season_months = meteorological; season_year = december_of_y; date_field = ClosedDate -> nv
      SELECT Id, CreatedDate, ClosedDate, Account.ShippingState FROM Case WHERE ClosedDate != null AND ClosedDate >= 2020-12-01T00:00:00Z AND ClosedDate < 2021-03-01T00:00:00Z
  season_months = meteorological; season_year = december_before_y; date_field = CreatedDate -> va
      SELECT Id, CreatedDate, ClosedDate, Account.ShippingState FROM Case WHERE ClosedDate != null AND CreatedDate >= 2019-12-01T00:00:00Z AND CreatedDate < 2020-03-01T00:00:00Z
  season_months = meteorological; season_year = december_before_y; date_field = ClosedDate -> va
      SELECT Id, CreatedDate, ClosedDate, Account.ShippingState FROM Case WHERE ClosedDate != null AND ClosedDate >= 2019-12-01T00:00:00Z AND ClosedDate < 2020-03-01T00:00:00Z
  season_months = quarter_aligned; date_field = CreatedDate -> id
      SELECT Id, CreatedDate, ClosedDate, Account.ShippingState FROM Case WHERE ClosedDate != null AND CreatedDate >= 2020-01-01T00:00:00Z AND CreatedDate < 2020-04-01T00:00:00Z
  season_months = quarter_aligned; date_field = ClosedDate -> id
      SELECT Id, CreatedDate, ClosedDate, Account.ShippingState FROM Case WHERE ClosedDate != null AND ClosedDate >= 2020-01-01T00:00:00Z AND ClosedDate < 2020-04-01T00:00:00Z
```

## original/1081 (best_region_identification, wrong)

```
run 1: answer tn (key ga, wrong)
  own level: pass (deciding query: receipt entry 1)
  [asked] date_field = CreatedDate -> ga
      SELECT Account.ShippingState, CreatedDate, ClosedDate FROM Case WHERE Account.ShippingState != NULL AND CreatedDate >= 2020-11-01T00:00:00Z AND CreatedDate < 2020-12-01T00:00:00Z
  date_field = ClosedDate -> tn
      SELECT Account.ShippingState, CreatedDate, ClosedDate FROM Case WHERE Account.ShippingState != NULL AND ClosedDate >= 2020-11-01T00:00:00Z AND ClosedDate < 2020-12-01T00:00:00Z
run 2: answer tn (key ga, wrong)
  own level: pass (deciding query: receipt entry 2)
  [asked] date_field = CreatedDate -> ga
      SELECT Account.ShippingState, CreatedDate, ClosedDate FROM Case WHERE CreatedDate >= 2020-11-01T00:00:00Z AND CreatedDate < 2020-12-01T00:00:00Z
  date_field = ClosedDate -> tn
      SELECT Account.ShippingState, CreatedDate, ClosedDate FROM Case WHERE ClosedDate >= 2020-11-01T00:00:00Z AND ClosedDate < 2020-12-01T00:00:00Z
run 3: answer tn (key ga, wrong)
  own level: pass (deciding query: receipt entry 1)
  [asked] date_field = CreatedDate -> ga
      SELECT Id, CreatedDate, ClosedDate, Account.ShippingState FROM Case WHERE Status = 'Closed' AND CreatedDate >= 2020-11-01T00:00:00Z AND CreatedDate < 2020-12-01T00:00:00Z
  date_field = ClosedDate -> tn
      SELECT Id, CreatedDate, ClosedDate, Account.ShippingState FROM Case WHERE Status = 'Closed' AND ClosedDate >= 2020-11-01T00:00:00Z AND ClosedDate < 2020-12-01T00:00:00Z
```

## original/780 (transfer_count, right)

```
run 1: answer 005Ws000001xatJ (key 005Ws000001xatJ, right)
  own level: fail (deciding query: receipt entry 4)
  [asked] past_months_years = rolling; rolling_end = today_counted -> 005Ws000001xYl3
      SELECT Id, CaseId__c, CreatedDate, OldValue__c, NewValue__c FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2021-07-22T00:00:00Z AND CreatedDate < 2021-09-23T00:00:00Z ORDER BY CreatedDate DESC
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> 005Ws000001xYl3
      SELECT Id, CaseId__c, CreatedDate, OldValue__c, NewValue__c FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2021-07-22T00:00:00Z AND CreatedDate < 2021-09-22T00:00:00Z ORDER BY CreatedDate DESC
  past_months_years = calendar -> 005Ws000001xYl3
      SELECT Id, CaseId__c, CreatedDate, OldValue__c, NewValue__c FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2021-07-01T00:00:00Z AND CreatedDate < 2021-09-01T00:00:00Z ORDER BY CreatedDate DESC
run 2: answer 005Ws000001xatJ (key 005Ws000001xatJ, right)
  own level: pass (deciding query: receipt entry 6)
  [asked] past_months_years = rolling; rolling_end = today_counted -> 005Ws000001xatJ
      SELECT Id, CaseId__c, CreatedDate, Field__c, OldValue__c, NewValue__c FROM CaseHistory__c WHERE CaseId__c = '500Ws000007rQunIAE' AND CreatedDate >= 2021-07-22T00:00:00Z AND CreatedDate < 2021-09-23T00:00:00Z ORDER BY CreatedDate ASC
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> 005Ws000001xatJ
      SELECT Id, CaseId__c, CreatedDate, Field__c, OldValue__c, NewValue__c FROM CaseHistory__c WHERE CaseId__c = '500Ws000007rQunIAE' AND CreatedDate >= 2021-07-22T00:00:00Z AND CreatedDate < 2021-09-22T00:00:00Z ORDER BY CreatedDate ASC
  past_months_years = calendar -> 005Ws000001xatJ
      SELECT Id, CaseId__c, CreatedDate, Field__c, OldValue__c, NewValue__c FROM CaseHistory__c WHERE CaseId__c = '500Ws000007rQunIAE' AND CreatedDate >= 2021-07-01T00:00:00Z AND CreatedDate < 2021-09-01T00:00:00Z ORDER BY CreatedDate ASC
run 3: answer 005Ws000001xatJ (key 005Ws000001xatJ, right)
  own level: pass (deciding query: receipt entry 4)
  [asked] past_months_years = rolling; rolling_end = today_counted -> 005Ws000001xatJ
      SELECT Id, CaseId__c, CreatedDate, Field__c, NewValue__c, OldValue__c FROM CaseHistory__c WHERE NewValue__c = '005Ws000001xatJIAQ' AND OldValue__c = null AND CreatedDate >= 2021-07-22T00:00:00Z AND CreatedDate < 2021-09-23T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> 005Ws000001xatJ
      SELECT Id, CaseId__c, CreatedDate, Field__c, NewValue__c, OldValue__c FROM CaseHistory__c WHERE NewValue__c = '005Ws000001xatJIAQ' AND OldValue__c = null AND CreatedDate >= 2021-07-22T00:00:00Z AND CreatedDate < 2021-09-22T00:00:00Z
  past_months_years = calendar -> 005Ws000001xatJ
      SELECT Id, CaseId__c, CreatedDate, Field__c, NewValue__c, OldValue__c FROM CaseHistory__c WHERE NewValue__c = '005Ws000001xatJIAQ' AND OldValue__c = null AND CreatedDate >= 2021-07-01T00:00:00Z AND CreatedDate < 2021-09-01T00:00:00Z
```

## original/786 (transfer_count, right)

```
run 1: answer 005Ws000001xZvd (key 005Ws000001xZvd, right)
  own level: pass (deciding query: receipt entry 10)
  [asked] past_quarters = rolling; rolling_end = today_counted -> 005Ws000001xZvd
      SELECT CaseId__c, CreatedDate, Field__c, NewValue__c, OldValue__c FROM CaseHistory__c WHERE (NewValue__c = '005Ws000001xZvdIAE' OR OldValue__c = '005Ws000001xZvdIAE') AND CreatedDate >= 2019-12-03T00:00:00Z AND CreatedDate < 2020-06-04T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> 005Ws000001xZvd
      SELECT CaseId__c, CreatedDate, Field__c, NewValue__c, OldValue__c FROM CaseHistory__c WHERE (NewValue__c = '005Ws000001xZvdIAE' OR OldValue__c = '005Ws000001xZvdIAE') AND CreatedDate >= 2019-12-03T00:00:00Z AND CreatedDate < 2020-06-03T00:00:00Z
  past_quarters = calendar -> 005Ws000001xZvd
      SELECT CaseId__c, CreatedDate, Field__c, NewValue__c, OldValue__c FROM CaseHistory__c WHERE (NewValue__c = '005Ws000001xZvdIAE' OR OldValue__c = '005Ws000001xZvdIAE') AND CreatedDate >= 2019-10-01T00:00:00Z AND CreatedDate < 2020-04-01T00:00:00Z
run 2: answer 005Ws000001xZvd (key 005Ws000001xZvd, right)
  own level: fail (deciding query: receipt entry 10)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT CaseId__c, Field__c, OldValue__c, NewValue__c, CreatedDate FROM CaseHistory__c WHERE CaseId__c = '500Ws000007rQ2tIAE' AND CreatedDate >= 2019-12-03T00:00:00Z AND CreatedDate < 2020-06-04T00:00:00Z ORDER BY CreatedDate ASC
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT CaseId__c, Field__c, OldValue__c, NewValue__c, CreatedDate FROM CaseHistory__c WHERE CaseId__c = '500Ws000007rQ2tIAE' AND CreatedDate >= 2019-12-03T00:00:00Z AND CreatedDate < 2020-06-03T00:00:00Z ORDER BY CreatedDate ASC
  past_quarters = calendar -> None
      SELECT CaseId__c, Field__c, OldValue__c, NewValue__c, CreatedDate FROM CaseHistory__c WHERE CaseId__c = '500Ws000007rQ2tIAE' AND CreatedDate >= 2019-10-01T00:00:00Z AND CreatedDate < 2020-04-01T00:00:00Z ORDER BY CreatedDate ASC
run 3: answer 005Ws000001xZvd (key 005Ws000001xZvd, right)
  own level: pass (deciding query: receipt entry 3)
  [asked] past_quarters = rolling; rolling_end = today_counted -> 005Ws000001xZvd
      SELECT Id, CreatedDate, Field__c, OldValue__c, NewValue__c, CaseId__c FROM CaseHistory__c WHERE CreatedDate >= 2019-12-03T00:00:00Z AND CreatedDate < 2020-06-04T00:00:00Z ORDER BY CreatedDate ASC
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> 005Ws000001xZvd
      SELECT Id, CreatedDate, Field__c, OldValue__c, NewValue__c, CaseId__c FROM CaseHistory__c WHERE CreatedDate >= 2019-12-03T00:00:00Z AND CreatedDate < 2020-06-03T00:00:00Z ORDER BY CreatedDate ASC
  past_quarters = calendar -> 005Ws000001xZvd
      SELECT Id, CreatedDate, Field__c, OldValue__c, NewValue__c, CaseId__c FROM CaseHistory__c WHERE CreatedDate >= 2019-10-01T00:00:00Z AND CreatedDate < 2020-04-01T00:00:00Z ORDER BY CreatedDate ASC
```

## original/808 (transfer_count, wrong)

```
run 1: answer None (key 005Ws000001xa0T, wrong)
  own level: pass (deciding query: receipt entry 4)
  [asked] past_months_years = rolling; rolling_end = today_counted -> a tie: 005Ws000001xYrV (first) or None
      SELECT OldValue__c, COUNT(Id) cnt FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2023-01-25T00:00:00Z AND CreatedDate < 2023-06-26T00:00:00Z GROUP BY OldValue__c
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> a tie: 005Ws000001xYrV (first) or None
      SELECT OldValue__c, COUNT(Id) cnt FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2023-01-25T00:00:00Z AND CreatedDate < 2023-06-25T00:00:00Z GROUP BY OldValue__c
  past_months_years = calendar -> a tie: 005Ws000001xYrV (first) or None
      SELECT OldValue__c, COUNT(Id) cnt FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2023-01-01T00:00:00Z AND CreatedDate < 2023-06-01T00:00:00Z GROUP BY OldValue__c
run 2: answer None (key 005Ws000001xa0T, wrong)
  own level: pass (deciding query: receipt entry 5)
  [asked] past_months_years = rolling; rolling_end = today_counted -> a tie: 005Ws000001xYrV (first) or None
      SELECT OldValue__c, COUNT(Id) FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2023-01-25T00:00:00Z AND CreatedDate < 2023-06-26T00:00:00Z GROUP BY OldValue__c
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> a tie: 005Ws000001xYrV (first) or None
      SELECT OldValue__c, COUNT(Id) FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2023-01-25T00:00:00Z AND CreatedDate < 2023-06-25T00:00:00Z GROUP BY OldValue__c
  past_months_years = calendar -> a tie: 005Ws000001xYrV (first) or None
      SELECT OldValue__c, COUNT(Id) FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2023-01-01T00:00:00Z AND CreatedDate < 2023-06-01T00:00:00Z GROUP BY OldValue__c
run 3: answer None (key 005Ws000001xa0T, wrong)
  own level: pass (deciding query: receipt entry 7)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT Id, CaseId__c, Field__c, OldValue__c, NewValue__c, CreatedDate FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND CreatedDate >= 2023-01-25T00:00:00Z AND CreatedDate < 2023-06-26T00:00:00Z ORDER BY CaseId__c, CreatedDate ASC
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT Id, CaseId__c, Field__c, OldValue__c, NewValue__c, CreatedDate FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND CreatedDate >= 2023-01-25T00:00:00Z AND CreatedDate < 2023-06-25T00:00:00Z ORDER BY CaseId__c, CreatedDate ASC
  past_months_years = calendar -> a tie: 005Ws000001xYl3 (first) or None
      SELECT Id, CaseId__c, Field__c, OldValue__c, NewValue__c, CreatedDate FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND CreatedDate >= 2023-01-01T00:00:00Z AND CreatedDate < 2023-06-01T00:00:00Z ORDER BY CaseId__c, CreatedDate ASC
```

## original/872 (transfer_count, right)

```
run 1: answer 005Ws000001xYoH (key 005Ws000001xYoH, right)
  own level: pass (deciding query: receipt entry 5)
  [asked] the period the question names -> a tie: 005Ws000001xYoH (first) or None
      SELECT OldValue__c, count(Id) FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2021-06-01T00:00:00Z AND CreatedDate < 2021-07-01T00:00:00Z GROUP BY OldValue__c
run 2: answer 005Ws000001xYoH (key 005Ws000001xYoH, right)
  own level: pass (deciding query: receipt entry 5)
  [asked] the period the question names -> 005Ws000001xYoH
      SELECT Id, CaseId__c, Field__c, NewValue__c, OldValue__c, CreatedDate FROM CaseHistory__c WHERE CaseId__c IN ('500Ws000007rQd8IAE', '500Ws000007qmEFIAY', '500Ws000007rGCQIA2') AND CreatedDate >= 2021-06-01T00:00:00Z AND CreatedDate < 2021-07-01T00:00:00Z ORDER BY CaseId__c, CreatedDate
run 3: answer 005Ws000001xYoH (key 005Ws000001xYoH, right)
  own level: pass (deciding query: receipt entry 4)
  [asked] the period the question names -> a tie: 005Ws000001xYoH (first) or None
      SELECT OldValue__c, count(Id) FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2021-06-01T00:00:00Z AND CreatedDate < 2021-07-01T00:00:00Z GROUP BY OldValue__c
```

## original/880 (transfer_count, right)

```
run 1: answer None (key None, right)
  own level: pass (deciding query: receipt entry 9)
  [asked] season_months = meteorological -> None
      SELECT CaseId__c, CreatedDate, Field__c, OldValue__c, NewValue__c FROM CaseHistory__c WHERE CaseId__c = '500Ws000007qqnQIAQ' AND CreatedDate >= 2022-09-01T00:00:00Z AND CreatedDate < 2022-12-01T00:00:00Z ORDER BY CreatedDate
  season_months = quarter_aligned -> None
      SELECT CaseId__c, CreatedDate, Field__c, OldValue__c, NewValue__c FROM CaseHistory__c WHERE CaseId__c = '500Ws000007qqnQIAQ' AND CreatedDate >= 2022-10-01T00:00:00Z AND CreatedDate < 2023-01-01T00:00:00Z ORDER BY CreatedDate
run 2: answer None (key None, right)
  own level: pass (deciding query: receipt entry 2)
  [asked] season_months = meteorological -> a tie: 005Ws000001xSR9 (first) or None
      SELECT OldValue__c, COUNT(Id) transfers FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2022-09-01T00:00:00Z AND CreatedDate < 2022-12-01T00:00:00Z GROUP BY OldValue__c
  season_months = quarter_aligned -> a tie: 005Ws000001xYt7 (first) or None
      SELECT OldValue__c, COUNT(Id) transfers FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2022-10-01T00:00:00Z AND CreatedDate < 2023-01-01T00:00:00Z GROUP BY OldValue__c
run 3: answer None (key None, right)
  own level: pass (deciding query: receipt entry 3)
  [asked] season_months = meteorological -> a tie: 005Ws000001xSR9 (first) or None
      SELECT OldValue__c, COUNT(Id) cnt FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2022-09-01T00:00:00Z AND CreatedDate < 2022-12-01T00:00:00Z GROUP BY OldValue__c
  season_months = quarter_aligned -> a tie: 005Ws000001xYt7 (first) or None
      SELECT OldValue__c, COUNT(Id) cnt FROM CaseHistory__c WHERE Field__c = 'Owner Assignment' AND OldValue__c != null AND CreatedDate >= 2022-10-01T00:00:00Z AND CreatedDate < 2023-01-01T00:00:00Z GROUP BY OldValue__c
```

## original/737 (handle_time, right)

```
run 1: answer 005Ws000001xZVp (key 005Ws000001xZVp, right)
  own level: fail (deciding query: receipt entry 4)
  [asked] date_field = CreatedDate -> None
      SELECT Id, CaseNumber, CreatedDate, ClosedDate, Status, OwnerId FROM Case WHERE CreatedDate >= 2023-04-01T00:00:00Z AND CreatedDate < 2023-07-01T00:00:00Z
  date_field = ClosedDate -> None
      SELECT Id, CaseNumber, CreatedDate, ClosedDate, Status, OwnerId FROM Case WHERE ClosedDate >= 2023-04-01T00:00:00Z AND ClosedDate < 2023-07-01T00:00:00Z
run 2: answer 005Ws000001xZVp (key 005Ws000001xZVp, right)
  own level: pass (deciding query: receipt entry 3)
  [asked] date_field = CreatedDate -> 005Ws000001xZVp
      SELECT Id, OwnerId, CreatedDate, ClosedDate, Status FROM Case WHERE CreatedDate >= 2023-04-01T00:00:00Z AND CreatedDate < 2023-07-01T00:00:00Z
  date_field = ClosedDate -> 005Ws000001xZVp
      SELECT Id, OwnerId, CreatedDate, ClosedDate, Status FROM Case WHERE ClosedDate >= 2023-04-01T00:00:00Z AND ClosedDate < 2023-07-01T00:00:00Z
run 3: answer 005Ws000001xZVp (key 005Ws000001xZVp, right)
  own level: pass (deciding query: receipt entry 3)
  [asked] date_field = CreatedDate -> 005Ws000001xZVp
      SELECT Id, CreatedDate, ClosedDate, OwnerId FROM Case WHERE CreatedDate >= 2023-04-01T00:00:00Z AND CreatedDate < 2023-07-01T00:00:00Z
  date_field = ClosedDate -> 005Ws000001xZVp
      SELECT Id, CreatedDate, ClosedDate, OwnerId FROM Case WHERE ClosedDate >= 2023-04-01T00:00:00Z AND ClosedDate < 2023-07-01T00:00:00Z
```

## original/759 (handle_time, wrong)

```
run 1: answer 005Ws000001xamr (key 005Ws000001xZCT, wrong)
  own level: fail (deciding query: receipt entry 6)
  [asked] past_quarters = rolling; rolling_end = today_counted; date_field = CreatedDate -> 005Ws000001xaQI
      SELECT Id, CreatedDate, ClosedDate, OwnerId, Status FROM Case WHERE Status = 'Closed' AND CreatedDate >= 2021-07-18T00:00:00Z AND CreatedDate < 2022-04-19T00:00:00Z
  past_quarters = rolling; rolling_end = today_counted; date_field = ClosedDate -> 005Ws000001xaQI
      SELECT Id, CreatedDate, ClosedDate, OwnerId, Status FROM Case WHERE Status = 'Closed' AND ClosedDate >= 2021-07-18T00:00:00Z AND ClosedDate < 2022-04-19T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted; date_field = CreatedDate -> 005Ws000001xaQI
      SELECT Id, CreatedDate, ClosedDate, OwnerId, Status FROM Case WHERE Status = 'Closed' AND CreatedDate >= 2021-07-18T00:00:00Z AND CreatedDate < 2022-04-18T00:00:00Z
  past_quarters = rolling; rolling_end = today_not_counted; date_field = ClosedDate -> 005Ws000001xaQI
      SELECT Id, CreatedDate, ClosedDate, OwnerId, Status FROM Case WHERE Status = 'Closed' AND ClosedDate >= 2021-07-18T00:00:00Z AND ClosedDate < 2022-04-18T00:00:00Z
  past_quarters = calendar; date_field = CreatedDate -> 005Ws000001xamr
      SELECT Id, CreatedDate, ClosedDate, OwnerId, Status FROM Case WHERE Status = 'Closed' AND CreatedDate >= 2021-07-01T00:00:00Z AND CreatedDate < 2022-04-01T00:00:00Z
  past_quarters = calendar; date_field = ClosedDate -> 005Ws000001xamr
      SELECT Id, CreatedDate, ClosedDate, OwnerId, Status FROM Case WHERE Status = 'Closed' AND ClosedDate >= 2021-07-01T00:00:00Z AND ClosedDate < 2022-04-01T00:00:00Z
run 2: answer 005Ws000001xamr (key 005Ws000001xZCT, wrong)
  not checked: no applicable query
run 3: answer 005Ws000001xamr (key 005Ws000001xZCT, wrong)
  own level: fail (deciding query: receipt entry 2)
  [asked] past_quarters = rolling; rolling_end = today_counted; date_field = CreatedDate -> 005Ws000001xaQI
      SELECT Id, CaseNumber, CreatedDate, ClosedDate, Status, OwnerId FROM Case WHERE CreatedDate >= 2021-07-18T00:00:00Z AND CreatedDate < 2022-04-19T00:00:00Z
  past_quarters = rolling; rolling_end = today_counted; date_field = ClosedDate -> 005Ws000001xaQI
      SELECT Id, CaseNumber, CreatedDate, ClosedDate, Status, OwnerId FROM Case WHERE ClosedDate >= 2021-07-18T00:00:00Z AND ClosedDate < 2022-04-19T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted; date_field = CreatedDate -> 005Ws000001xaQI
      SELECT Id, CaseNumber, CreatedDate, ClosedDate, Status, OwnerId FROM Case WHERE CreatedDate >= 2021-07-18T00:00:00Z AND CreatedDate < 2022-04-18T00:00:00Z
  past_quarters = rolling; rolling_end = today_not_counted; date_field = ClosedDate -> 005Ws000001xaQI
      SELECT Id, CaseNumber, CreatedDate, ClosedDate, Status, OwnerId FROM Case WHERE ClosedDate >= 2021-07-18T00:00:00Z AND ClosedDate < 2022-04-18T00:00:00Z
  past_quarters = calendar; date_field = CreatedDate -> 005Ws000001xamr
      SELECT Id, CaseNumber, CreatedDate, ClosedDate, Status, OwnerId FROM Case WHERE CreatedDate >= 2021-07-01T00:00:00Z AND CreatedDate < 2022-04-01T00:00:00Z
  past_quarters = calendar; date_field = ClosedDate -> 005Ws000001xamr
      SELECT Id, CaseNumber, CreatedDate, ClosedDate, Status, OwnerId FROM Case WHERE ClosedDate >= 2021-07-01T00:00:00Z AND ClosedDate < 2022-04-01T00:00:00Z
```

## original/147 (monthly_trend_analysis, right)

```
run 1: answer june (key june, right)
  own level: pass (deciding query: receipt entry 5)
  [asked] past_months_years = rolling; rolling_end = today_counted -> june
      SELECT CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001ltLaIAI', '802Ws000001lwmgIAA', '802Ws000001lxQiIAI', '802Ws000001lyeUIAQ', '802Ws000001lz19IAA', '802Ws000001m08VIAQ', '802Ws000001m0MxIAI', '802Ws000001m0gRIAQ', '802Ws000001m25WIAQ', '802Ws000001m26zIAA', '802Ws000001m2TnIAI', '802Ws000001m47FIAQ', '802Ws000001m4KDIAY', '802Ws000001m4SFIAY', '802Ws000001m54sIAA', '802Ws000001m5eLIAQ', '802Ws000001m5hZIAQ', '802Ws000001m6uKIAQ', '802Ws000001m8qlIAA', '802Ws000001m9tLIAQ', '802Ws000001mAPWIA2', '802Ws000001mCKvIAM', '802Ws000001mCKyIAM', '802Ws000001mDTqIAM') AND CreatedDate >= 2022-06-01T00:00:00Z AND CreatedDate < 2023-05-02T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> june
      SELECT CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001ltLaIAI', '802Ws000001lwmgIAA', '802Ws000001lxQiIAI', '802Ws000001lyeUIAQ', '802Ws000001lz19IAA', '802Ws000001m08VIAQ', '802Ws000001m0MxIAI', '802Ws000001m0gRIAQ', '802Ws000001m25WIAQ', '802Ws000001m26zIAA', '802Ws000001m2TnIAI', '802Ws000001m47FIAQ', '802Ws000001m4KDIAY', '802Ws000001m4SFIAY', '802Ws000001m54sIAA', '802Ws000001m5eLIAQ', '802Ws000001m5hZIAQ', '802Ws000001m6uKIAQ', '802Ws000001m8qlIAA', '802Ws000001m9tLIAQ', '802Ws000001mAPWIA2', '802Ws000001mCKvIAM', '802Ws000001mCKyIAM', '802Ws000001mDTqIAM') AND CreatedDate >= 2022-06-01T00:00:00Z AND CreatedDate < 2023-05-01T00:00:00Z
  past_months_years = calendar -> june
      SELECT CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001ltLaIAI', '802Ws000001lwmgIAA', '802Ws000001lxQiIAI', '802Ws000001lyeUIAQ', '802Ws000001lz19IAA', '802Ws000001m08VIAQ', '802Ws000001m0MxIAI', '802Ws000001m0gRIAQ', '802Ws000001m25WIAQ', '802Ws000001m26zIAA', '802Ws000001m2TnIAI', '802Ws000001m47FIAQ', '802Ws000001m4KDIAY', '802Ws000001m4SFIAY', '802Ws000001m54sIAA', '802Ws000001m5eLIAQ', '802Ws000001m5hZIAQ', '802Ws000001m6uKIAQ', '802Ws000001m8qlIAA', '802Ws000001m9tLIAQ', '802Ws000001mAPWIA2', '802Ws000001mCKvIAM', '802Ws000001mCKyIAM', '802Ws000001mDTqIAM') AND CreatedDate >= 2022-06-01T00:00:00Z AND CreatedDate < 2023-05-01T00:00:00Z
run 2: answer june (key june, right)
  own level: fail (deciding query: receipt entry 5)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wODjIAM' AND CreatedDate >= 2022-06-01T00:00:00Z AND CreatedDate < 2023-05-02T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wODjIAM' AND CreatedDate >= 2022-06-01T00:00:00Z AND CreatedDate < 2023-05-01T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
  past_months_years = calendar -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wODjIAM' AND CreatedDate >= 2022-06-01T00:00:00Z AND CreatedDate < 2023-05-01T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
run 3: answer june (key june, right)
  own level: pass (deciding query: receipt entry 7)
  [asked] past_months_years = rolling; rolling_end = today_counted -> june
      SELECT Id, CreatedDate, OrderItemId__c, Subject FROM Case WHERE CreatedDate >= 2022-06-01T00:00:00Z AND CreatedDate < 2023-05-02T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> june
      SELECT Id, CreatedDate, OrderItemId__c, Subject FROM Case WHERE CreatedDate >= 2022-06-01T00:00:00Z AND CreatedDate < 2023-05-01T00:00:00Z
  past_months_years = calendar -> june
      SELECT Id, CreatedDate, OrderItemId__c, Subject FROM Case WHERE CreatedDate >= 2022-06-01T00:00:00Z AND CreatedDate < 2023-05-01T00:00:00Z
```

## original/148 (monthly_trend_analysis, right)

```
run 1: answer march (key march, right)
  own level: fail (deciding query: receipt entry 3)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wRxxIAE' AND CreatedDate >= 2019-12-16T00:00:00Z AND CreatedDate < 2021-06-17T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wRxxIAE' AND CreatedDate >= 2019-12-16T00:00:00Z AND CreatedDate < 2021-06-16T00:00:00Z
  past_quarters = calendar -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wRxxIAE' AND CreatedDate >= 2019-10-01T00:00:00Z AND CreatedDate < 2021-04-01T00:00:00Z
run 2: answer march (key march, right)
  own level: fail (deciding query: receipt entry 2)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT CALENDAR_YEAR(CreatedDate) Year, CALENDAR_MONTH(CreatedDate) Month, COUNT(Id) Total FROM Case WHERE ProductId = '01tWs000002wRxxIAE' AND CreatedDate >= 2019-12-16T00:00:00Z AND CreatedDate < 2021-06-17T00:00:00Z GROUP BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT CALENDAR_YEAR(CreatedDate) Year, CALENDAR_MONTH(CreatedDate) Month, COUNT(Id) Total FROM Case WHERE ProductId = '01tWs000002wRxxIAE' AND CreatedDate >= 2019-12-16T00:00:00Z AND CreatedDate < 2021-06-16T00:00:00Z GROUP BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
  past_quarters = calendar -> None
      SELECT CALENDAR_YEAR(CreatedDate) Year, CALENDAR_MONTH(CreatedDate) Month, COUNT(Id) Total FROM Case WHERE ProductId = '01tWs000002wRxxIAE' AND CreatedDate >= 2019-10-01T00:00:00Z AND CreatedDate < 2021-04-01T00:00:00Z GROUP BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
run 3: answer march (key march, right)
  own level: pass (deciding query: receipt entry 9)
  [asked] past_quarters = rolling; rolling_end = today_counted -> march
      SELECT Id, CreatedDate, Subject, OrderItemId__c, IssueId__c FROM Case WHERE Id IN ('500Ws000007rETxIAM', '500Ws000007rHA6IAM', '500Ws000007rRsTIAU') AND CreatedDate >= 2019-12-16T00:00:00Z AND CreatedDate < 2021-06-17T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> march
      SELECT Id, CreatedDate, Subject, OrderItemId__c, IssueId__c FROM Case WHERE Id IN ('500Ws000007rETxIAM', '500Ws000007rHA6IAM', '500Ws000007rRsTIAU') AND CreatedDate >= 2019-12-16T00:00:00Z AND CreatedDate < 2021-06-16T00:00:00Z
  past_quarters = calendar -> march
      SELECT Id, CreatedDate, Subject, OrderItemId__c, IssueId__c FROM Case WHERE Id IN ('500Ws000007rETxIAM', '500Ws000007rHA6IAM', '500Ws000007rRsTIAU') AND CreatedDate >= 2019-10-01T00:00:00Z AND CreatedDate < 2021-04-01T00:00:00Z
```

## original/153 (monthly_trend_analysis, right)

```
run 1: answer september (key september, right)
  not checked: no applicable query
run 2: answer september (key september, right)
  own level: fail (deciding query: receipt entry 3)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wRmfIAE' AND CreatedDate >= 2020-07-14T00:00:00Z AND CreatedDate < 2021-05-15T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wRmfIAE' AND CreatedDate >= 2020-07-14T00:00:00Z AND CreatedDate < 2021-05-14T00:00:00Z
  past_months_years = calendar -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wRmfIAE' AND CreatedDate >= 2020-07-01T00:00:00Z AND CreatedDate < 2021-05-01T00:00:00Z
run 3: answer september (key september, right)
  own level: pass (deciding query: receipt entry 5)
  [asked] past_months_years = rolling; rolling_end = today_counted -> september
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lr1zIAA', '802Ws000001lt8ZIAQ', '802Ws000001lu1TIAQ', '802Ws000001lu31IAA', '802Ws000001lvonIAA', '802Ws000001lvwlIAA', '802Ws000001lw02IAA', '802Ws000001lwOAIAY', '802Ws000001lwRVIAY', '802Ws000001lwpiIAA', '802Ws000001lx2ZIAQ', '802Ws000001lxIiIAI', '802Ws000001ly57IAA', '802Ws000001lyWcIAI', '802Ws000001lz4MIAQ', '802Ws000001lz9CIAQ', '802Ws000001lzPFIAY', '802Ws000001lzp3IAA', '802Ws000001m0bYIAQ', '802Ws000001m0hwIAA', '802Ws000001m1CeIAI', '802Ws000001m1ZJIAY', '802Ws000001m1cVIAQ', '802Ws000001m1e0IAA', '802Ws000001m23mIAA', '802Ws000001m2GjIAI', '802Ws000001m2n2IAA', '802Ws000001m3XjIAI', '802Ws000001m4bzIAA', '802Ws000001m51eIAA', '802Ws000001m67OIAQ', '802Ws000001m6HCIAY', '802Ws000001m6LvIAI', '802Ws000001m6QmIAI', '802Ws000001m6VdIAI', '802Ws000001m6nLIAQ', '802Ws000001m76kIAA', '802Ws000001m8KUIAY', '802Ws000001m8igIAA', '802Ws000001m9GXIAY', '802Ws000001m9JlIAI', '802Ws000001mAqyIAE', '802Ws000001mAxYIAU', '802Ws000001mBBuIAM', '802Ws000001mBTfIAM', '802Ws000001mBocIAE', '802Ws000001mBrrIAE', '802Ws000001mC1ZIAU', '802Ws000001mC37IAE', '802Ws000001mCZTIA2', '802Ws000001mCnuIAE', '802Ws000001mEhfIAE', '802Ws000001mFAgIAM') AND CreatedDate >= 2020-07-14T00:00:00Z AND CreatedDate < 2021-05-15T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> september
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lr1zIAA', '802Ws000001lt8ZIAQ', '802Ws000001lu1TIAQ', '802Ws000001lu31IAA', '802Ws000001lvonIAA', '802Ws000001lvwlIAA', '802Ws000001lw02IAA', '802Ws000001lwOAIAY', '802Ws000001lwRVIAY', '802Ws000001lwpiIAA', '802Ws000001lx2ZIAQ', '802Ws000001lxIiIAI', '802Ws000001ly57IAA', '802Ws000001lyWcIAI', '802Ws000001lz4MIAQ', '802Ws000001lz9CIAQ', '802Ws000001lzPFIAY', '802Ws000001lzp3IAA', '802Ws000001m0bYIAQ', '802Ws000001m0hwIAA', '802Ws000001m1CeIAI', '802Ws000001m1ZJIAY', '802Ws000001m1cVIAQ', '802Ws000001m1e0IAA', '802Ws000001m23mIAA', '802Ws000001m2GjIAI', '802Ws000001m2n2IAA', '802Ws000001m3XjIAI', '802Ws000001m4bzIAA', '802Ws000001m51eIAA', '802Ws000001m67OIAQ', '802Ws000001m6HCIAY', '802Ws000001m6LvIAI', '802Ws000001m6QmIAI', '802Ws000001m6VdIAI', '802Ws000001m6nLIAQ', '802Ws000001m76kIAA', '802Ws000001m8KUIAY', '802Ws000001m8igIAA', '802Ws000001m9GXIAY', '802Ws000001m9JlIAI', '802Ws000001mAqyIAE', '802Ws000001mAxYIAU', '802Ws000001mBBuIAM', '802Ws000001mBTfIAM', '802Ws000001mBocIAE', '802Ws000001mBrrIAE', '802Ws000001mC1ZIAU', '802Ws000001mC37IAE', '802Ws000001mCZTIA2', '802Ws000001mCnuIAE', '802Ws000001mEhfIAE', '802Ws000001mFAgIAM') AND CreatedDate >= 2020-07-14T00:00:00Z AND CreatedDate < 2021-05-14T00:00:00Z
  past_months_years = calendar -> september
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lr1zIAA', '802Ws000001lt8ZIAQ', '802Ws000001lu1TIAQ', '802Ws000001lu31IAA', '802Ws000001lvonIAA', '802Ws000001lvwlIAA', '802Ws000001lw02IAA', '802Ws000001lwOAIAY', '802Ws000001lwRVIAY', '802Ws000001lwpiIAA', '802Ws000001lx2ZIAQ', '802Ws000001lxIiIAI', '802Ws000001ly57IAA', '802Ws000001lyWcIAI', '802Ws000001lz4MIAQ', '802Ws000001lz9CIAQ', '802Ws000001lzPFIAY', '802Ws000001lzp3IAA', '802Ws000001m0bYIAQ', '802Ws000001m0hwIAA', '802Ws000001m1CeIAI', '802Ws000001m1ZJIAY', '802Ws000001m1cVIAQ', '802Ws000001m1e0IAA', '802Ws000001m23mIAA', '802Ws000001m2GjIAI', '802Ws000001m2n2IAA', '802Ws000001m3XjIAI', '802Ws000001m4bzIAA', '802Ws000001m51eIAA', '802Ws000001m67OIAQ', '802Ws000001m6HCIAY', '802Ws000001m6LvIAI', '802Ws000001m6QmIAI', '802Ws000001m6VdIAI', '802Ws000001m6nLIAQ', '802Ws000001m76kIAA', '802Ws000001m8KUIAY', '802Ws000001m8igIAA', '802Ws000001m9GXIAY', '802Ws000001m9JlIAI', '802Ws000001mAqyIAE', '802Ws000001mAxYIAU', '802Ws000001mBBuIAM', '802Ws000001mBTfIAM', '802Ws000001mBocIAE', '802Ws000001mBrrIAE', '802Ws000001mC1ZIAU', '802Ws000001mC37IAE', '802Ws000001mCZTIA2', '802Ws000001mCnuIAE', '802Ws000001mEhfIAE', '802Ws000001mFAgIAM') AND CreatedDate >= 2020-07-01T00:00:00Z AND CreatedDate < 2021-05-01T00:00:00Z
```

## original/167 (monthly_trend_analysis, right)

```
run 1: answer december (key december, right)
  own level: fail (deciding query: receipt entry 5)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT CreatedDate, ProductId FROM Case WHERE ProductId = '01tWs000002wOIYIA2' AND CreatedDate >= 2023-05-16T00:00:00Z AND CreatedDate < 2024-08-17T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT CreatedDate, ProductId FROM Case WHERE ProductId = '01tWs000002wOIYIA2' AND CreatedDate >= 2023-05-16T00:00:00Z AND CreatedDate < 2024-08-16T00:00:00Z
  past_quarters = calendar -> None
      SELECT CreatedDate, ProductId FROM Case WHERE ProductId = '01tWs000002wOIYIA2' AND CreatedDate >= 2023-04-01T00:00:00Z AND CreatedDate < 2024-07-01T00:00:00Z
run 2: answer december (key december, right)
  own level: fail (deciding query: receipt entry 3)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) 
FROM Case WHERE ProductId = '01tWs000002wOIYIA2' AND CreatedDate >= 2023-05-16T00:00:00Z AND CreatedDate < 2024-08-17T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate)
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) 
FROM Case WHERE ProductId = '01tWs000002wOIYIA2' AND CreatedDate >= 2023-05-16T00:00:00Z AND CreatedDate < 2024-08-16T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate)
  past_quarters = calendar -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) 
FROM Case WHERE ProductId = '01tWs000002wOIYIA2' AND CreatedDate >= 2023-04-01T00:00:00Z AND CreatedDate < 2024-07-01T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate)
run 3: answer december (key december, right)
  own level: pass (deciding query: receipt entry 9)
  [asked] past_quarters = rolling; rolling_end = today_counted -> december
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lyTEIAY','802Ws000001lyczIAA','802Ws000001lzFmIAI','802Ws000001lzKUIAY','802Ws000001lzScIAI','802Ws000001lzdoIAA','802Ws000001lznUIAQ','802Ws000001lzu2IAA','802Ws000001lzxDIAQ','802Ws000001m08SIAQ','802Ws000001m0EsIAI','802Ws000001m0N1IAI','802Ws000001m0RrIAI','802Ws000001m0ZvIAI','802Ws000001m0bUIAQ','802Ws000001m1m2IAA','802Ws000001m2LZIAY','802Ws000001m2TdIAI','802Ws000001m3KzIAI','802Ws000001m3hbIAA') AND CreatedDate >= 2023-05-16T00:00:00Z AND CreatedDate < 2024-08-17T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> december
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lyTEIAY','802Ws000001lyczIAA','802Ws000001lzFmIAI','802Ws000001lzKUIAY','802Ws000001lzScIAI','802Ws000001lzdoIAA','802Ws000001lznUIAQ','802Ws000001lzu2IAA','802Ws000001lzxDIAQ','802Ws000001m08SIAQ','802Ws000001m0EsIAI','802Ws000001m0N1IAI','802Ws000001m0RrIAI','802Ws000001m0ZvIAI','802Ws000001m0bUIAQ','802Ws000001m1m2IAA','802Ws000001m2LZIAY','802Ws000001m2TdIAI','802Ws000001m3KzIAI','802Ws000001m3hbIAA') AND CreatedDate >= 2023-05-16T00:00:00Z AND CreatedDate < 2024-08-16T00:00:00Z
  past_quarters = calendar -> december
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lyTEIAY','802Ws000001lyczIAA','802Ws000001lzFmIAI','802Ws000001lzKUIAY','802Ws000001lzScIAI','802Ws000001lzdoIAA','802Ws000001lznUIAQ','802Ws000001lzu2IAA','802Ws000001lzxDIAQ','802Ws000001m08SIAQ','802Ws000001m0EsIAI','802Ws000001m0N1IAI','802Ws000001m0RrIAI','802Ws000001m0ZvIAI','802Ws000001m0bUIAQ','802Ws000001m1m2IAA','802Ws000001m2LZIAY','802Ws000001m2TdIAI','802Ws000001m3KzIAI','802Ws000001m3hbIAA') AND CreatedDate >= 2023-04-01T00:00:00Z AND CreatedDate < 2024-07-01T00:00:00Z
```

## original/169 (monthly_trend_analysis, right)

```
run 1: answer august (key august, right)
  own level: fail (deciding query: receipt entry 3)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wRRhIAM' AND CreatedDate >= 2021-01-06T00:00:00Z AND CreatedDate < 2021-09-07T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wRRhIAM' AND CreatedDate >= 2021-01-06T00:00:00Z AND CreatedDate < 2021-09-06T00:00:00Z
  past_months_years = calendar -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wRRhIAM' AND CreatedDate >= 2021-01-01T00:00:00Z AND CreatedDate < 2021-09-01T00:00:00Z
run 2: answer august (key august, right)
  own level: pass (deciding query: receipt entry 6)
  [asked] past_months_years = rolling; rolling_end = today_counted -> august
      SELECT CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsUJIAY','802Ws000001lscKIAQ','802Ws000001lt8eIAA','802Ws000001ltoVIAQ','802Ws000001ltrmIAA','802Ws000001lu0LIAQ','802Ws000001luW4IAI','802Ws000001lukpIAA','802Ws000001lvbtIAA','802Ws000001lwG8IAI','802Ws000001lwhZIAQ','802Ws000001lxAcIAI','802Ws000001lxKPIAY','802Ws000001lxTzIAI','802Ws000001lxddIAA','802Ws000001ly3WIAQ','802Ws000001ly50IAA','802Ws000001ly9wIAA','802Ws000001lyZgIAI','802Ws000001lyZpIAI','802Ws000001lyzUIAQ','802Ws000001lz97IAA','802Ws000001lzKWIAY','802Ws000001lzM3IAI','802Ws000001lzicIAA','802Ws000001m0EuIAI','802Ws000001m0huIAA','802Ws000001m17jIAA','802Ws000001m1CbIAI','802Ws000001m1J3IAI','802Ws000001m1UJIAY','802Ws000001m23rIAA','802Ws000001m240IAA','802Ws000001m241IAA','802Ws000001m271IAA','802Ws000001m2F9IAI','802Ws000001m2IVIAY','802Ws000001m2ThIAI','802Ws000001m2esIAA','802Ws000001m2wfIAA') AND CreatedDate >= 2021-01-06T00:00:00Z AND CreatedDate < 2021-09-07T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> august
      SELECT CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsUJIAY','802Ws000001lscKIAQ','802Ws000001lt8eIAA','802Ws000001ltoVIAQ','802Ws000001ltrmIAA','802Ws000001lu0LIAQ','802Ws000001luW4IAI','802Ws000001lukpIAA','802Ws000001lvbtIAA','802Ws000001lwG8IAI','802Ws000001lwhZIAQ','802Ws000001lxAcIAI','802Ws000001lxKPIAY','802Ws000001lxTzIAI','802Ws000001lxddIAA','802Ws000001ly3WIAQ','802Ws000001ly50IAA','802Ws000001ly9wIAA','802Ws000001lyZgIAI','802Ws000001lyZpIAI','802Ws000001lyzUIAQ','802Ws000001lz97IAA','802Ws000001lzKWIAY','802Ws000001lzM3IAI','802Ws000001lzicIAA','802Ws000001m0EuIAI','802Ws000001m0huIAA','802Ws000001m17jIAA','802Ws000001m1CbIAI','802Ws000001m1J3IAI','802Ws000001m1UJIAY','802Ws000001m23rIAA','802Ws000001m240IAA','802Ws000001m241IAA','802Ws000001m271IAA','802Ws000001m2F9IAI','802Ws000001m2IVIAY','802Ws000001m2ThIAI','802Ws000001m2esIAA','802Ws000001m2wfIAA') AND CreatedDate >= 2021-01-06T00:00:00Z AND CreatedDate < 2021-09-06T00:00:00Z
  past_months_years = calendar -> august
      SELECT CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsUJIAY','802Ws000001lscKIAQ','802Ws000001lt8eIAA','802Ws000001ltoVIAQ','802Ws000001ltrmIAA','802Ws000001lu0LIAQ','802Ws000001luW4IAI','802Ws000001lukpIAA','802Ws000001lvbtIAA','802Ws000001lwG8IAI','802Ws000001lwhZIAQ','802Ws000001lxAcIAI','802Ws000001lxKPIAY','802Ws000001lxTzIAI','802Ws000001lxddIAA','802Ws000001ly3WIAQ','802Ws000001ly50IAA','802Ws000001ly9wIAA','802Ws000001lyZgIAI','802Ws000001lyZpIAI','802Ws000001lyzUIAQ','802Ws000001lz97IAA','802Ws000001lzKWIAY','802Ws000001lzM3IAI','802Ws000001lzicIAA','802Ws000001m0EuIAI','802Ws000001m0huIAA','802Ws000001m17jIAA','802Ws000001m1CbIAI','802Ws000001m1J3IAI','802Ws000001m1UJIAY','802Ws000001m23rIAA','802Ws000001m240IAA','802Ws000001m241IAA','802Ws000001m271IAA','802Ws000001m2F9IAI','802Ws000001m2IVIAY','802Ws000001m2ThIAI','802Ws000001m2esIAA','802Ws000001m2wfIAA') AND CreatedDate >= 2021-01-01T00:00:00Z AND CreatedDate < 2021-09-01T00:00:00Z
run 3: answer august (key august, right)
  own level: pass (deciding query: receipt entry 6)
  [asked] past_months_years = rolling; rolling_end = today_counted -> august
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsUJIAY','802Ws000001lscKIAQ','802Ws000001lt8eIAA','802Ws000001ltoVIAQ','802Ws000001ltrmIAA','802Ws000001lu0LIAQ','802Ws000001luW4IAI','802Ws000001lukpIAA','802Ws000001lvbtIAA','802Ws000001lwG8IAI','802Ws000001lwhZIAQ','802Ws000001lxAcIAI','802Ws000001lxKPIAY','802Ws000001lxTzIAI','802Ws000001lxddIAA','802Ws000001ly3WIAQ','802Ws000001ly50IAA','802Ws000001ly9wIAA','802Ws000001lyZgIAI','802Ws000001lyZpIAI') AND CreatedDate >= 2021-01-06T00:00:00Z AND CreatedDate < 2021-09-07T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> august
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsUJIAY','802Ws000001lscKIAQ','802Ws000001lt8eIAA','802Ws000001ltoVIAQ','802Ws000001ltrmIAA','802Ws000001lu0LIAQ','802Ws000001luW4IAI','802Ws000001lukpIAA','802Ws000001lvbtIAA','802Ws000001lwG8IAI','802Ws000001lwhZIAQ','802Ws000001lxAcIAI','802Ws000001lxKPIAY','802Ws000001lxTzIAI','802Ws000001lxddIAA','802Ws000001ly3WIAQ','802Ws000001ly50IAA','802Ws000001ly9wIAA','802Ws000001lyZgIAI','802Ws000001lyZpIAI') AND CreatedDate >= 2021-01-06T00:00:00Z AND CreatedDate < 2021-09-06T00:00:00Z
  past_months_years = calendar -> august
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsUJIAY','802Ws000001lscKIAQ','802Ws000001lt8eIAA','802Ws000001ltoVIAQ','802Ws000001ltrmIAA','802Ws000001lu0LIAQ','802Ws000001luW4IAI','802Ws000001lukpIAA','802Ws000001lvbtIAA','802Ws000001lwG8IAI','802Ws000001lwhZIAQ','802Ws000001lxAcIAI','802Ws000001lxKPIAY','802Ws000001lxTzIAI','802Ws000001lxddIAA','802Ws000001ly3WIAQ','802Ws000001ly50IAA','802Ws000001ly9wIAA','802Ws000001lyZgIAI','802Ws000001lyZpIAI') AND CreatedDate >= 2021-01-01T00:00:00Z AND CreatedDate < 2021-09-01T00:00:00Z
```

## original/172 (monthly_trend_analysis, right)

```
run 1: answer march (key march, right)
  own level: fail (deciding query: receipt entry 5)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT Id, CreatedDate FROM Case WHERE ProductId = '01tWs000002wQH8IAM' AND CreatedDate >= 2022-11-08T00:00:00Z AND CreatedDate < 2023-06-09T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT Id, CreatedDate FROM Case WHERE ProductId = '01tWs000002wQH8IAM' AND CreatedDate >= 2022-11-08T00:00:00Z AND CreatedDate < 2023-06-08T00:00:00Z
  past_months_years = calendar -> None
      SELECT Id, CreatedDate FROM Case WHERE ProductId = '01tWs000002wQH8IAM' AND CreatedDate >= 2022-11-01T00:00:00Z AND CreatedDate < 2023-06-01T00:00:00Z
run 2: answer march (key march, right)
  own level: fail (deciding query: receipt entry 3)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wQH8IAM' AND CreatedDate >= 2022-11-08T00:00:00Z AND CreatedDate < 2023-06-09T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wQH8IAM' AND CreatedDate >= 2022-11-08T00:00:00Z AND CreatedDate < 2023-06-08T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
  past_months_years = calendar -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wQH8IAM' AND CreatedDate >= 2022-11-01T00:00:00Z AND CreatedDate < 2023-06-01T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
run 3: answer march (key march, right)
  own level: pass (deciding query: receipt entry 8)
  [asked] past_months_years = rolling; rolling_end = today_counted -> march
      SELECT Id, CreatedDate, Subject, OrderItemId__c, IssueId__c FROM Case WHERE Id = '500Ws000007rBxWIAU' AND CreatedDate >= 2022-11-08T00:00:00Z AND CreatedDate < 2023-06-09T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> march
      SELECT Id, CreatedDate, Subject, OrderItemId__c, IssueId__c FROM Case WHERE Id = '500Ws000007rBxWIAU' AND CreatedDate >= 2022-11-08T00:00:00Z AND CreatedDate < 2023-06-08T00:00:00Z
  past_months_years = calendar -> march
      SELECT Id, CreatedDate, Subject, OrderItemId__c, IssueId__c FROM Case WHERE Id = '500Ws000007rBxWIAU' AND CreatedDate >= 2022-11-01T00:00:00Z AND CreatedDate < 2023-06-01T00:00:00Z
```

## original/183 (monthly_trend_analysis, right)

```
run 1: answer march (key march, right)
  own level: fail (deciding query: receipt entry 3)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wRxxIAE' AND CreatedDate >= 2020-01-09T00:00:00Z AND CreatedDate < 2020-09-10T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate)
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wRxxIAE' AND CreatedDate >= 2020-01-09T00:00:00Z AND CreatedDate < 2020-09-09T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate)
  past_months_years = calendar -> None
      SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wRxxIAE' AND CreatedDate >= 2020-01-01T00:00:00Z AND CreatedDate < 2020-09-01T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate)
run 2: answer march (key march, right)
  own level: fail (deciding query: receipt entry 7)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT count(Id), CALENDAR_MONTH(CreatedDate) FROM Case WHERE ProductId = '01tWs000002wRxxIAE' AND CreatedDate >= 2020-01-09T00:00:00Z AND CreatedDate < 2020-09-10T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate) ORDER BY COUNT(Id) DESC
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT count(Id), CALENDAR_MONTH(CreatedDate) FROM Case WHERE ProductId = '01tWs000002wRxxIAE' AND CreatedDate >= 2020-01-09T00:00:00Z AND CreatedDate < 2020-09-09T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate) ORDER BY COUNT(Id) DESC
  past_months_years = calendar -> None
      SELECT count(Id), CALENDAR_MONTH(CreatedDate) FROM Case WHERE ProductId = '01tWs000002wRxxIAE' AND CreatedDate >= 2020-01-01T00:00:00Z AND CreatedDate < 2020-09-01T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate) ORDER BY COUNT(Id) DESC
run 3: answer march (key march, right)
  own level: pass (deciding query: receipt entry 5)
  [asked] past_months_years = rolling; rolling_end = today_counted -> march
      SELECT Id, CreatedDate, OrderItemId__c, Subject FROM Case WHERE OrderItemId__c IN ('802Ws000001lvHGIAY', '802Ws000001lvgdIAA', '802Ws000001m0QEIAY', '802Ws000001m1MEIAY', '802Ws000001m28cIAA', '802Ws000001m3krIAA', '802Ws000001m4OzIAI', '802Ws000001m4jwIAA', '802Ws000001m5ufIAA', '802Ws000001m6ykIAA', '802Ws000001m70EIAQ', '802Ws000001m7WWIAY', '802Ws000001m8CUIAY', '802Ws000001m8lwIAA', '802Ws000001mBIMIA2', '802Ws000001mBbmIAE', '802Ws000001mCT2IAM', '802Ws000001mCpWIAU', '802Ws000001mEWNIA2', '802Ws000001mEhgIAE') AND CreatedDate >= 2020-01-09T00:00:00Z AND CreatedDate < 2020-09-10T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> march
      SELECT Id, CreatedDate, OrderItemId__c, Subject FROM Case WHERE OrderItemId__c IN ('802Ws000001lvHGIAY', '802Ws000001lvgdIAA', '802Ws000001m0QEIAY', '802Ws000001m1MEIAY', '802Ws000001m28cIAA', '802Ws000001m3krIAA', '802Ws000001m4OzIAI', '802Ws000001m4jwIAA', '802Ws000001m5ufIAA', '802Ws000001m6ykIAA', '802Ws000001m70EIAQ', '802Ws000001m7WWIAY', '802Ws000001m8CUIAY', '802Ws000001m8lwIAA', '802Ws000001mBIMIA2', '802Ws000001mBbmIAE', '802Ws000001mCT2IAM', '802Ws000001mCpWIAU', '802Ws000001mEWNIA2', '802Ws000001mEhgIAE') AND CreatedDate >= 2020-01-09T00:00:00Z AND CreatedDate < 2020-09-09T00:00:00Z
  past_months_years = calendar -> march
      SELECT Id, CreatedDate, OrderItemId__c, Subject FROM Case WHERE OrderItemId__c IN ('802Ws000001lvHGIAY', '802Ws000001lvgdIAA', '802Ws000001m0QEIAY', '802Ws000001m1MEIAY', '802Ws000001m28cIAA', '802Ws000001m3krIAA', '802Ws000001m4OzIAI', '802Ws000001m4jwIAA', '802Ws000001m5ufIAA', '802Ws000001m6ykIAA', '802Ws000001m70EIAQ', '802Ws000001m7WWIAY', '802Ws000001m8CUIAY', '802Ws000001m8lwIAA', '802Ws000001mBIMIA2', '802Ws000001mBbmIAE', '802Ws000001mCT2IAM', '802Ws000001mCpWIAU', '802Ws000001mEWNIA2', '802Ws000001mEhgIAE') AND CreatedDate >= 2020-01-01T00:00:00Z AND CreatedDate < 2020-09-01T00:00:00Z
```

## original/184 (monthly_trend_analysis, right)

```
run 1: answer december (key december, right)
  not checked: no applicable query
run 2: answer december (key december, right)
  own level: pass (deciding query: receipt entry 10)
  [asked] past_quarters = rolling; rolling_end = today_counted -> december
      SELECT CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lupPIAQ','802Ws000001lur1IAA','802Ws000001lwOCIAY','802Ws000001lwXuIAI','802Ws000001lwZgIAI','802Ws000001lweKIAQ','802Ws000001lwjKIAQ','802Ws000001lwo6IAA','802Ws000001lwrFIAQ','802Ws000001lx2cIAA','802Ws000001lxKGIAY','802Ws000001lxQfIAI','802Ws000001lxaLIAQ','802Ws000001lxqTIAQ','802Ws000001ly4zIAA','802Ws000001lyD5IAI','802Ws000001lyGMIAY','802Ws000001lyGOIAY','802Ws000001lyLBIAY','802Ws000001lz2gIAA','802Ws000001lzxCIAQ','802Ws000001m03jIAA','802Ws000001m0BeIAI','802Ws000001m0uoIAA','802Ws000001m166IAA','802Ws000001m17hIAA','802Ws000001m1MDIAY','802Ws000001m1SiIAI','802Ws000001m1dxIAA','802Ws000001m1qrIAA','802Ws000001m1vhIAA','802Ws000001m2QNIAY','802Ws000001m2VFIAY','802Ws000001m2i6IAA','802Ws000001m2v2IAA','802Ws000001m3RFIAY','802Ws000001m3XiIAI','802Ws000001m3pbIAA','802Ws000001m4OwIAI','802Ws000001m4YeIAI','802Ws000001m4aGIAQ','802Ws000001m4aHIAQ','802Ws000001m5MeIAI','802Ws000001m5eWIAQ','802Ws000001m5pdIAA','802Ws000001m5rIIAQ','802Ws000001m6NaIAI','802Ws000001m6TyIAI','802Ws000001m6YxIAI','802Ws000001m7JhIAI','802Ws000001m7MnIAI','802Ws000001m9DJIAY','802Ws000001mAxNIAU','802Ws000001mDgkIAE','802Ws000001mDjxIAE') AND CreatedDate >= 2023-08-09T00:00:00Z AND CreatedDate < 2024-11-10T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> december
      SELECT CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lupPIAQ','802Ws000001lur1IAA','802Ws000001lwOCIAY','802Ws000001lwXuIAI','802Ws000001lwZgIAI','802Ws000001lweKIAQ','802Ws000001lwjKIAQ','802Ws000001lwo6IAA','802Ws000001lwrFIAQ','802Ws000001lx2cIAA','802Ws000001lxKGIAY','802Ws000001lxQfIAI','802Ws000001lxaLIAQ','802Ws000001lxqTIAQ','802Ws000001ly4zIAA','802Ws000001lyD5IAI','802Ws000001lyGMIAY','802Ws000001lyGOIAY','802Ws000001lyLBIAY','802Ws000001lz2gIAA','802Ws000001lzxCIAQ','802Ws000001m03jIAA','802Ws000001m0BeIAI','802Ws000001m0uoIAA','802Ws000001m166IAA','802Ws000001m17hIAA','802Ws000001m1MDIAY','802Ws000001m1SiIAI','802Ws000001m1dxIAA','802Ws000001m1qrIAA','802Ws000001m1vhIAA','802Ws000001m2QNIAY','802Ws000001m2VFIAY','802Ws000001m2i6IAA','802Ws000001m2v2IAA','802Ws000001m3RFIAY','802Ws000001m3XiIAI','802Ws000001m3pbIAA','802Ws000001m4OwIAI','802Ws000001m4YeIAI','802Ws000001m4aGIAQ','802Ws000001m4aHIAQ','802Ws000001m5MeIAI','802Ws000001m5eWIAQ','802Ws000001m5pdIAA','802Ws000001m5rIIAQ','802Ws000001m6NaIAI','802Ws000001m6TyIAI','802Ws000001m6YxIAI','802Ws000001m7JhIAI','802Ws000001m7MnIAI','802Ws000001m9DJIAY','802Ws000001mAxNIAU','802Ws000001mDgkIAE','802Ws000001mDjxIAE') AND CreatedDate >= 2023-08-09T00:00:00Z AND CreatedDate < 2024-11-09T00:00:00Z
  past_quarters = calendar -> december
      SELECT CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lupPIAQ','802Ws000001lur1IAA','802Ws000001lwOCIAY','802Ws000001lwXuIAI','802Ws000001lwZgIAI','802Ws000001lweKIAQ','802Ws000001lwjKIAQ','802Ws000001lwo6IAA','802Ws000001lwrFIAQ','802Ws000001lx2cIAA','802Ws000001lxKGIAY','802Ws000001lxQfIAI','802Ws000001lxaLIAQ','802Ws000001lxqTIAQ','802Ws000001ly4zIAA','802Ws000001lyD5IAI','802Ws000001lyGMIAY','802Ws000001lyGOIAY','802Ws000001lyLBIAY','802Ws000001lz2gIAA','802Ws000001lzxCIAQ','802Ws000001m03jIAA','802Ws000001m0BeIAI','802Ws000001m0uoIAA','802Ws000001m166IAA','802Ws000001m17hIAA','802Ws000001m1MDIAY','802Ws000001m1SiIAI','802Ws000001m1dxIAA','802Ws000001m1qrIAA','802Ws000001m1vhIAA','802Ws000001m2QNIAY','802Ws000001m2VFIAY','802Ws000001m2i6IAA','802Ws000001m2v2IAA','802Ws000001m3RFIAY','802Ws000001m3XiIAI','802Ws000001m3pbIAA','802Ws000001m4OwIAI','802Ws000001m4YeIAI','802Ws000001m4aGIAQ','802Ws000001m4aHIAQ','802Ws000001m5MeIAI','802Ws000001m5eWIAQ','802Ws000001m5pdIAA','802Ws000001m5rIIAQ','802Ws000001m6NaIAI','802Ws000001m6TyIAI','802Ws000001m6YxIAI','802Ws000001m7JhIAI','802Ws000001m7MnIAI','802Ws000001m9DJIAY','802Ws000001mAxNIAU','802Ws000001mDgkIAE','802Ws000001mDjxIAE') AND CreatedDate >= 2023-07-01T00:00:00Z AND CreatedDate < 2024-10-01T00:00:00Z
run 3: answer december (key december, right)
  own level: pass (deciding query: receipt entry 9)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT OrderItemId__c, CreatedDate FROM Case WHERE OrderItemId__c IN ('802Ws000001m4aGIAQ','802Ws000001m4aHIAQ','802Ws000001m5MeIAI','802Ws000001m5eWIAQ','802Ws000001m5pdIAA','802Ws000001m5rIIAQ','802Ws000001m6NaIAI','802Ws000001m6TyIAI','802Ws000001m6YxIAI','802Ws000001m7JhIAI','802Ws000001m7MnIAI','802Ws000001m9DJIAY','802Ws000001mAxNIAU','802Ws000001mDgkIAE','802Ws000001mDjxIAE') AND CreatedDate >= 2023-08-09T00:00:00Z AND CreatedDate < 2024-11-10T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT OrderItemId__c, CreatedDate FROM Case WHERE OrderItemId__c IN ('802Ws000001m4aGIAQ','802Ws000001m4aHIAQ','802Ws000001m5MeIAI','802Ws000001m5eWIAQ','802Ws000001m5pdIAA','802Ws000001m5rIIAQ','802Ws000001m6NaIAI','802Ws000001m6TyIAI','802Ws000001m6YxIAI','802Ws000001m7JhIAI','802Ws000001m7MnIAI','802Ws000001m9DJIAY','802Ws000001mAxNIAU','802Ws000001mDgkIAE','802Ws000001mDjxIAE') AND CreatedDate >= 2023-08-09T00:00:00Z AND CreatedDate < 2024-11-09T00:00:00Z
  past_quarters = calendar -> None
      SELECT OrderItemId__c, CreatedDate FROM Case WHERE OrderItemId__c IN ('802Ws000001m4aGIAQ','802Ws000001m4aHIAQ','802Ws000001m5MeIAI','802Ws000001m5eWIAQ','802Ws000001m5pdIAA','802Ws000001m5rIIAQ','802Ws000001m6NaIAI','802Ws000001m6TyIAI','802Ws000001m6YxIAI','802Ws000001m7JhIAI','802Ws000001m7MnIAI','802Ws000001m9DJIAY','802Ws000001mAxNIAU','802Ws000001mDgkIAE','802Ws000001mDjxIAE') AND CreatedDate >= 2023-07-01T00:00:00Z AND CreatedDate < 2024-10-01T00:00:00Z
```

## original/194 (monthly_trend_analysis, right)

```
run 1: answer august (key august, right)
  own level: fail (deciding query: receipt entry 3)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wRptIAE' AND CreatedDate >= 2021-01-17T00:00:00Z AND CreatedDate < 2021-10-18T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate)
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wRptIAE' AND CreatedDate >= 2021-01-17T00:00:00Z AND CreatedDate < 2021-10-17T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate)
  past_months_years = calendar -> None
      SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wRptIAE' AND CreatedDate >= 2021-01-01T00:00:00Z AND CreatedDate < 2021-10-01T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate)
run 2: answer august (key august, right)
  own level: pass (deciding query: receipt entry 6)
  [asked] past_months_years = rolling; rolling_end = today_counted -> august
      SELECT CreatedDate, OrderItemId__c FROM Case WHERE CreatedDate >= 2021-01-17T00:00:00Z AND CreatedDate < 2021-10-18T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> august
      SELECT CreatedDate, OrderItemId__c FROM Case WHERE CreatedDate >= 2021-01-17T00:00:00Z AND CreatedDate < 2021-10-17T00:00:00Z
  past_months_years = calendar -> august
      SELECT CreatedDate, OrderItemId__c FROM Case WHERE CreatedDate >= 2021-01-01T00:00:00Z AND CreatedDate < 2021-10-01T00:00:00Z
run 3: answer august (key august, right)
  own level: pass (deciding query: receipt entry 10)
  [asked] past_months_years = rolling; rolling_end = today_counted -> august
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001m3uJIAQ','802Ws000001m3uPIAQ','802Ws000001m4FMIAY','802Ws000001m4NOIAY','802Ws000001m4gkIAA','802Ws000001m4olIAA','802Ws000001m5JQIAY','802Ws000001m5JSIAY','802Ws000001m5OGIAY','802Ws000001m5UgIAI','802Ws000001m5hfIAA','802Ws000001m64DIAQ','802Ws000001m6AjIAI','802Ws000001m6FVIAY','802Ws000001m6FYIAY','802Ws000001m70FIAQ','802Ws000001m7OTIAY','802Ws000001m7gCIAQ','802Ws000001m84QIAQ','802Ws000001m862IAA','802Ws000001m8SkIAI','802Ws000001m8UNIAY','802Ws000001m8kHIAQ','802Ws000001m8nXIAQ','802Ws000001m9F3IAI','802Ws000001m9oRIAQ','802Ws000001m9zqIAA','802Ws000001mAXZIA2','802Ws000001mB76IAE','802Ws000001mBDbIAM','802Ws000001mBVGIA2','802Ws000001mBYgIAM','802Ws000001mCHlIAM','802Ws000001mCHoIAM','802Ws000001mDtjIAE','802Ws000001mEUjIAM','802Ws000001mFyfIAE') AND CreatedDate >= 2021-01-17T00:00:00Z AND CreatedDate < 2021-10-18T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> august
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001m3uJIAQ','802Ws000001m3uPIAQ','802Ws000001m4FMIAY','802Ws000001m4NOIAY','802Ws000001m4gkIAA','802Ws000001m4olIAA','802Ws000001m5JQIAY','802Ws000001m5JSIAY','802Ws000001m5OGIAY','802Ws000001m5UgIAI','802Ws000001m5hfIAA','802Ws000001m64DIAQ','802Ws000001m6AjIAI','802Ws000001m6FVIAY','802Ws000001m6FYIAY','802Ws000001m70FIAQ','802Ws000001m7OTIAY','802Ws000001m7gCIAQ','802Ws000001m84QIAQ','802Ws000001m862IAA','802Ws000001m8SkIAI','802Ws000001m8UNIAY','802Ws000001m8kHIAQ','802Ws000001m8nXIAQ','802Ws000001m9F3IAI','802Ws000001m9oRIAQ','802Ws000001m9zqIAA','802Ws000001mAXZIA2','802Ws000001mB76IAE','802Ws000001mBDbIAM','802Ws000001mBVGIA2','802Ws000001mBYgIAM','802Ws000001mCHlIAM','802Ws000001mCHoIAM','802Ws000001mDtjIAE','802Ws000001mEUjIAM','802Ws000001mFyfIAE') AND CreatedDate >= 2021-01-17T00:00:00Z AND CreatedDate < 2021-10-17T00:00:00Z
  past_months_years = calendar -> august
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001m3uJIAQ','802Ws000001m3uPIAQ','802Ws000001m4FMIAY','802Ws000001m4NOIAY','802Ws000001m4gkIAA','802Ws000001m4olIAA','802Ws000001m5JQIAY','802Ws000001m5JSIAY','802Ws000001m5OGIAY','802Ws000001m5UgIAI','802Ws000001m5hfIAA','802Ws000001m64DIAQ','802Ws000001m6AjIAI','802Ws000001m6FVIAY','802Ws000001m6FYIAY','802Ws000001m70FIAQ','802Ws000001m7OTIAY','802Ws000001m7gCIAQ','802Ws000001m84QIAQ','802Ws000001m862IAA','802Ws000001m8SkIAI','802Ws000001m8UNIAY','802Ws000001m8kHIAQ','802Ws000001m8nXIAQ','802Ws000001m9F3IAI','802Ws000001m9oRIAQ','802Ws000001m9zqIAA','802Ws000001mAXZIA2','802Ws000001mB76IAE','802Ws000001mBDbIAM','802Ws000001mBVGIA2','802Ws000001mBYgIAM','802Ws000001mCHlIAM','802Ws000001mCHoIAM','802Ws000001mDtjIAE','802Ws000001mEUjIAM','802Ws000001mFyfIAE') AND CreatedDate >= 2021-01-01T00:00:00Z AND CreatedDate < 2021-10-01T00:00:00Z
```

## original/198 (monthly_trend_analysis, right)

```
run 1: answer march (key march, right)
  not checked: no applicable query
run 2: answer march (key march, right)
  own level: fail (deciding query: receipt entry 3)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT COUNT(Id), CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) FROM Case WHERE ProductId = '01tWs000002wSafIAE' AND CreatedDate >= 2022-11-20T00:00:00Z AND CreatedDate < 2023-08-21T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate) ASC, CALENDAR_MONTH(CreatedDate) ASC
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT COUNT(Id), CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) FROM Case WHERE ProductId = '01tWs000002wSafIAE' AND CreatedDate >= 2022-11-20T00:00:00Z AND CreatedDate < 2023-08-20T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate) ASC, CALENDAR_MONTH(CreatedDate) ASC
  past_months_years = calendar -> None
      SELECT COUNT(Id), CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) FROM Case WHERE ProductId = '01tWs000002wSafIAE' AND CreatedDate >= 2022-11-01T00:00:00Z AND CreatedDate < 2023-08-01T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate) ASC, CALENDAR_MONTH(CreatedDate) ASC
run 3: answer march (key march, right)
  own level: pass (deciding query: receipt entry 6)
  [asked] past_months_years = rolling; rolling_end = today_counted -> march
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE CreatedDate >= 2022-11-20T00:00:00Z AND CreatedDate < 2023-08-21T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> march
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE CreatedDate >= 2022-11-20T00:00:00Z AND CreatedDate < 2023-08-20T00:00:00Z
  past_months_years = calendar -> march
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE CreatedDate >= 2022-11-01T00:00:00Z AND CreatedDate < 2023-08-01T00:00:00Z
```

## original/215 (monthly_trend_analysis, right)

```
run 1: answer december (key december, right)
  own level: fail (deciding query: receipt entry 3)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wSu1IAE' AND CreatedDate >= 2023-07-19T00:00:00Z AND CreatedDate < 2024-07-20T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate)
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wSu1IAE' AND CreatedDate >= 2023-07-19T00:00:00Z AND CreatedDate < 2024-07-19T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate)
  past_quarters = calendar -> None
      SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wSu1IAE' AND CreatedDate >= 2023-07-01T00:00:00Z AND CreatedDate < 2024-07-01T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate)
run 2: answer december (key december, right)
  own level: fail (deciding query: receipt entry 8)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT CreatedDate, ProductId FROM Case WHERE ProductId = '01tWs000002wSu1IAE' AND CreatedDate >= 2023-07-19T00:00:00Z AND CreatedDate < 2024-07-20T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT CreatedDate, ProductId FROM Case WHERE ProductId = '01tWs000002wSu1IAE' AND CreatedDate >= 2023-07-19T00:00:00Z AND CreatedDate < 2024-07-19T00:00:00Z
  past_quarters = calendar -> None
      SELECT CreatedDate, ProductId FROM Case WHERE ProductId = '01tWs000002wSu1IAE' AND CreatedDate >= 2023-07-01T00:00:00Z AND CreatedDate < 2024-07-01T00:00:00Z
run 3: answer december (key december, right)
  own level: fail (deciding query: receipt entry 10)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT Id, CreatedDate, ProductId FROM Case WHERE ProductId = '01tWs000002wSu1IAE' AND CreatedDate >= 2023-07-19T00:00:00Z AND CreatedDate < 2024-07-20T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT Id, CreatedDate, ProductId FROM Case WHERE ProductId = '01tWs000002wSu1IAE' AND CreatedDate >= 2023-07-19T00:00:00Z AND CreatedDate < 2024-07-19T00:00:00Z
  past_quarters = calendar -> None
      SELECT Id, CreatedDate, ProductId FROM Case WHERE ProductId = '01tWs000002wSu1IAE' AND CreatedDate >= 2023-07-01T00:00:00Z AND CreatedDate < 2024-07-01T00:00:00Z
```

## original/230 (monthly_trend_analysis, right)

```
run 1: answer december (key december, right)
  own level: fail (deciding query: receipt entry 10)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wNr9IAE' AND CreatedDate >= 2020-01-20T00:00:00Z AND CreatedDate < 2020-12-21T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wNr9IAE' AND CreatedDate >= 2020-01-20T00:00:00Z AND CreatedDate < 2020-12-20T00:00:00Z
  past_months_years = calendar -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wNr9IAE' AND CreatedDate >= 2020-01-01T00:00:00Z AND CreatedDate < 2020-12-01T00:00:00Z
run 2: answer december (key december, right)
  own level: pass (deciding query: receipt entry 7)
  [asked] past_months_years = rolling; rolling_end = today_counted -> december
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE CreatedDate >= 2020-01-20T00:00:00Z AND CreatedDate < 2020-12-21T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> december
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE CreatedDate >= 2020-01-20T00:00:00Z AND CreatedDate < 2020-12-20T00:00:00Z
  past_months_years = calendar -> None
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE CreatedDate >= 2020-01-01T00:00:00Z AND CreatedDate < 2020-12-01T00:00:00Z
run 3: answer december (key december, right)
  own level: pass (deciding query: receipt entry 6)
  [asked] past_months_years = rolling; rolling_end = today_counted -> december
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001m2OmIAI', '802Ws000001m3ROIAY', '802Ws000001m3cYIAQ', '802Ws000001m3caIAA', '802Ws000001m3z9IAA', '802Ws000001m4dVIAQ', '802Ws000001m4s2IAA', '802Ws000001m5HpIAI', '802Ws000001m6cAIAQ', '802Ws000001m7EtIAI', '802Ws000001m7rRIAQ', '802Ws000001m7zhIAA', '802Ws000001m82uIAA', '802Ws000001m85xIAA', '802Ws000001m90RIAQ', '802Ws000001m9dAIAQ', '802Ws000001m9rdIAA', '802Ws000001mAxQIAU', '802Ws000001mCHjIAM', '802Ws000001mCJHIA2', '802Ws000001mEGDIA2') AND CreatedDate >= 2020-01-20T00:00:00Z AND CreatedDate < 2020-12-21T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> december
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001m2OmIAI', '802Ws000001m3ROIAY', '802Ws000001m3cYIAQ', '802Ws000001m3caIAA', '802Ws000001m3z9IAA', '802Ws000001m4dVIAQ', '802Ws000001m4s2IAA', '802Ws000001m5HpIAI', '802Ws000001m6cAIAQ', '802Ws000001m7EtIAI', '802Ws000001m7rRIAQ', '802Ws000001m7zhIAA', '802Ws000001m82uIAA', '802Ws000001m85xIAA', '802Ws000001m90RIAQ', '802Ws000001m9dAIAQ', '802Ws000001m9rdIAA', '802Ws000001mAxQIAU', '802Ws000001mCHjIAM', '802Ws000001mCJHIA2', '802Ws000001mEGDIA2') AND CreatedDate >= 2020-01-20T00:00:00Z AND CreatedDate < 2020-12-20T00:00:00Z
  past_months_years = calendar -> None
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001m2OmIAI', '802Ws000001m3ROIAY', '802Ws000001m3cYIAQ', '802Ws000001m3caIAA', '802Ws000001m3z9IAA', '802Ws000001m4dVIAQ', '802Ws000001m4s2IAA', '802Ws000001m5HpIAI', '802Ws000001m6cAIAQ', '802Ws000001m7EtIAI', '802Ws000001m7rRIAQ', '802Ws000001m7zhIAA', '802Ws000001m82uIAA', '802Ws000001m85xIAA', '802Ws000001m90RIAQ', '802Ws000001m9dAIAQ', '802Ws000001m9rdIAA', '802Ws000001mAxQIAU', '802Ws000001mCHjIAM', '802Ws000001mCJHIA2', '802Ws000001mEGDIA2') AND CreatedDate >= 2020-01-01T00:00:00Z AND CreatedDate < 2020-12-01T00:00:00Z
```

## original/242 (monthly_trend_analysis, right)

```
run 1: answer september (key september, right)
  own level: fail (deciding query: receipt entry 3)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wSHJIA2' AND CreatedDate >= 2020-05-27T00:00:00Z AND CreatedDate < 2021-11-28T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wSHJIA2' AND CreatedDate >= 2020-05-27T00:00:00Z AND CreatedDate < 2021-11-27T00:00:00Z
  past_quarters = calendar -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wSHJIA2' AND CreatedDate >= 2020-04-01T00:00:00Z AND CreatedDate < 2021-10-01T00:00:00Z
run 2: answer september (key september, right)
  own level: fail (deciding query: receipt entry 6)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wSHJIA2' AND CreatedDate >= 2020-05-27T00:00:00Z AND CreatedDate < 2021-11-28T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate)
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wSHJIA2' AND CreatedDate >= 2020-05-27T00:00:00Z AND CreatedDate < 2021-11-27T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate)
  past_quarters = calendar -> None
      SELECT CALENDAR_MONTH(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wSHJIA2' AND CreatedDate >= 2020-04-01T00:00:00Z AND CreatedDate < 2021-10-01T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate)
run 3: answer september (key september, right)
  own level: pass (deciding query: receipt entry 4)
  [asked] past_quarters = rolling; rolling_end = today_counted -> september
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lx7OIAQ','802Ws000001lxyfIAA','802Ws000001lyLCIAY','802Ws000001lzDyIAI','802Ws000001lzSTIAY','802Ws000001m03ZIAQ','802Ws000001m5HvIAI','802Ws000001m5RVIAY','802Ws000001m73ZIAQ') AND CreatedDate >= 2020-05-27T00:00:00Z AND CreatedDate < 2021-11-28T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> september
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lx7OIAQ','802Ws000001lxyfIAA','802Ws000001lyLCIAY','802Ws000001lzDyIAI','802Ws000001lzSTIAY','802Ws000001m03ZIAQ','802Ws000001m5HvIAI','802Ws000001m5RVIAY','802Ws000001m73ZIAQ') AND CreatedDate >= 2020-05-27T00:00:00Z AND CreatedDate < 2021-11-27T00:00:00Z
  past_quarters = calendar -> september
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lx7OIAQ','802Ws000001lxyfIAA','802Ws000001lyLCIAY','802Ws000001lzDyIAI','802Ws000001lzSTIAY','802Ws000001m03ZIAQ','802Ws000001m5HvIAI','802Ws000001m5RVIAY','802Ws000001m73ZIAQ') AND CreatedDate >= 2020-04-01T00:00:00Z AND CreatedDate < 2021-10-01T00:00:00Z
```

## original/244 (monthly_trend_analysis, wrong)

```
run 1: answer None (key august, wrong)
  own level: pass (deciding query: receipt entry 3)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wRl4IAE' AND CreatedDate >= 2023-07-11T00:00:00Z AND CreatedDate < 2024-06-12T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wRl4IAE' AND CreatedDate >= 2023-07-11T00:00:00Z AND CreatedDate < 2024-06-11T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
  past_months_years = calendar -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) FROM Case WHERE ProductId = '01tWs000002wRl4IAE' AND CreatedDate >= 2023-07-01T00:00:00Z AND CreatedDate < 2024-06-01T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
run 2: answer None (key august, wrong)
  own level: pass (deciding query: receipt entry 5)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) 
FROM Case WHERE ProductId = '01tWs000002wRl4IAE' AND CreatedDate >= 2023-07-11T00:00:00Z AND CreatedDate < 2024-06-12T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) 
FROM Case WHERE ProductId = '01tWs000002wRl4IAE' AND CreatedDate >= 2023-07-11T00:00:00Z AND CreatedDate < 2024-06-11T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
  past_months_years = calendar -> None
      SELECT CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate), COUNT(Id) 
FROM Case WHERE ProductId = '01tWs000002wRl4IAE' AND CreatedDate >= 2023-07-01T00:00:00Z AND CreatedDate < 2024-06-01T00:00:00Z GROUP BY CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate) ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
run 3: answer None (key august, wrong)
  own level: fail (deciding query: receipt entry 8)
  [asked] past_months_years = rolling; rolling_end = today_counted -> august
      SELECT Id, Subject, OrderItemId__c, CreatedDate FROM Case WHERE (Subject LIKE '%Velocity%' OR Subject LIKE '%Cleats%') AND CreatedDate >= 2023-07-11T00:00:00Z AND CreatedDate < 2024-06-12T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> august
      SELECT Id, Subject, OrderItemId__c, CreatedDate FROM Case WHERE (Subject LIKE '%Velocity%' OR Subject LIKE '%Cleats%') AND CreatedDate >= 2023-07-11T00:00:00Z AND CreatedDate < 2024-06-11T00:00:00Z
  past_months_years = calendar -> august
      SELECT Id, Subject, OrderItemId__c, CreatedDate FROM Case WHERE (Subject LIKE '%Velocity%' OR Subject LIKE '%Cleats%') AND CreatedDate >= 2023-07-01T00:00:00Z AND CreatedDate < 2024-06-01T00:00:00Z
```

## original/248 (monthly_trend_analysis, right)

```
run 1: answer october (key october, right)
  own level: fail (deciding query: receipt entry 5)
  [asked] past_months_years = rolling; rolling_end = today_counted -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wTgPIAU' AND CreatedDate >= 2021-07-26T00:00:00Z AND CreatedDate < 2022-03-27T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wTgPIAU' AND CreatedDate >= 2021-07-26T00:00:00Z AND CreatedDate < 2022-03-26T00:00:00Z
  past_months_years = calendar -> None
      SELECT CreatedDate FROM Case WHERE ProductId = '01tWs000002wTgPIAU' AND CreatedDate >= 2021-07-01T00:00:00Z AND CreatedDate < 2022-03-01T00:00:00Z
run 2: answer october (key october, right)
  not checked: no applicable query
run 3: answer october (key october, right)
  own level: pass (deciding query: receipt entry 6)
  [asked] past_months_years = rolling; rolling_end = today_counted -> october
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lqFbIAI','802Ws000001lttrIAA','802Ws000001lwrSIAQ','802Ws000001lxleIAA','802Ws000001lyQ6IAI','802Ws000001lyudIAA','802Ws000001lzEGIAY','802Ws000001m0TVIAY','802Ws000001m0uyIAA','802Ws000001m1EIIAY','802Ws000001m1FmIAI','802Ws000001m1viIAA','802Ws000001m2gWIAQ','802Ws000001m3j0IAA','802Ws000001m3kqIAA','802Ws000001m4FRIAY','802Ws000001m5ElIAI','802Ws000001m5HlIAI','802Ws000001m5KzIAI','802Ws000001m5WJIAY','802Ws000001m6fRIAQ','802Ws000001m8z0IAA','802Ws000001m9OdIAI','802Ws000001m9WlIAI','802Ws000001mAEEIA2','802Ws000001mBLcIAM','802Ws000001mBTdIAM','802Ws000001mC4pIAE','802Ws000001mDIXIA2','802Ws000001mDdXIAU','802Ws000001mEPtIAM') AND CreatedDate >= 2021-07-26T00:00:00Z AND CreatedDate < 2022-03-27T00:00:00Z
  [asked] past_months_years = rolling; rolling_end = today_not_counted -> october
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lqFbIAI','802Ws000001lttrIAA','802Ws000001lwrSIAQ','802Ws000001lxleIAA','802Ws000001lyQ6IAI','802Ws000001lyudIAA','802Ws000001lzEGIAY','802Ws000001m0TVIAY','802Ws000001m0uyIAA','802Ws000001m1EIIAY','802Ws000001m1FmIAI','802Ws000001m1viIAA','802Ws000001m2gWIAQ','802Ws000001m3j0IAA','802Ws000001m3kqIAA','802Ws000001m4FRIAY','802Ws000001m5ElIAI','802Ws000001m5HlIAI','802Ws000001m5KzIAI','802Ws000001m5WJIAY','802Ws000001m6fRIAQ','802Ws000001m8z0IAA','802Ws000001m9OdIAI','802Ws000001m9WlIAI','802Ws000001mAEEIA2','802Ws000001mBLcIAM','802Ws000001mBTdIAM','802Ws000001mC4pIAE','802Ws000001mDIXIA2','802Ws000001mDdXIAU','802Ws000001mEPtIAM') AND CreatedDate >= 2021-07-26T00:00:00Z AND CreatedDate < 2022-03-26T00:00:00Z
  past_months_years = calendar -> october
      SELECT Id, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lqFbIAI','802Ws000001lttrIAA','802Ws000001lwrSIAQ','802Ws000001lxleIAA','802Ws000001lyQ6IAI','802Ws000001lyudIAA','802Ws000001lzEGIAY','802Ws000001m0TVIAY','802Ws000001m0uyIAA','802Ws000001m1EIIAY','802Ws000001m1FmIAI','802Ws000001m1viIAA','802Ws000001m2gWIAQ','802Ws000001m3j0IAA','802Ws000001m3kqIAA','802Ws000001m4FRIAY','802Ws000001m5ElIAI','802Ws000001m5HlIAI','802Ws000001m5KzIAI','802Ws000001m5WJIAY','802Ws000001m6fRIAQ','802Ws000001m8z0IAA','802Ws000001m9OdIAI','802Ws000001m9WlIAI','802Ws000001mAEEIA2','802Ws000001mBLcIAM','802Ws000001mBTdIAM','802Ws000001mC4pIAE','802Ws000001mDIXIA2','802Ws000001mDdXIAU','802Ws000001mEPtIAM') AND CreatedDate >= 2021-07-01T00:00:00Z AND CreatedDate < 2022-03-01T00:00:00Z
```

## original/257 (monthly_trend_analysis, right)

```
run 1: answer january (key january, right)
  own level: fail (deciding query: receipt entry 5)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT Id, CreatedDate FROM Case WHERE ProductId = '01tWs000002wNw0IAE' AND CreatedDate >= 2019-08-02T00:00:00Z AND CreatedDate < 2020-08-03T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT Id, CreatedDate FROM Case WHERE ProductId = '01tWs000002wNw0IAE' AND CreatedDate >= 2019-08-02T00:00:00Z AND CreatedDate < 2020-08-02T00:00:00Z
  past_quarters = calendar -> None
      SELECT Id, CreatedDate FROM Case WHERE ProductId = '01tWs000002wNw0IAE' AND CreatedDate >= 2019-07-01T00:00:00Z AND CreatedDate < 2020-07-01T00:00:00Z
run 2: answer january (key january, right)
  not checked: no applicable query
run 3: answer january (key january, right)
  own level: pass (deciding query: receipt entry 9)
  [asked] past_quarters = rolling; rolling_end = today_counted -> january
      SELECT Id, CreatedDate, OrderItemId__c, Subject, Description FROM Case WHERE OrderItemId__c IN ('802Ws000001lscLIAQ', '802Ws000001lvn7IAA', '802Ws000001lyBcIAI', '802Ws000001m0MyIAI', '802Ws000001m2bpIAA', '802Ws000001m5XtIAI', '802Ws000001mBn6IAE', '802Ws000001mCzFIAU', '802Ws000001mD8vIAE') AND CreatedDate >= 2019-08-02T00:00:00Z AND CreatedDate < 2020-08-03T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> january
      SELECT Id, CreatedDate, OrderItemId__c, Subject, Description FROM Case WHERE OrderItemId__c IN ('802Ws000001lscLIAQ', '802Ws000001lvn7IAA', '802Ws000001lyBcIAI', '802Ws000001m0MyIAI', '802Ws000001m2bpIAA', '802Ws000001m5XtIAI', '802Ws000001mBn6IAE', '802Ws000001mCzFIAU', '802Ws000001mD8vIAE') AND CreatedDate >= 2019-08-02T00:00:00Z AND CreatedDate < 2020-08-02T00:00:00Z
  past_quarters = calendar -> january
      SELECT Id, CreatedDate, OrderItemId__c, Subject, Description FROM Case WHERE OrderItemId__c IN ('802Ws000001lscLIAQ', '802Ws000001lvn7IAA', '802Ws000001lyBcIAI', '802Ws000001m0MyIAI', '802Ws000001m2bpIAA', '802Ws000001m5XtIAI', '802Ws000001mBn6IAE', '802Ws000001mCzFIAU', '802Ws000001mD8vIAE') AND CreatedDate >= 2019-07-01T00:00:00Z AND CreatedDate < 2020-07-01T00:00:00Z
```

## original/262 (top_issue_identification, right)

```
run 1: answer None (key None, right)
  not checked: no applicable query
run 2: answer None (key None, right)
  not checked: no applicable query
run 3: answer None (key None, right)
  not checked: no applicable query
```

## original/294 (top_issue_identification, wrong)

```
run 1: answer None (key a1MWs0000012tvt, wrong)
  own level: fail (deciding query: receipt entry 8)
  [asked] past_quarters = rolling; rolling_end = today_counted -> a1MWs0000012tvt
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lvHGIAY','802Ws000001lvgdIAA','802Ws000001m0QEIAY','802Ws000001m1MEIAY','802Ws000001m28cIAA','802Ws000001m3krIAA','802Ws000001m4OzIAI','802Ws000001m4jwIAA','802Ws000001m5ufIAA','802Ws000001m6ykIAA','802Ws000001m70EIAQ','802Ws000001m7WWIAY','802Ws000001m8CUIAY','802Ws000001m8lwIAA','802Ws000001mBIMIA2','802Ws000001mBbmIAE','802Ws000001mCT2IAM','802Ws000001mCpWIAU','802Ws000001mEWNIA2','802Ws000001mEhgIAE') AND CreatedDate >= 2021-03-18T00:00:00Z AND CreatedDate < 2021-12-19T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> a1MWs0000012tvt
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lvHGIAY','802Ws000001lvgdIAA','802Ws000001m0QEIAY','802Ws000001m1MEIAY','802Ws000001m28cIAA','802Ws000001m3krIAA','802Ws000001m4OzIAI','802Ws000001m4jwIAA','802Ws000001m5ufIAA','802Ws000001m6ykIAA','802Ws000001m70EIAQ','802Ws000001m7WWIAY','802Ws000001m8CUIAY','802Ws000001m8lwIAA','802Ws000001mBIMIA2','802Ws000001mBbmIAE','802Ws000001mCT2IAM','802Ws000001mCpWIAU','802Ws000001mEWNIA2','802Ws000001mEhgIAE') AND CreatedDate >= 2021-03-18T00:00:00Z AND CreatedDate < 2021-12-18T00:00:00Z
  past_quarters = calendar -> a1MWs0000012tvt
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lvHGIAY','802Ws000001lvgdIAA','802Ws000001m0QEIAY','802Ws000001m1MEIAY','802Ws000001m28cIAA','802Ws000001m3krIAA','802Ws000001m4OzIAI','802Ws000001m4jwIAA','802Ws000001m5ufIAA','802Ws000001m6ykIAA','802Ws000001m70EIAQ','802Ws000001m7WWIAY','802Ws000001m8CUIAY','802Ws000001m8lwIAA','802Ws000001mBIMIA2','802Ws000001mBbmIAE','802Ws000001mCT2IAM','802Ws000001mCpWIAU','802Ws000001mEWNIA2','802Ws000001mEhgIAE') AND CreatedDate >= 2021-01-01T00:00:00Z AND CreatedDate < 2021-10-01T00:00:00Z
run 2: answer None (key a1MWs0000012tvt, wrong)
  own level: fail (deciding query: receipt entry 9)
  [asked] past_quarters = rolling; rolling_end = today_counted -> a1MWs0000012tvt
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lvHGIAY','802Ws000001lvgdIAA','802Ws000001m0QEIAY','802Ws000001m1MEIAY','802Ws000001m28cIAA','802Ws000001m3krIAA','802Ws000001m4OzIAI','802Ws000001m4jwIAA','802Ws000001m5ufIAA','802Ws000001m6ykIAA','802Ws000001m70EIAQ','802Ws000001m7WWIAY','802Ws000001m8CUIAY','802Ws000001m8lwIAA','802Ws000001mBIMIA2','802Ws000001mBbmIAE','802Ws000001mCT2IAM','802Ws000001mCpWIAU','802Ws000001mEWNIA2','802Ws000001mEhgIAE') AND CreatedDate >= 2021-03-18T00:00:00Z AND CreatedDate < 2021-12-19T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> a1MWs0000012tvt
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lvHGIAY','802Ws000001lvgdIAA','802Ws000001m0QEIAY','802Ws000001m1MEIAY','802Ws000001m28cIAA','802Ws000001m3krIAA','802Ws000001m4OzIAI','802Ws000001m4jwIAA','802Ws000001m5ufIAA','802Ws000001m6ykIAA','802Ws000001m70EIAQ','802Ws000001m7WWIAY','802Ws000001m8CUIAY','802Ws000001m8lwIAA','802Ws000001mBIMIA2','802Ws000001mBbmIAE','802Ws000001mCT2IAM','802Ws000001mCpWIAU','802Ws000001mEWNIA2','802Ws000001mEhgIAE') AND CreatedDate >= 2021-03-18T00:00:00Z AND CreatedDate < 2021-12-18T00:00:00Z
  past_quarters = calendar -> a1MWs0000012tvt
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lvHGIAY','802Ws000001lvgdIAA','802Ws000001m0QEIAY','802Ws000001m1MEIAY','802Ws000001m28cIAA','802Ws000001m3krIAA','802Ws000001m4OzIAI','802Ws000001m4jwIAA','802Ws000001m5ufIAA','802Ws000001m6ykIAA','802Ws000001m70EIAQ','802Ws000001m7WWIAY','802Ws000001m8CUIAY','802Ws000001m8lwIAA','802Ws000001mBIMIA2','802Ws000001mBbmIAE','802Ws000001mCT2IAM','802Ws000001mCpWIAU','802Ws000001mEWNIA2','802Ws000001mEhgIAE') AND CreatedDate >= 2021-01-01T00:00:00Z AND CreatedDate < 2021-10-01T00:00:00Z
run 3: answer None (key a1MWs0000012tvt, wrong)
  own level: pass (deciding query: receipt entry 10)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT Id, Subject, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE Subject LIKE '%Mat%' AND CreatedDate >= 2021-03-18T00:00:00Z AND CreatedDate < 2021-12-19T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT Id, Subject, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE Subject LIKE '%Mat%' AND CreatedDate >= 2021-03-18T00:00:00Z AND CreatedDate < 2021-12-18T00:00:00Z
  past_quarters = calendar -> None
      SELECT Id, Subject, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE Subject LIKE '%Mat%' AND CreatedDate >= 2021-01-01T00:00:00Z AND CreatedDate < 2021-10-01T00:00:00Z
```

## original/307 (top_issue_identification, right)

```
run 1: answer a1MWs0000012u2L (key a1MWs0000012u2L, right)
  own level: pass (deciding query: receipt entry 8)
  [asked] season_months = meteorological; season_year = december_of_y -> a1MWs0000012u2L
      SELECT Id, OrderItemId__c, IssueId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001m4DdIAI', '802Ws000001lzE8IAI') AND CreatedDate >= 2021-12-01T00:00:00Z AND CreatedDate < 2022-03-01T00:00:00Z
  season_months = meteorological; season_year = december_before_y -> None
      SELECT Id, OrderItemId__c, IssueId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001m4DdIAI', '802Ws000001lzE8IAI') AND CreatedDate >= 2020-12-01T00:00:00Z AND CreatedDate < 2021-03-01T00:00:00Z
  season_months = quarter_aligned -> None
      SELECT Id, OrderItemId__c, IssueId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001m4DdIAI', '802Ws000001lzE8IAI') AND CreatedDate >= 2021-01-01T00:00:00Z AND CreatedDate < 2021-04-01T00:00:00Z
run 2: answer a1MWs0000012u2L (key a1MWs0000012u2L, right)
  own level: pass (deciding query: receipt entry 9)
  [asked] season_months = meteorological; season_year = december_of_y -> a tie: a1MWs0000012u2L (first) or None
      SELECT Id, IssueId__c, OrderItemId__c, CreatedDate FROM Case WHERE OrderItemId__c IN ('802Ws000001m3XqIAI', '802Ws000001m3awIAA', '802Ws000001m3cgIAA', '802Ws000001m3eBIAQ', '802Ws000001m3hQIAQ', '802Ws000001m3j2IAA', '802Ws000001m3kfIAA', '802Ws000001m3r8IAA', '802Ws000001m4C7IAI', '802Ws000001m4DdIAI', '802Ws000001m4K5IAI', '802Ws000001m4QbIAI', '802Ws000001m4SAIAY', '802Ws000001m4YgIAI', '802Ws000001m4YkIAI', '802Ws000001m4c0IAA', '802Ws000001m4cAIAQ', '802Ws000001m4dRIAQ', '802Ws000001m59pIAA', '802Ws000001m5BLIAY', '802Ws000001m5BOIAY', '802Ws000001m5GBIAY', '802Ws000001m5HyIAI', '802Ws000001m5MkIAI', '802Ws000001m5MmIAI', '802Ws000001m5OIIAY', '802Ws000001m5UjIAI', '802Ws000001m5jEIAQ', '802Ws000001m5wCIAQ', '802Ws000001m62ZIAQ', '802Ws000001m64FIAQ', '802Ws000001m64IIAQ', '802Ws000001m65mIAA', '802Ws000001m65sIAA', '802Ws000001m67RIAQ', '802Ws000001m67WIAQ', '802Ws000001m6H4IAI', '802Ws000001m6H5IAI', '802Ws000001m6NbIAI', '802Ws000001m6P7IAI', '802Ws000001m6PKIAY', '802Ws000001m6deIAA', '802Ws000001m6liIAA', '802Ws000001m6lnIAA', '802Ws000001m6nSIAQ', '802Ws000001m6qaIAA', '802Ws000001m6sEIAQ', '802Ws000001m79uIAA', '802Ws000001m79vIAA', '802Ws000001m7BbIAI', '802Ws000001m7D8IAI', '802Ws000001m7GOIAY', '802Ws000001m7QGIAY', '802Ws000001m7Y8IAI', '802Ws000001m7pwIAA', '802Ws000001m7zVIAQ', '802Ws000001m81AIAQ', '802Ws000001m81CIAQ', '802Ws000001m84RIAQ', '802Ws000001m865IAA', '802Ws000001m866IAA', '802Ws000001m87gIAA', '802Ws000001m8FdIAI', '802Ws000001m8UAIAY', '802Ws000001m8Z0IAI', '802Ws000001m8amIAA', '802Ws000001m8fSIAQ', '802Ws000001m8hFIAQ', '802Ws000001m8kKIAQ', '802Ws000001m8neIAA', '802Ws000001m8u3IAA', '802Ws000001m93dIAA', '802Ws000001m95JIAQ', '802Ws000001m9A9IAI', '802Ws000001m9BhIAI', '802Ws000001m9JnIAI', '802Ws000001m9JqIAI', '802Ws000001m9YHIAY', '802Ws000001m9emIAA', '802Ws000001m9hzIAA', '802Ws000001m9mwIAA', '802Ws000001m9uuIAA', '802Ws000001m9waIAA', '802Ws000001mA9ZIAU', '802Ws000001mACbIAM', '802Ws000001mAKhIAM', '802Ws000001mAR7IAM', '802Ws000001mASnIAM', '802Ws000001mAcPIAU', '802Ws000001mAmNIAU', '802Ws000001mAuBIAU', '802Ws000001mAz2IAE', '802Ws000001mAzFIAU', '802Ws000001mB0eIAE', '802Ws000001mB0hIAE', '802Ws000001mB5RIAU', '802Ws000001mB5SIAU', '802Ws000001mBGlIAM', '802Ws000001mBNDIA2', '802Ws000001mBNKIA2', '802Ws000001mBWsIAM', '802Ws000001mC6PIAU', '802Ws000001mCEQIA2', '802Ws000001mCPsIAM', '802Ws000001mCfpIAE', '802Ws000001mCr8IAE', '802Ws000001mCzCIAU', '802Ws000001mD5dIAE', '802Ws000001mDDiIAM', '802Ws000001mDGwIAM', '802Ws000001mDLmIAM', '802Ws000001mDVRIA2', '802Ws000001mDqRIAU', '802Ws000001mDs4IAE', '802Ws000001mDtdIAE', '802Ws000001mDvFIAU', '802Ws000001mE3TIAU', '802Ws000001mE4xIAE', '802Ws000001mESYIA2', '802Ws000001mEcnIAE', '802Ws000001mF4DIAU', '802Ws000001mFKLIA2', '802Ws000001mFXHIA2', '802Ws000001mFXIIA2', '802Ws000001mFqdIAE', '802Ws000001mG58IAE') AND CreatedDate >= 2021-12-01T00:00:00Z AND CreatedDate < 2022-03-01T00:00:00Z
  season_months = meteorological; season_year = december_before_y -> None
      SELECT Id, IssueId__c, OrderItemId__c, CreatedDate FROM Case WHERE OrderItemId__c IN ('802Ws000001m3XqIAI', '802Ws000001m3awIAA', '802Ws000001m3cgIAA', '802Ws000001m3eBIAQ', '802Ws000001m3hQIAQ', '802Ws000001m3j2IAA', '802Ws000001m3kfIAA', '802Ws000001m3r8IAA', '802Ws000001m4C7IAI', '802Ws000001m4DdIAI', '802Ws000001m4K5IAI', '802Ws000001m4QbIAI', '802Ws000001m4SAIAY', '802Ws000001m4YgIAI', '802Ws000001m4YkIAI', '802Ws000001m4c0IAA', '802Ws000001m4cAIAQ', '802Ws000001m4dRIAQ', '802Ws000001m59pIAA', '802Ws000001m5BLIAY', '802Ws000001m5BOIAY', '802Ws000001m5GBIAY', '802Ws000001m5HyIAI', '802Ws000001m5MkIAI', '802Ws000001m5MmIAI', '802Ws000001m5OIIAY', '802Ws000001m5UjIAI', '802Ws000001m5jEIAQ', '802Ws000001m5wCIAQ', '802Ws000001m62ZIAQ', '802Ws000001m64FIAQ', '802Ws000001m64IIAQ', '802Ws000001m65mIAA', '802Ws000001m65sIAA', '802Ws000001m67RIAQ', '802Ws000001m67WIAQ', '802Ws000001m6H4IAI', '802Ws000001m6H5IAI', '802Ws000001m6NbIAI', '802Ws000001m6P7IAI', '802Ws000001m6PKIAY', '802Ws000001m6deIAA', '802Ws000001m6liIAA', '802Ws000001m6lnIAA', '802Ws000001m6nSIAQ', '802Ws000001m6qaIAA', '802Ws000001m6sEIAQ', '802Ws000001m79uIAA', '802Ws000001m79vIAA', '802Ws000001m7BbIAI', '802Ws000001m7D8IAI', '802Ws000001m7GOIAY', '802Ws000001m7QGIAY', '802Ws000001m7Y8IAI', '802Ws000001m7pwIAA', '802Ws000001m7zVIAQ', '802Ws000001m81AIAQ', '802Ws000001m81CIAQ', '802Ws000001m84RIAQ', '802Ws000001m865IAA', '802Ws000001m866IAA', '802Ws000001m87gIAA', '802Ws000001m8FdIAI', '802Ws000001m8UAIAY', '802Ws000001m8Z0IAI', '802Ws000001m8amIAA', '802Ws000001m8fSIAQ', '802Ws000001m8hFIAQ', '802Ws000001m8kKIAQ', '802Ws000001m8neIAA', '802Ws000001m8u3IAA', '802Ws000001m93dIAA', '802Ws000001m95JIAQ', '802Ws000001m9A9IAI', '802Ws000001m9BhIAI', '802Ws000001m9JnIAI', '802Ws000001m9JqIAI', '802Ws000001m9YHIAY', '802Ws000001m9emIAA', '802Ws000001m9hzIAA', '802Ws000001m9mwIAA', '802Ws000001m9uuIAA', '802Ws000001m9waIAA', '802Ws000001mA9ZIAU', '802Ws000001mACbIAM', '802Ws000001mAKhIAM', '802Ws000001mAR7IAM', '802Ws000001mASnIAM', '802Ws000001mAcPIAU', '802Ws000001mAmNIAU', '802Ws000001mAuBIAU', '802Ws000001mAz2IAE', '802Ws000001mAzFIAU', '802Ws000001mB0eIAE', '802Ws000001mB0hIAE', '802Ws000001mB5RIAU', '802Ws000001mB5SIAU', '802Ws000001mBGlIAM', '802Ws000001mBNDIA2', '802Ws000001mBNKIA2', '802Ws000001mBWsIAM', '802Ws000001mC6PIAU', '802Ws000001mCEQIA2', '802Ws000001mCPsIAM', '802Ws000001mCfpIAE', '802Ws000001mCr8IAE', '802Ws000001mCzCIAU', '802Ws000001mD5dIAE', '802Ws000001mDDiIAM', '802Ws000001mDGwIAM', '802Ws000001mDLmIAM', '802Ws000001mDVRIA2', '802Ws000001mDqRIAU', '802Ws000001mDs4IAE', '802Ws000001mDtdIAE', '802Ws000001mDvFIAU', '802Ws000001mE3TIAU', '802Ws000001mE4xIAE', '802Ws000001mESYIA2', '802Ws000001mEcnIAE', '802Ws000001mF4DIAU', '802Ws000001mFKLIA2', '802Ws000001mFXHIA2', '802Ws000001mFXIIA2', '802Ws000001mFqdIAE', '802Ws000001mG58IAE') AND CreatedDate >= 2020-12-01T00:00:00Z AND CreatedDate < 2021-03-01T00:00:00Z
  season_months = quarter_aligned -> None
      SELECT Id, IssueId__c, OrderItemId__c, CreatedDate FROM Case WHERE OrderItemId__c IN ('802Ws000001m3XqIAI', '802Ws000001m3awIAA', '802Ws000001m3cgIAA', '802Ws000001m3eBIAQ', '802Ws000001m3hQIAQ', '802Ws000001m3j2IAA', '802Ws000001m3kfIAA', '802Ws000001m3r8IAA', '802Ws000001m4C7IAI', '802Ws000001m4DdIAI', '802Ws000001m4K5IAI', '802Ws000001m4QbIAI', '802Ws000001m4SAIAY', '802Ws000001m4YgIAI', '802Ws000001m4YkIAI', '802Ws000001m4c0IAA', '802Ws000001m4cAIAQ', '802Ws000001m4dRIAQ', '802Ws000001m59pIAA', '802Ws000001m5BLIAY', '802Ws000001m5BOIAY', '802Ws000001m5GBIAY', '802Ws000001m5HyIAI', '802Ws000001m5MkIAI', '802Ws000001m5MmIAI', '802Ws000001m5OIIAY', '802Ws000001m5UjIAI', '802Ws000001m5jEIAQ', '802Ws000001m5wCIAQ', '802Ws000001m62ZIAQ', '802Ws000001m64FIAQ', '802Ws000001m64IIAQ', '802Ws000001m65mIAA', '802Ws000001m65sIAA', '802Ws000001m67RIAQ', '802Ws000001m67WIAQ', '802Ws000001m6H4IAI', '802Ws000001m6H5IAI', '802Ws000001m6NbIAI', '802Ws000001m6P7IAI', '802Ws000001m6PKIAY', '802Ws000001m6deIAA', '802Ws000001m6liIAA', '802Ws000001m6lnIAA', '802Ws000001m6nSIAQ', '802Ws000001m6qaIAA', '802Ws000001m6sEIAQ', '802Ws000001m79uIAA', '802Ws000001m79vIAA', '802Ws000001m7BbIAI', '802Ws000001m7D8IAI', '802Ws000001m7GOIAY', '802Ws000001m7QGIAY', '802Ws000001m7Y8IAI', '802Ws000001m7pwIAA', '802Ws000001m7zVIAQ', '802Ws000001m81AIAQ', '802Ws000001m81CIAQ', '802Ws000001m84RIAQ', '802Ws000001m865IAA', '802Ws000001m866IAA', '802Ws000001m87gIAA', '802Ws000001m8FdIAI', '802Ws000001m8UAIAY', '802Ws000001m8Z0IAI', '802Ws000001m8amIAA', '802Ws000001m8fSIAQ', '802Ws000001m8hFIAQ', '802Ws000001m8kKIAQ', '802Ws000001m8neIAA', '802Ws000001m8u3IAA', '802Ws000001m93dIAA', '802Ws000001m95JIAQ', '802Ws000001m9A9IAI', '802Ws000001m9BhIAI', '802Ws000001m9JnIAI', '802Ws000001m9JqIAI', '802Ws000001m9YHIAY', '802Ws000001m9emIAA', '802Ws000001m9hzIAA', '802Ws000001m9mwIAA', '802Ws000001m9uuIAA', '802Ws000001m9waIAA', '802Ws000001mA9ZIAU', '802Ws000001mACbIAM', '802Ws000001mAKhIAM', '802Ws000001mAR7IAM', '802Ws000001mASnIAM', '802Ws000001mAcPIAU', '802Ws000001mAmNIAU', '802Ws000001mAuBIAU', '802Ws000001mAz2IAE', '802Ws000001mAzFIAU', '802Ws000001mB0eIAE', '802Ws000001mB0hIAE', '802Ws000001mB5RIAU', '802Ws000001mB5SIAU', '802Ws000001mBGlIAM', '802Ws000001mBNDIA2', '802Ws000001mBNKIA2', '802Ws000001mBWsIAM', '802Ws000001mC6PIAU', '802Ws000001mCEQIA2', '802Ws000001mCPsIAM', '802Ws000001mCfpIAE', '802Ws000001mCr8IAE', '802Ws000001mCzCIAU', '802Ws000001mD5dIAE', '802Ws000001mDDiIAM', '802Ws000001mDGwIAM', '802Ws000001mDLmIAM', '802Ws000001mDVRIA2', '802Ws000001mDqRIAU', '802Ws000001mDs4IAE', '802Ws000001mDtdIAE', '802Ws000001mDvFIAU', '802Ws000001mE3TIAU', '802Ws000001mE4xIAE', '802Ws000001mESYIA2', '802Ws000001mEcnIAE', '802Ws000001mF4DIAU', '802Ws000001mFKLIA2', '802Ws000001mFXHIA2', '802Ws000001mFXIIA2', '802Ws000001mFqdIAE', '802Ws000001mG58IAE') AND CreatedDate >= 2021-01-01T00:00:00Z AND CreatedDate < 2021-04-01T00:00:00Z
run 3: answer a1MWs0000012u2L (key a1MWs0000012u2L, right)
  own level: pass (deciding query: receipt entry 6)
  [asked] season_months = meteorological; season_year = december_of_y -> a1MWs0000012u2L
      SELECT OrderItemId__c, IssueId__c FROM Case WHERE CreatedDate >= 2021-12-01T00:00:00Z AND CreatedDate < 2022-03-01T00:00:00Z
  season_months = meteorological; season_year = december_before_y -> a1MWs0000012u2L
      SELECT OrderItemId__c, IssueId__c FROM Case WHERE CreatedDate >= 2020-12-01T00:00:00Z AND CreatedDate < 2021-03-01T00:00:00Z
  season_months = quarter_aligned -> a1MWs0000012u2L
      SELECT OrderItemId__c, IssueId__c FROM Case WHERE CreatedDate >= 2021-01-01T00:00:00Z AND CreatedDate < 2021-04-01T00:00:00Z
```

## original/334 (top_issue_identification, right)

```
run 1: answer None (key None, right)
  not checked: no applicable query
run 2: answer None (key None, right)
  not checked: no applicable query
run 3: answer None (key None, right)
  not checked: no applicable query
```

## original/337 (top_issue_identification, wrong)

```
run 1: answer None (key a1MWs0000012u0j, wrong)
  own level: pass (deciding query: receipt entry 9)
  [asked] season_months = meteorological; season_year = december_of_y -> a1MWs0000012u0j
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsNnIAI','802Ws000001lvgkIAA','802Ws000001lwY1IAI','802Ws000001lwo7IAA','802Ws000001lxDnIAI','802Ws000001lxKOIAY','802Ws000001lyGIIAY','802Ws000001lyTMIAY','802Ws000001lyl6IAA','802Ws000001lz66IAA','802Ws000001lzcFIAQ','802Ws000001lzylIAA','802Ws000001m16CIAQ','802Ws000001m1O4IAI','802Ws000001m5Y0IAI','802Ws000001m758IAA','802Ws000001m7Q5IAI','802Ws000001m8FkIAI','802Ws000001m8fRIAQ','802Ws000001m8kSIAQ','802Ws000001m8vbIAA','802Ws000001m9jgIAA','802Ws000001mAMQIA2','802Ws000001mAVxIAM','802Ws000001mAvmIAE','802Ws000001mBANIA2','802Ws000001mBrpIAE') AND CreatedDate >= 2020-12-01T00:00:00Z AND CreatedDate < 2021-03-01T00:00:00Z
  season_months = meteorological; season_year = december_before_y -> None
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsNnIAI','802Ws000001lvgkIAA','802Ws000001lwY1IAI','802Ws000001lwo7IAA','802Ws000001lxDnIAI','802Ws000001lxKOIAY','802Ws000001lyGIIAY','802Ws000001lyTMIAY','802Ws000001lyl6IAA','802Ws000001lz66IAA','802Ws000001lzcFIAQ','802Ws000001lzylIAA','802Ws000001m16CIAQ','802Ws000001m1O4IAI','802Ws000001m5Y0IAI','802Ws000001m758IAA','802Ws000001m7Q5IAI','802Ws000001m8FkIAI','802Ws000001m8fRIAQ','802Ws000001m8kSIAQ','802Ws000001m8vbIAA','802Ws000001m9jgIAA','802Ws000001mAMQIA2','802Ws000001mAVxIAM','802Ws000001mAvmIAE','802Ws000001mBANIA2','802Ws000001mBrpIAE') AND CreatedDate >= 2019-12-01T00:00:00Z AND CreatedDate < 2020-03-01T00:00:00Z
  season_months = quarter_aligned -> None
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsNnIAI','802Ws000001lvgkIAA','802Ws000001lwY1IAI','802Ws000001lwo7IAA','802Ws000001lxDnIAI','802Ws000001lxKOIAY','802Ws000001lyGIIAY','802Ws000001lyTMIAY','802Ws000001lyl6IAA','802Ws000001lz66IAA','802Ws000001lzcFIAQ','802Ws000001lzylIAA','802Ws000001m16CIAQ','802Ws000001m1O4IAI','802Ws000001m5Y0IAI','802Ws000001m758IAA','802Ws000001m7Q5IAI','802Ws000001m8FkIAI','802Ws000001m8fRIAQ','802Ws000001m8kSIAQ','802Ws000001m8vbIAA','802Ws000001m9jgIAA','802Ws000001mAMQIA2','802Ws000001mAVxIAM','802Ws000001mAvmIAE','802Ws000001mBANIA2','802Ws000001mBrpIAE') AND CreatedDate >= 2020-01-01T00:00:00Z AND CreatedDate < 2020-04-01T00:00:00Z
run 2: answer None (key a1MWs0000012u0j, wrong)
  own level: pass (deciding query: receipt entry 6)
  [asked] season_months = meteorological; season_year = december_of_y -> a1MWs0000012u0j
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsNnIAI','802Ws000001lvgkIAA','802Ws000001lwY1IAI','802Ws000001lwo7IAA','802Ws000001lxDnIAI','802Ws000001lxKOIAY','802Ws000001lyGIIAY','802Ws000001lyTMIAY','802Ws000001lyl6IAA','802Ws000001lz66IAA','802Ws000001lzcFIAQ','802Ws000001lzylIAA','802Ws000001m16CIAQ','802Ws000001m1O4IAI','802Ws000001m5Y0IAI','802Ws000001m758IAA','802Ws000001m7Q5IAI','802Ws000001m8FkIAI','802Ws000001m8fRIAQ','802Ws000001m8kSIAQ','802Ws000001m8vbIAA','802Ws000001m9jgIAA','802Ws000001mAMQIA2','802Ws000001mAVxIAM','802Ws000001mAvmIAE','802Ws000001mBANIA2','802Ws000001mBrpIAE') AND CreatedDate >= 2020-12-01T00:00:00Z AND CreatedDate < 2021-03-01T00:00:00Z
  season_months = meteorological; season_year = december_before_y -> None
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsNnIAI','802Ws000001lvgkIAA','802Ws000001lwY1IAI','802Ws000001lwo7IAA','802Ws000001lxDnIAI','802Ws000001lxKOIAY','802Ws000001lyGIIAY','802Ws000001lyTMIAY','802Ws000001lyl6IAA','802Ws000001lz66IAA','802Ws000001lzcFIAQ','802Ws000001lzylIAA','802Ws000001m16CIAQ','802Ws000001m1O4IAI','802Ws000001m5Y0IAI','802Ws000001m758IAA','802Ws000001m7Q5IAI','802Ws000001m8FkIAI','802Ws000001m8fRIAQ','802Ws000001m8kSIAQ','802Ws000001m8vbIAA','802Ws000001m9jgIAA','802Ws000001mAMQIA2','802Ws000001mAVxIAM','802Ws000001mAvmIAE','802Ws000001mBANIA2','802Ws000001mBrpIAE') AND CreatedDate >= 2019-12-01T00:00:00Z AND CreatedDate < 2020-03-01T00:00:00Z
  season_months = quarter_aligned -> None
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsNnIAI','802Ws000001lvgkIAA','802Ws000001lwY1IAI','802Ws000001lwo7IAA','802Ws000001lxDnIAI','802Ws000001lxKOIAY','802Ws000001lyGIIAY','802Ws000001lyTMIAY','802Ws000001lyl6IAA','802Ws000001lz66IAA','802Ws000001lzcFIAQ','802Ws000001lzylIAA','802Ws000001m16CIAQ','802Ws000001m1O4IAI','802Ws000001m5Y0IAI','802Ws000001m758IAA','802Ws000001m7Q5IAI','802Ws000001m8FkIAI','802Ws000001m8fRIAQ','802Ws000001m8kSIAQ','802Ws000001m8vbIAA','802Ws000001m9jgIAA','802Ws000001mAMQIA2','802Ws000001mAVxIAM','802Ws000001mAvmIAE','802Ws000001mBANIA2','802Ws000001mBrpIAE') AND CreatedDate >= 2020-01-01T00:00:00Z AND CreatedDate < 2020-04-01T00:00:00Z
run 3: answer None (key a1MWs0000012u0j, wrong)
  own level: fail (deciding query: receipt entry 3)
  [asked] season_months = meteorological; season_year = december_of_y -> a1MWs0000012u0j
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsNnIAI','802Ws000001lvgkIAA','802Ws000001lwY1IAI','802Ws000001lwo7IAA','802Ws000001lxDnIAI','802Ws000001lxKOIAY','802Ws000001lyGIIAY','802Ws000001lyTMIAY','802Ws000001lyl6IAA','802Ws000001lz66IAA','802Ws000001lzcFIAQ','802Ws000001lzylIAA','802Ws000001m16CIAQ','802Ws000001m1O4IAI','802Ws000001m5Y0IAI','802Ws000001m758IAA','802Ws000001m7Q5IAI','802Ws000001m8FkIAI','802Ws000001m8fRIAQ','802Ws000001m8kSIAQ','802Ws000001m8vbIAA','802Ws000001m9jgIAA','802Ws000001mAMQIA2','802Ws000001mAVxIAM','802Ws000001mAvmIAE','802Ws000001mBANIA2','802Ws000001mBrpIAE') AND CreatedDate >= 2020-12-01T00:00:00Z AND CreatedDate < 2021-03-01T00:00:00Z
  season_months = meteorological; season_year = december_before_y -> None
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsNnIAI','802Ws000001lvgkIAA','802Ws000001lwY1IAI','802Ws000001lwo7IAA','802Ws000001lxDnIAI','802Ws000001lxKOIAY','802Ws000001lyGIIAY','802Ws000001lyTMIAY','802Ws000001lyl6IAA','802Ws000001lz66IAA','802Ws000001lzcFIAQ','802Ws000001lzylIAA','802Ws000001m16CIAQ','802Ws000001m1O4IAI','802Ws000001m5Y0IAI','802Ws000001m758IAA','802Ws000001m7Q5IAI','802Ws000001m8FkIAI','802Ws000001m8fRIAQ','802Ws000001m8kSIAQ','802Ws000001m8vbIAA','802Ws000001m9jgIAA','802Ws000001mAMQIA2','802Ws000001mAVxIAM','802Ws000001mAvmIAE','802Ws000001mBANIA2','802Ws000001mBrpIAE') AND CreatedDate >= 2019-12-01T00:00:00Z AND CreatedDate < 2020-03-01T00:00:00Z
  season_months = quarter_aligned -> None
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lsNnIAI','802Ws000001lvgkIAA','802Ws000001lwY1IAI','802Ws000001lwo7IAA','802Ws000001lxDnIAI','802Ws000001lxKOIAY','802Ws000001lyGIIAY','802Ws000001lyTMIAY','802Ws000001lyl6IAA','802Ws000001lz66IAA','802Ws000001lzcFIAQ','802Ws000001lzylIAA','802Ws000001m16CIAQ','802Ws000001m1O4IAI','802Ws000001m5Y0IAI','802Ws000001m758IAA','802Ws000001m7Q5IAI','802Ws000001m8FkIAI','802Ws000001m8fRIAQ','802Ws000001m8kSIAQ','802Ws000001m8vbIAA','802Ws000001m9jgIAA','802Ws000001mAMQIA2','802Ws000001mAVxIAM','802Ws000001mAvmIAE','802Ws000001mBANIA2','802Ws000001mBrpIAE') AND CreatedDate >= 2020-01-01T00:00:00Z AND CreatedDate < 2020-04-01T00:00:00Z
```

## original/340 (top_issue_identification, right)

```
run 1: answer None (key None, right)
  not checked: no applicable query
run 2: answer None (key None, right)
  not checked: no applicable query
run 3: answer None (key None, right)
  not checked: no applicable query
```

## original/354 (top_issue_identification, right)

```
run 1: answer a1MWs0000012u5Z (key a1MWs0000012u5Z, right)
  own level: fail (deciding query: receipt entry 7)
  [asked] past_quarters = rolling; rolling_end = today_counted -> None
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c, ProductId FROM Case WHERE ProductId = '01tWs000002wRrVIAU' AND CreatedDate >= 2023-06-24T00:00:00Z AND CreatedDate < 2024-03-25T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> None
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c, ProductId FROM Case WHERE ProductId = '01tWs000002wRrVIAU' AND CreatedDate >= 2023-06-24T00:00:00Z AND CreatedDate < 2024-03-24T00:00:00Z
  past_quarters = calendar -> None
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c, ProductId FROM Case WHERE ProductId = '01tWs000002wRrVIAU' AND CreatedDate >= 2023-04-01T00:00:00Z AND CreatedDate < 2024-01-01T00:00:00Z
run 2: answer a1MWs0000012u5Z (key a1MWs0000012u5Z, right)
  own level: fail (deciding query: receipt entry 4)
  [asked] past_quarters = rolling; rolling_end = today_counted -> a1MWs0000012u5Z
      SELECT Id, IssueId__c, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lussIAA','802Ws000001lvn6IAA','802Ws000001lvwnIAA','802Ws000001lwg5IAA','802Ws000001lwjCIAQ','802Ws000001lwkrIAA','802Ws000001lwmZIAQ','802Ws000001lww9IAA','802Ws000001lx5oIAA','802Ws000001lxAbIAI','802Ws000001lxNXIAY','802Ws000001lxVYIAY','802Ws000001lyZkIAI','802Ws000001lzKVIAY','802Ws000001lzZ6IAI','802Ws000001lzdyIAA','802Ws000001m0ICIAY','802Ws000001m0JhIAI','802Ws000001m0JpIAI','802Ws000001m0uuIAA','802Ws000001m1SnIAI','802Ws000001m1xPIAQ','802Ws000001m2OoIAI','802Ws000001m2aBIAQ','802Ws000001m2blIAA','802Ws000001m2dOIAQ','802Ws000001m2tNIAQ','802Ws000001m31SIAQ','802Ws000001m382IAA','802Ws000001m3keIAA','802Ws000001m4C5IAI','802Ws000001m4S9IAI','802Ws000001m4laIAA','802Ws000001m5PsIAI','802Ws000001m5RXIAY','802Ws000001m5eTIAQ','802Ws000001m6fHIAQ','802Ws000001m6ylIAA','802Ws000001m7ZkIAI','802Ws000001m7eeIAA','802Ws000001m8PNIAY','802Ws000001m8cFIAQ','802Ws000001m8ioIAA','802Ws000001m8yxIAA','802Ws000001m9TTIAY','802Ws000001m9YKIAY','802Ws000001m9rhIAA','802Ws000001mA9TIAU','802Ws000001mB73IAE','802Ws000001mCG4IAM','802Ws000001mDwuIAE','802Ws000001mDwwIAE','802Ws000001mE3QIAU') AND CreatedDate >= 2023-06-24T00:00:00Z AND CreatedDate < 2024-03-25T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> a1MWs0000012u5Z
      SELECT Id, IssueId__c, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lussIAA','802Ws000001lvn6IAA','802Ws000001lvwnIAA','802Ws000001lwg5IAA','802Ws000001lwjCIAQ','802Ws000001lwkrIAA','802Ws000001lwmZIAQ','802Ws000001lww9IAA','802Ws000001lx5oIAA','802Ws000001lxAbIAI','802Ws000001lxNXIAY','802Ws000001lxVYIAY','802Ws000001lyZkIAI','802Ws000001lzKVIAY','802Ws000001lzZ6IAI','802Ws000001lzdyIAA','802Ws000001m0ICIAY','802Ws000001m0JhIAI','802Ws000001m0JpIAI','802Ws000001m0uuIAA','802Ws000001m1SnIAI','802Ws000001m1xPIAQ','802Ws000001m2OoIAI','802Ws000001m2aBIAQ','802Ws000001m2blIAA','802Ws000001m2dOIAQ','802Ws000001m2tNIAQ','802Ws000001m31SIAQ','802Ws000001m382IAA','802Ws000001m3keIAA','802Ws000001m4C5IAI','802Ws000001m4S9IAI','802Ws000001m4laIAA','802Ws000001m5PsIAI','802Ws000001m5RXIAY','802Ws000001m5eTIAQ','802Ws000001m6fHIAQ','802Ws000001m6ylIAA','802Ws000001m7ZkIAI','802Ws000001m7eeIAA','802Ws000001m8PNIAY','802Ws000001m8cFIAQ','802Ws000001m8ioIAA','802Ws000001m8yxIAA','802Ws000001m9TTIAY','802Ws000001m9YKIAY','802Ws000001m9rhIAA','802Ws000001mA9TIAU','802Ws000001mB73IAE','802Ws000001mCG4IAM','802Ws000001mDwuIAE','802Ws000001mDwwIAE','802Ws000001mE3QIAU') AND CreatedDate >= 2023-06-24T00:00:00Z AND CreatedDate < 2024-03-24T00:00:00Z
  past_quarters = calendar -> a1MWs0000012u5Z
      SELECT Id, IssueId__c, CreatedDate, OrderItemId__c FROM Case WHERE OrderItemId__c IN ('802Ws000001lussIAA','802Ws000001lvn6IAA','802Ws000001lvwnIAA','802Ws000001lwg5IAA','802Ws000001lwjCIAQ','802Ws000001lwkrIAA','802Ws000001lwmZIAQ','802Ws000001lww9IAA','802Ws000001lx5oIAA','802Ws000001lxAbIAI','802Ws000001lxNXIAY','802Ws000001lxVYIAY','802Ws000001lyZkIAI','802Ws000001lzKVIAY','802Ws000001lzZ6IAI','802Ws000001lzdyIAA','802Ws000001m0ICIAY','802Ws000001m0JhIAI','802Ws000001m0JpIAI','802Ws000001m0uuIAA','802Ws000001m1SnIAI','802Ws000001m1xPIAQ','802Ws000001m2OoIAI','802Ws000001m2aBIAQ','802Ws000001m2blIAA','802Ws000001m2dOIAQ','802Ws000001m2tNIAQ','802Ws000001m31SIAQ','802Ws000001m382IAA','802Ws000001m3keIAA','802Ws000001m4C5IAI','802Ws000001m4S9IAI','802Ws000001m4laIAA','802Ws000001m5PsIAI','802Ws000001m5RXIAY','802Ws000001m5eTIAQ','802Ws000001m6fHIAQ','802Ws000001m6ylIAA','802Ws000001m7ZkIAI','802Ws000001m7eeIAA','802Ws000001m8PNIAY','802Ws000001m8cFIAQ','802Ws000001m8ioIAA','802Ws000001m8yxIAA','802Ws000001m9TTIAY','802Ws000001m9YKIAY','802Ws000001m9rhIAA','802Ws000001mA9TIAU','802Ws000001mB73IAE','802Ws000001mCG4IAM','802Ws000001mDwuIAE','802Ws000001mDwwIAE','802Ws000001mE3QIAU') AND CreatedDate >= 2023-04-01T00:00:00Z AND CreatedDate < 2024-01-01T00:00:00Z
run 3: answer a1MWs0000012u5Z (key a1MWs0000012u5Z, right)
  own level: pass (deciding query: receipt entry 6)
  [asked] past_quarters = rolling; rolling_end = today_counted -> a1MWs0000012u5Z
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE CreatedDate >= 2023-06-24T00:00:00Z AND CreatedDate < 2024-03-25T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> a1MWs0000012u5Z
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE CreatedDate >= 2023-06-24T00:00:00Z AND CreatedDate < 2024-03-24T00:00:00Z
  past_quarters = calendar -> a1MWs0000012u5Z
      SELECT Id, CreatedDate, IssueId__c, OrderItemId__c FROM Case WHERE CreatedDate >= 2023-04-01T00:00:00Z AND CreatedDate < 2024-01-01T00:00:00Z
```

## original/356 (top_issue_identification, wrong)

```
run 1: answer a1MWs0000012u7B (key a1MWs0000012u0j, wrong)
  own level: fail (deciding query: receipt entry 8)
  [asked] past_quarters = rolling; rolling_end = today_counted -> a1MWs0000012u0j
      SELECT Id, OrderItemId__c, CreatedDate, IssueId__c FROM Case WHERE CreatedDate >= 2020-06-05T00:00:00Z AND CreatedDate < 2021-12-06T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> a1MWs0000012u0j
      SELECT Id, OrderItemId__c, CreatedDate, IssueId__c FROM Case WHERE CreatedDate >= 2020-06-05T00:00:00Z AND CreatedDate < 2021-12-05T00:00:00Z
  past_quarters = calendar -> a tie: a1MWs0000012u0j (first) or None
      SELECT Id, OrderItemId__c, CreatedDate, IssueId__c FROM Case WHERE CreatedDate >= 2020-04-01T00:00:00Z AND CreatedDate < 2021-10-01T00:00:00Z
run 2: answer a1MWs0000012u7B (key a1MWs0000012u0j, wrong)
  own level: fail (deciding query: receipt entry 9)
  [asked] past_quarters = rolling; rolling_end = today_counted -> a1MWs0000012u0j
      SELECT OrderItemId__c, IssueId__c, CreatedDate FROM Case WHERE OrderItemId__c != null AND CreatedDate >= 2020-06-05T00:00:00Z AND CreatedDate < 2021-12-06T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> a1MWs0000012u0j
      SELECT OrderItemId__c, IssueId__c, CreatedDate FROM Case WHERE OrderItemId__c != null AND CreatedDate >= 2020-06-05T00:00:00Z AND CreatedDate < 2021-12-05T00:00:00Z
  past_quarters = calendar -> a tie: a1MWs0000012u0j (first) or None
      SELECT OrderItemId__c, IssueId__c, CreatedDate FROM Case WHERE OrderItemId__c != null AND CreatedDate >= 2020-04-01T00:00:00Z AND CreatedDate < 2021-10-01T00:00:00Z
run 3: answer a1MWs0000012u7B (key a1MWs0000012u0j, wrong)
  own level: fail (deciding query: receipt entry 10)
  [asked] past_quarters = rolling; rolling_end = today_counted -> a1MWs0000012u0j
      SELECT Id, IssueId__c, OrderItemId__c, CreatedDate FROM Case WHERE CreatedDate >= 2020-06-05T00:00:00Z AND CreatedDate < 2021-12-06T00:00:00Z
  [asked] past_quarters = rolling; rolling_end = today_not_counted -> a1MWs0000012u0j
      SELECT Id, IssueId__c, OrderItemId__c, CreatedDate FROM Case WHERE CreatedDate >= 2020-06-05T00:00:00Z AND CreatedDate < 2021-12-05T00:00:00Z
  past_quarters = calendar -> a tie: a1MWs0000012u0j (first) or None
      SELECT Id, IssueId__c, OrderItemId__c, CreatedDate FROM Case WHERE CreatedDate >= 2020-04-01T00:00:00Z AND CreatedDate < 2021-10-01T00:00:00Z
```
