# Discord Integration Architecture Notes & Roadmap

## Context & Limitations (Why Option B was chosen first)
1. **User Token ("Self-botting") Restrictions**:
   - Discord Terms of Service explicitly forbid automating user accounts with user tokens.
   - User OAuth2 (`https://discord.com/oauth2/authorize`) does **not** provide any permission scope to read messages or search server channel history.
2. **Bot Permissions**:
   - Discord bots can only read servers where they have been explicitly invited by an administrator.
   - Discord's native search API (`/guilds/{id}/messages/search`) is restricted to user clients and returns `403 Forbidden` for Bot tokens.

---

## Current Solution: Option B (Community Directory & Intelligent Router)
- Module: `app/discord_service.py`
- Tool: `find_discord_resources(topic_or_issue)`
- Maps real-world VESC issues, hardware models, and tuning inquiries to:
  - **Float with VESC** (`https://discord.gg/Kwsgzte2`)
  - **VESC Development** (`https://discord.gg/tq6tav6MQ`)
  - **Vescify** (`https://discord.gg/ahJXqXVVz`)
  - **Funwheel** (`https://discord.gg/ydvbEvafa`)
  - **JetFleet** (`https://discord.gg/ztuacpdhE`)
  - **Floatwheel** (`https://discord.gg/KjKzYvFP5`)
  - **FixMyPEV** (`https://discord.gg/KjKzYvFP5`)
- Recommends exact channels (e.g. `#adv-troubleshooting`, `#xr-conversion`, `#battery-repair`) and pinned topics.

---

## Future Roadmap: Architecture A (Ingestion & Semantic Mirroring)
If we want the agent to perform full-text search across live Discord messages in the future without violating Discord TOS:

1. **Ingest Bot Deployment**:
   - Deploy an official Discord bot using `discord.py` or `hikari` to a Cloud Run worker or GKE pod.
   - Authorize the bot in cooperative servers where admins grant `Read Message History` on specific public channels (`#announcements`, `#troubleshooting-pins`, `#firmware-releases`).
2. **Persistence & Vector Storage**:
   - **Firestore Collection**: Store messages under `discord_knowledge_archive` with metadata:
     - `guild_id`, `channel_name`, `author`, `timestamp`, `content`, `attachments`.
   - **Vertex AI RAG Engine**: Connect the archive to a Vertex AI Search / RAG Engine corpus for semantic vector similarity search.
3. **Agent Tool**:
   - Expose a tool `search_discord_archive(query)` that queries the Firestore collection or Vertex RAG corpus directly with zero rate limits or auth friction.
