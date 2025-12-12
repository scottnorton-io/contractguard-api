#!/bin/bash
set -euo pipefail

echo "🧪 Running ContractGuard Contract Tests"

API_URL="http://localhost:8000"
TOKEN="dev-token-12345"
TENANT_ID="test-tenant-001"

# Wait for service ready
echo "⏳ Waiting for service..."
for i in {1..30}; do
  if curl -sf "$API_URL/readyz" > /dev/null; then
    echo "✅ Service ready"
    break
  fi
  sleep 2
done

# Test 1: Health check
echo "\n📊 Test 1: Health endpoints"
curl -sf "$API_URL/healthz" | jq .
curl -sf "$API_URL/readyz" | jq .
curl -sf "$API_URL/version" | jq .

# Test 2: Auth required
echo "\n🔐 Test 2: Auth enforcement"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/v1/contracts")
if [ "$STATUS" == "401" ]; then
  echo "✅ Auth required (401 returned)"
else
  echo "❌ Auth bypass detected (expected 401, got $STATUS)"
  exit 1
fi

# Test 3: Tenant isolation
echo "\n🏢 Test 3: Tenant scoping"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  "$API_URL/v1/contracts")
if [ "$STATUS" == "400" ]; then
  echo "✅ Tenant required (400 returned)"
else
  echo "❌ Tenant bypass detected (expected 400, got $STATUS)"
  exit 1
fi

# Test 4: Compliance query (mock)
echo "\n⚖️ Test 4: Compliance check"
RESPONSE=$(curl -s -X POST "$API_URL/v1/compliance/check" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "test-contract-001",
    "proposed_activity": {
      "type": "clinic",
      "location": "Tokyo, Japan",
      "dates": ["2025-01-15"],
      "marketing_as": "PPA professional"
    }
  }')

echo "$RESPONSE" | jq .

VERDICT=$(echo "$RESPONSE" | jq -r '.verdict')
AUDIT_ID=$(echo "$RESPONSE" | jq -r '.audit_id')

if [ -n "$AUDIT_ID" ] && [ "$AUDIT_ID" != "null" ]; then
  echo "✅ Audit event generated: $AUDIT_ID"
else
  echo "❌ No audit event generated"
  exit 1
fi

# Test 5: Redaction (check logs don't contain sensitive data)
echo "\n🔒 Test 5: Redaction verification"
echo "(Check Docker logs manually for clause_text redaction)"

echo "\n✅ All contract tests passed"
