# Core game systems & patterns

## Data persistence

`DataStoreService` is the backend for saving player data across sessions. Core
calls: `GetDataStore`, `GetAsync` (read; 4-second local cache), `SetAsync`
(overwrite — fast, write-limit only, but risks inconsistency across servers),
`UpdateAsync` (atomic read-modify-write via a non-yielding callback — safe for
multi-server), `IncrementAsync`, `RemoveAsync`.
[data-stores](https://create.roblox.com/docs/cloud-services/data-stores)

Limits: value ≤**4 MiB** (4,194,304 chars); key/scope/name ≤50 chars. Per-server
budgets scale with players (read/write ≈ `60 + players×40` /min). Throughput per
key: read 25 MB/min, write 4 MB/min. Check `GetRequestBudgetForRequestType`
before bursting. [limits](https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits)

### The session-locking problem (do not skip)

If one player's data is loaded on two servers, the older server can overwrite the
newer save → **data loss and item dupes**. Roblox's own guide warns about exactly
this and recommends writing a lock into the key's metadata inside the same
`UpdateAsync`. [player-data](https://create.roblox.com/docs/cloud-services/data-stores/player-data-purchasing)

Also always `BindToClose` to save on shutdown — the server waits **30 seconds**
for bound functions before terminating.

### Use ProfileStore for player data

[ProfileStore](https://github.com/MadStudioRoblox/ProfileStore) (by loleris, the
successor to ProfileService) is a DataStore wrapper that handles **auto-saving,
session locking, and final saves** for you — eliminating the dupe/data-loss
class. Use it for new projects; keep ProfileService on legacy ones. It is **not**
for leaderboards/global state — use `OrderedDataStore` (`GetSortedAsync`, integer
values) for those.

```lua
local ProfileStore = require(game.ServerScriptService.ProfileStore)
local TEMPLATE = { Cash = 0, Items = {} }
local Players = game:GetService("Players")
local Store = ProfileStore.New("PlayerStore", TEMPLATE)
local Profiles = {}

local function onAdded(player)
    local profile = Store:StartSessionAsync(`{player.UserId}`, {
        Cancel = function() return player.Parent ~= Players end,
    })
    if not profile then player:Kick("Profile load fail") return end
    profile:AddUserId(player.UserId)
    profile:Reconcile()
    profile.OnSessionEnd:Connect(function()
        Profiles[player] = nil
        player:Kick("Profile session ended - rejoin")
    end)
    if player.Parent == Players then
        Profiles[player] = profile
    else
        profile:EndSession()
    end
end

for _, p in Players:GetPlayers() do task.spawn(onAdded, p) end
Players.PlayerAdded:Connect(onAdded)
Players.PlayerRemoving:Connect(function(p)
    local profile = Profiles[p]
    if profile then profile:EndSession() end
end)
```

## leaderstats

A `Folder` named `leaderstats` parented to the `Player`, holding `IntValue`/
`StringValue` children, renders Roblox's built-in leaderboard. Drive its values
from server-owned state (e.g. the profile) — never let the client write them.

## Economy (currencies, sources, sinks)

Keep all currency on the server (profile data + a leaderstats mirror). Design
explicit **sources** (gameplay rewards, dailies) and **sinks** (upgrades,
cosmetics) so the economy doesn't inflate. Validate every spend server-side
against the player's real balance — never trust a client-sent price or amount.

## Round systems

The canonical loop is intermission → round → end → repeat, run server-side in its
own thread with a yield each iteration so it never runs unthrottled. Track a
phase state (`Waiting`/`Intermission`/`InProgress`/`Ending`).
[round tutorial](https://devforum.roblox.com/t/how-to-make-a-round-based-system/487712)

```lua
task.spawn(function()
    while true do
        setPhase("Intermission"); countdown(15)   -- countdown() calls task.wait(1)
        setPhase("InProgress");   countdown(60)
        setPhase("Ending");       task.wait(3)
    end
end)
```

## Anti-exploit (server authority)

> "Assume every piece of data sent from the client has been manipulated."
> [security-tactics](https://create.roblox.com/docs/scripting/security/security-tactics)

Exploiters fully control their client and can fire remotes at any rate with any
arguments. Rules:

1. **Validate every remote argument** — type, range, whitelist. The `Player`
   first arg is engine-set and trustworthy; everything else is not.
2. **Server is authority** — does the player actually *own* the item/currency?
   Compute outcomes server-side; mutate state only on the server.
3. **Rate-limit** per player; **silently drop** abuse (don't error back).
4. **Sanity-check movement** server-side; rubber-band speed/teleport hacks.
5. Keep logic and secrets in `ServerScriptService`, never in `ReplicatedStorage`
   or `Workspace`.

```lua
local last = {}                              -- per-player throttle
local MIN = 0.5
remote.OnServerEvent:Connect(function(player, itemName)
    local now = os.clock()
    if last[player] and now - last[player] < MIN then return end
    last[player] = now
    if type(itemName) ~= "string" then return end      -- validate
    local item = SHOP[itemName]; if not item then return end  -- whitelist
    if getBalance(player) < item.price then return end        -- authority
    setBalance(player, getBalance(player) - item.price)       -- server-only mutate
end)
game:GetService("Players").PlayerRemoving:Connect(function(p) last[p] = nil end)
```

## Retention hooks (build these in)

Daily login streaks, timed rewards, quests, limited-time events, and
play-with-friends bonuses directly feed the discovery signals in `06`. Bake them
into the design, not as an afterthought.
