# Round 3's blinded audit: the seal

Written by `scripts/checkable3_audit.py prepare` before any item was labelled. The reader sees `runs/checkable3_audit/items.json`; `runs/checkable3_audit/sealed.json` says which candidate is the key and stays unread until the labels are in. Their sha256:

- `items.json`: `ecaad7d5b79d2ae072a1c95d48763984e6b78701c8936517538207beef4aec69`
- `sealed.json`: `cf33c4207ce0b28211936500722aceccfe40fcaabefe89f2604a3fbf756cd1ea`

25 items (seed 20261103):

- key-reproduction flag: 11
- released, right by the key: 7
- released, wrong by the key: 7
