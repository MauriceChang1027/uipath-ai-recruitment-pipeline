# Setup and Studio Web import

This repository is a sanitized source snapshot. It is deliberately not connected to the repository owner's tenant, Google account, Drive folder, Sheet, or Gmail mailbox.

## Prerequisites

- UiPath Automation Cloud with Studio Web, Agents, Maestro/Flow, Document Understanding, and Integration Service access
- Google Drive, Google Sheets, and Gmail connections created under your own account
- A test-only Drive folder containing synthetic CV PDFs
- A Google Sheet with the columns represented in `samples/candidate-screening.example.csv`

## Import sequence

1. In Studio Web, create a new Solution.
2. Import the projects under `solution/`:
   - `RPA Workflow`
   - `RPA Workflow 1`
   - `Agent`
   - `CandidateCommunicationRouter`
   - `RecruitmentOrchestrator`
3. Rebind the orchestrator's local resource nodes to the imported projects if Studio Web assigns new solution resource keys.
4. Open each RPA workflow and replace every placeholder connection with your own Integration Service connection.
5. Select your own CV folder, output Sheet, Document Understanding project/model, and Gmail connection through the Studio Web resource picker.
6. Replace `hr@example.com` with the test HR mailbox you control.
7. Validate every project, then validate the complete Solution.

## Placeholder map

| Public value | Replace with |
| --- | --- |
| `11111111-1111-4111-8111-111111111111` | Google Drive connection selected in Studio Web |
| `22222222-2222-4222-8222-222222222222` | Google Sheets connection selected in Studio Web |
| `33333333-3333-4333-8333-333333333333` | Gmail connection selected in Studio Web |
| `44444444-4444-4444-8444-444444444444` | Content-generation/LLM connection selected in Studio Web |
| `REPLACE_WITH_YOUR_DRIVE_FOLDER_ID` | Test CV folder ID |
| `REPLACE_WITH_YOUR_SPREADSHEET_ID` | Test output Sheet ID |
| `My Drive/YourProject` | Your own Drive path |
| `hr@example.com` | Your controlled test HR mailbox |

Do not edit generated `resources/solution_folder` files by hand. Let UiPath create the solution bindings when the projects are imported and use the Studio Web resource picker to rebind them.

## Safe verification order

1. Upload only synthetic CVs and clear the test Sheet except for the header row.
2. Run the extraction project and verify that the first candidate is written to row 2.
3. Confirm that the number of candidate rows equals the number of CV files.
4. Run the evaluation project and confirm that only pending rows receive agent output.
5. Set Gmail to a controlled test mailbox, then run the communication router on one row.
6. Verify the message in Gmail and confirm that `EmailStatus`, `EmailDetailStatus`, `CommunicationRoute`, and `RecipientEmail` are updated.
7. Rerun the router and verify that a successfully sent row is skipped rather than emailed twice.

Debugging can produce real side effects. Never test with real candidate addresses or a production mailbox.
