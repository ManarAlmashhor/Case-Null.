"""Evidence-backed relationships for the interactive corkboard.

The API checks links against the canonical *fictional* records. It never returns a
final candidate or an accusation. Unknown evidence is not treated as false.
"""
from .discovery import BY_ID
from .engine import SUSPECTS, ACCESS_RELATION, DEVICE_RELATION


def validate_connection(account: str, document_id: str, discovered: list[str]) -> dict:
    if account not in SUSPECTS or document_id not in BY_ID:
        raise ValueError("Unrecognized suspect or case record")
    if document_id not in discovered:
        raise ValueError("Discover the source record before linking it")
    person = SUSPECTS[account]
    name = person['name']
    if document_id == 'access-register':
        is_supported = (account, 'research.pdf') in ACCESS_RELATION
        return dict(status='supported' if is_supported else 'unsupported',
                    message=f"{name}'s account is listed for research.pdf." if is_supported else "The permissions register does not support that access claim.",
                    relation='R_access', pair=[account, 'research.pdf'])
    if document_id == 'workstation-record':
        is_supported = (account, 'Lab-PC2') in DEVICE_RELATION
        return dict(status='supported' if is_supported else 'unsupported',
                    message='The workstation record supports an account–device association.' if is_supported else 'No matching Lab-PC2 event is verified for that account.',
                    relation='R_device', pair=[account, 'Lab-PC2'])
    if document_id == 'authentication-log':
        is_supported = person['last_login'] is not None
        return dict(status='supported' if is_supported else 'unknown',
                    message='A login event exists for this account. Check its time before treating it as incident-window evidence.' if is_supported else 'No verified login appears for this account; this is unknown, not proof of absence.',
                    relation='R_login', pair=[account, person['last_login'] or 'Unknown'])
    if document_id == 'location-verification':
        if account == 'S':
            return dict(status='supported',message='The fictional campus record verifies an alibi for Sara; compare its time and source.',relation='R_location',pair=[account,'Verified elsewhere'])
        return dict(status='unknown',message='No verified alibi is recorded for this account. Absence of a record is not proof of presence.',relation='R_location',pair=[account,'Unknown'])
    if document_id in ('account-directory', 'training-register'):
        return dict(status='supported',message='The source contains an account entry. Check the recorded value before drawing conclusions.',relation='R_record',pair=[account, document_id])
    raise ValueError('Unrecognized evidence record')
