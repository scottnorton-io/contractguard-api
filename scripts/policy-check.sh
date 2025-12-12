#!/bin/bash
set -euo pipefail

echo "📋 Running P0 Policy Checks"

FAILED=0

# P0-001: No AUTH_MODE=none in production configs
echo "\n🔐 P0-001: AUTH_MODE=none check"
if find . -name "*.env*" -o -name "*.yaml" -o -name "*.yml" | \
   xargs grep -l "AUTH_MODE.*=.*none" 2>/dev/null | \
   grep -E "(prod|production)" ; then
  echo "❌ P0-001 FAIL: AUTH_MODE=none found in production config"
  FAILED=1
else
  echo "✅ P0-001 PASS"
fi

# P0-002: Audit emission required
echo "\n📝 P0-002: Audit event emission check"
if grep -r "audit" src/contractguard/services/ > /dev/null && \
   grep -r "compliance_query" src/contractguard/api/compliance.py > /dev/null; then
  echo "✅ P0-002 PASS"
else
  echo "❌ P0-002 FAIL: Audit events missing"
  FAILED=1
fi

# P0-003: Redaction required
echo "\n🔒 P0-003: Redaction implementation check"
if [ -f "scripts/test-redaction.sh" ]; then
  echo "✅ P0-003 PASS"
else
  echo "❌ P0-003 FAIL: Redaction tests missing"
  FAILED=1
fi

if [ $FAILED -eq 0 ]; then
  echo "\n✅ All P0 policies passed"
  exit 0
else
  echo "\n❌ P0 policy violations detected"
  exit 1
fi
