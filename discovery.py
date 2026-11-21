"""Source documents and a spoiler-free submission check for independent play.

The raw documents reuse Appendix A. No computed candidate set is returned until
the player submits a supported conclusion.
"""
from .engine import SUSPECTS, ACCESS_RELATION, DEVICE_RELATION, analyze

DOCUMENTS = [
    {"id": "access-register", "title": "File access register", "folder": "Research archive", "clue": "E1"},
    {"id": "authentication-log", "title": "Authentication log", "folder": "System records", "clue": "E2"},
    {"id": "workstation-record", "title": "Workstation activity", "folder": "System records", "clue": "E3"},
    {"id": "location-verification", "title": "Location verification", "folder": "Campus records", "clue": "E4"},
    {"id": "account-directory", "title": "Account directory", "folder": "Administration", "clue": "E5"},
    {"id": "training-register", "title": "Laboratory training register", "folder": "Administration", "clue": "E6"},
]
BY_ID = {document["id"]: document for document in DOCUMENTS}
CORE_DOCUMENTS = {document["id"] for document in DOCUMENTS[:4]}


def discovery_case():
    return {
        "id": "CASE-001",
        "title": "The Research Leak",
        "brief": "At approximately 10:25 PM, research.pdf was copied using a local session on Lab-PC2. Establish which account is compatible with the verified records and explain your conclusion.",
        "scope": "This controlled case investigates direct physical use of Lab-PC2. Remote access is outside the case assumptions. The incident login window is 10:00–10:30 PM.",
        "suspects": [{"id": code, "name": person["name"], "role": person["role"]} for code, person in SUSPECTS.items()],
        "documents": [{key: document[key] for key in ("id", "title", "folder")} for document in DOCUMENTS],
    }


def source_document(document_id):
    if document_id not in BY_ID:
        raise ValueError("Unknown source document")
    document = BY_ID[document_id]
    rows = []
    for code, person in SUSPECTS.items():
        if document_id == "access-register":
            values = [code, person["name"], "Allowed" if (code, "research.pdf") in ACCESS_RELATION else "Not authorized", "Allowed" if (code, "draft.txt") in ACCESS_RELATION else "Not authorized"]
        elif document_id == "authentication-log":
            values = [code, person["name"], person["last_login"] or "No verified event"]
        elif document_id == "workstation-record":
            values = [code, person["name"], "Lab-PC2 activity recorded" if (code, "Lab-PC2") in DEVICE_RELATION else "No matching Lab-PC2 event in this case"]
        elif document_id == "location-verification":
            values = [code, person["name"], "No verified alibi recorded" if person["N"] else "Verified physical alibi: elsewhere"]
        elif document_id == "account-directory":
            values = [code, person["name"], person["role"], "Active" if person["active"] else "Inactive"]
        else:
            values = [code, person["name"], "Completed" if person["training"] else "Not completed"]
        rows.append({"account": code, "values": values})
    columns, description = {
        "access-register": (["Account", "Name", "research.pdf", "draft.txt"], "Recorded user-to-file permissions. A permission record describes access rights, not proof that a file was opened or copied."),
        "authentication-log": (["Account", "Name", "Last verified login"], "Verified synthetic authentication records. Missing data is labeled explicitly; no login time has been invented."),
        "workstation-record": (["Account", "Name", "Device record"], "Account associations with Lab-PC2 activity in this controlled case. These records do not identify the individual operating the computer."),
        "location-verification": (["Account", "Name", "Verified location evidence"], "Physical-location verification for the incident. An unrecorded alibi is not proof that an alibi does not exist."),
        "account-directory": (["Account", "Name", "System role", "Account state"], "The identities and account states included in this synthetic investigation."),
        "training-register": (["Account", "Name", "Laboratory access training"], "Laboratory access-training records included in the case repository."),
    }[document_id]
    return {"id": document_id, "title": document["title"], "folder": document["folder"], "source": "Synthetic case repository · Research Appendix A", "description": description, "columns": columns, "rows": rows}


def check_conclusion(candidate, documents, reasoning):
    if candidate not in SUSPECTS:
        raise ValueError("Select an account from this case")
    if len(documents) != len(set(documents)) or any(document not in BY_ID for document in documents):
        raise ValueError("Citations must be unique source documents from this case")
    if len(reasoning.strip()) < 40:
        return {"accepted": False, "status": "insufficient", "message": "Add your reasoning before submitting: explain how your cited records support your conclusion."}
    selected_clues = [document["clue"] for document in DOCUMENTS if document["id"] in documents]
    result = analyze(selected_clues)
    supported = CORE_DOCUMENTS.issubset(documents) and result["candidates"] == [candidate]
    if not supported:
        # The category is useful but does not reveal the correct identity or hidden candidate set.
        status = 'insufficient' if not CORE_DOCUMENTS.issubset(documents) else 'inconsistent'
        message = ('Insufficient Evidence: not all mandatory records have been cited. Continue investigating.'
                   if status == 'insufficient' else
                   'Inconsistent Investigation: your selected account conflicts with the cited mandatory records. Recheck your evidence.')
        return {"accepted": False, "status": status, "message": message}
    return {"accepted": True, "status": "supported", "message": "Supported Conclusion: your account selection is compatible with the cited synthetic records under the direct-use assumption. This does not establish guilt.", "review": result}
