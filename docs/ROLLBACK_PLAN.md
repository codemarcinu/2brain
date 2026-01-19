# Rollback Plan

## When to Rollback

Rollback if:
- Data loss occurs
- Critical features broken for >4 hours
- Performance degradation >50%
- Security vulnerability discovered

## Rollback Procedure

### Phase 1: Stop New System (5 minutes)

```bash
cd obsidian-brain-v2
docker compose down
```

### Phase 2: Restore Data (15 minutes)

```bash
# Restore Vault
rm -rf $OBSIDIAN_VAULT_PATH
cp -r /backup/vault-YYYYMMDD $OBSIDIAN_VAULT_PATH

# Restore database (if needed)
docker exec brain-postgres psql -U brain -d obsidian_brain < /backup/postgres-YYYYMMDD.sql
```

### Phase 3: Restart Old System (10 minutes)

```bash
cd /path/to/old/system
./run_brain.sh
```

### Phase 4: Validate (10 minutes)

- [ ] Old system starts successfully
- [ ] Vault accessible
- [ ] No data corruption
- [ ] All features working

### Phase 5: Communication

Notify users:
- What happened
- Why rollback was necessary
- Expected timeline for fix
- Workarounds if any

## Post-Rollback Actions

1. **Investigate root cause**
2. **Fix issues in staging**
3. **Re-test thoroughly**
4. **Plan new migration date**

## Prevention

- Always backup before changes
- Test in staging first
- Have monitoring alerts
- Keep old system for 2 weeks minimum
