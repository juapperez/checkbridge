# CheckBridge — local application prototype

CheckBridge exposes three fixed numerical examples through an experimental MCP stdio adapter. It lets an agent submit a number and receive the reference derivation, assumptions, units and individual check outcomes. It never executes supplied code or accesses files, networks, wallets or AI services.

This is an AI-assisted prototype prepared on 6 November 2026. The numerical core derives from the new MIT Independent Checks application prototype; it does not copy or relicense any existing commercial application. Specifications and tests are also AI-assisted. No independent domain review, security audit, production readiness, goose integration or real-model evaluation has been completed.

Run with Python 3.9+ and no dependencies:

```sh
python3 -m unittest -v
python3 server.py
```

The server uses newline-delimited JSON-RPC over stdin/stdout. Initialize with protocol version `2025-11-25`, send `notifications/initialized`, then use `tools/list` and `tools/call`. The sole tool is `verify_case`, with `case_id` and a finite `candidate_output`. The three case IDs are `concentration_units`, `steady_mixer` and `first_order_decay`. The existing numerical core's CLI remains available through `python3 checks.py`.

The adapter returns a failed scientific check as a normal tool result; invalid arguments produce a tool error. It does not declare an answer correct beyond the fixed case and stated assumptions. An unweighted mixer answer of 0.125 lies within the inlet bounds but fails the solute balance; 0.11 passes this example. The reference assumptions themselves still need independent review.

The protocol implementation is intentionally small and experimental, not a general MCP SDK. Transport tests exercise a subprocess, negotiation, initialization sequencing, discovery, valid and defective scientific results, malformed input and invalid values. Compatibility with an actual goose release and maintained MCP client SDK is proposed funded work, not a completed result.

Proposal scope: reviewable numerical results for local open AI agents, versioned case records and bilingual human-readable explanations. Related Independent Checks funding requests are alternatives; overlapping costs must not be billed twice.

New code: MIT (LICENSE). New written materials and illustrative results: CC BY 4.0. Attribution: Juan Pablo Pérez Vélez, 2026.

Protocol references: https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle ; https://modelcontextprotocol.io/specification/2025-11-25/server/tools ; https://modelcontextprotocol.io/specification/2025-11-25/basic/transports .
