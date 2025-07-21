# N8N Workflow Testing Procedures

## Pre-Testing Checklist
- [ ] N8N workflow imported and saved
- [ ] FUB credentials configured (`fub-basic-auth`)
- [ ] GitHub webhook configured and active
- [ ] N8N workflow activated/enabled

## Test 1: Workflow Import Validation
1. Import workflow JSON into N8N
2. Verify all 7 nodes are present and connected
3. Check credential references are correct
4. Save workflow without errors

**Expected Result**: Workflow imports successfully with no missing dependencies.

## Test 2: CMA Deployment Simulation
1. Create test CMA file: `test-123-elm-street.html`
2. Add basic HTML content
3. Commit and push to repository
4. Monitor N8N executions

**Expected Results**:
- GitHub webhook triggers workflow
- CMA data extracted: Client "Test", Address "123 Elm Street"
- Person ID defaults to 1903 (Sara Blackwell)
- Due date set to 48 hours from deployment

## Test 3: FUB Integration Validation
Monitor FUB system after test deployment:
1. **Task Creation**: Look for task "CMA Delivered - 123 Elm Street"
2. **Activity Note**: Check activity feed for deployment confirmation
3. **Assignment**: Verify assigned to correct agent (Glenn by default)

**Expected FUB Records**:
- New task with 48-hour due date
- Activity note with CMA URL and deployment details
- Both records linked to Person ID 1903

## Test 4: Agent Assignment Logic
Deploy test CMAs with location-specific names:
- `beacon-test.html` → Should assign to Justin Phillips (ID: 6)
- `coldspring-test.html` → Should assign to Heather Martin (ID: 2)
- `poughkeepsie-test.html` → Should assign to Lloyd Gray (ID: 3)

## Test 5: Error Handling
1. Deploy invalid file (non-HTML)
2. Deploy HTML file with invalid naming
3. Temporarily disable FUB credentials

**Expected Results**:
- Invalid files filtered out (no workflow execution)
- Invalid names default to "Unknown Client/Property"
- Credential errors logged in N8N execution details

## Validation Metrics
After successful test:
- ✅ GitHub webhook delivery: 200 status
- ✅ N8N execution: Success (green)
- ✅ FUB task created: Valid task ID returned
- ✅ FUB activity created: Valid activity ID returned
- ✅ Completion logged: Success status in workflow

## Production Readiness
Workflow is production-ready when:
1. All tests pass consistently
2. No errors in N8N execution logs
3. FUB tasks and activities created correctly
4. Agent assignments working per location rules
5. GitHub webhook delivers 100% success rate

---
*Test completion confirms WILLOW v32.0 automation is operational.*
