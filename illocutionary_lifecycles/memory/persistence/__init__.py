"""The folder that stores a conversation's record beyond the running process, with one interface and four storage
vendors that replace each other, chosen per session by registered name.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and its record is kept in memory while it runs, so this folder, inside
``memory``, is where it is written to disk or to a database and read back to reopen a finished conversation. Of the
package's four folders, ``core`` selects a vendor when it starts a session, from the provider's ``memory_vendor`` and
``vendor_session_address``, and ``analyzers`` and ``server`` never reach a vendor.

The module ``PersistentSaveLoadBase`` holds the interface and ``build_persistent_connection``, which builds the vendor
a session names. The module ``LocalConversationSaveLoad`` holds the vendor registered as "local", one JSON file per
event under a directory. The module ``CosmosSaveLoad`` holds the vendor registered as "cosmos", one document per event
in an Azure Cosmos DB container. The module ``ReadOnlySaveLoad`` holds "local-readonly" and "cosmos-readonly", the same
two with every write refused, for reading a finished conversation. Importing this folder imports every vendor, which
registers it, and the vendors, ``build_persistent_connection`` and ``ReadOnlyStoreError`` are re-exported here.
"""
from illocutionary_lifecycles.memory.persistence.PersistentSaveLoadBase import (
    PersistentSaveLoadBase,
    build_persistent_connection,
)
from illocutionary_lifecycles.memory.persistence.LocalConversationSaveLoad import LocalConversationSaveLoad
from illocutionary_lifecycles.memory.persistence.CosmosSaveLoad import CosmosSaveLoad
from illocutionary_lifecycles.memory.persistence.ReadOnlySaveLoad import (
    CosmosSaveLoadReadOnly,
    LocalConversationSaveLoadReadOnly,
    ReadOnlyStoreError,
)

__all__ = [
    "PersistentSaveLoadBase",
    "build_persistent_connection",
    "LocalConversationSaveLoad",
    "CosmosSaveLoad",
    "LocalConversationSaveLoadReadOnly",
    "CosmosSaveLoadReadOnly",
    "ReadOnlyStoreError",
]
